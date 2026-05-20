import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from config import BRIDGE_HOST, BRIDGE_PORT, ESP32_API_KEY
from database import (
    add_sensor_data,
    get_access_state,
    get_alert_config,
    get_light_state,
    get_schedule,
)

LAST_TELEMETRY_TS = 0.0
LAST_TELEMETRY_DEVICE = None


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict):
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _is_authorized(handler: BaseHTTPRequestHandler) -> bool:
    if not ESP32_API_KEY:
        return True
    return handler.headers.get("X-API-Key", "") == ESP32_API_KEY


def _parse_float(data: dict, key: str):
    value = data.get(key)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _store_telemetry(data: dict):
    global LAST_TELEMETRY_TS, LAST_TELEMETRY_DEVICE

    sensor_map = {
        "temperatura": "Temperatura",
        "humedad": "Humedad",
        "calidad_aire": "Calidad de Aire",
        "humo": "Nivel de Humo",
        "luminosidad": "Luminosidad",
        "distancia_norte": "Distancia - norte",
        "distancia_sur": "Distancia - sur",
        "caudal": "Flujo de Agua",
        "viento": "Velocidad de Viento",
    }

    inserted = 0
    for incoming_key, db_name in sensor_map.items():
        val = _parse_float(data, incoming_key)
        if val is None:
            continue
        add_sensor_data(db_name, val)
        inserted += 1

    LAST_TELEMETRY_TS = time.time()
    LAST_TELEMETRY_DEVICE = str(data.get("device_id", "esp32"))
    return inserted


def _build_command_payload() -> dict:
    light = get_light_state()
    access_north = get_access_state("norte")
    access_south = get_access_state("sur")
    alert_cfg = get_alert_config()
    schedule = get_schedule()

    return {
        "timestamp": int(time.time()),
        "led": light.get("estado", "off") == "on",
        "barrera_norte": bool(access_north.get("barrera_abierta", False)),
        "barrera_sur": bool(access_south.get("barrera_abierta", False)),
        "thresholds": {
            "temp_max": float(alert_cfg.get("temp_max", 35)),
            "hum_min": float(alert_cfg.get("hum_min", 30)),
            "hum_max": float(alert_cfg.get("hum_max", 70)),
            "iaq_max": float(alert_cfg.get("iaq_max", 100)),
            "humo_max": float(alert_cfg.get("humo_max", 25)),
            "viento_max": float(alert_cfg.get("viento_max", 50)),
        },
        "schedule": {
            "hora_inicio": int(schedule.get("hora_inicio", 0) or 0),
            "minuto_inicio": int(schedule.get("minuto_inicio", 0) or 0),
            "hora_fin": int(schedule.get("hora_fin", 0) or 0),
            "minuto_fin": int(schedule.get("minuto_fin", 0) or 0),
        },
    }


class BridgeHandler(BaseHTTPRequestHandler):
    server_version = "SmartBridge/1.0"

    def log_message(self, fmt, *args):
        print(f"[WIFI_BRIDGE] {self.address_string()} - {fmt % args}")

    def do_GET(self):
        if not _is_authorized(self):
            _json_response(self, 401, {"ok": False, "error": "unauthorized"})
            return

        parsed = urlparse(self.path)
        if parsed.path == "/health":
            age = time.time() - LAST_TELEMETRY_TS if LAST_TELEMETRY_TS else None
            _json_response(
                self,
                200,
                {
                    "ok": True,
                    "service": "wifi_bridge",
                    "last_telemetry_age_s": age,
                    "last_device": LAST_TELEMETRY_DEVICE,
                },
            )
            return

        if parsed.path == "/command":
            params = parse_qs(parsed.query)
            device_id = params.get("device_id", ["esp32"])[0]
            payload = _build_command_payload()
            payload["device_id"] = device_id
            _json_response(self, 200, {"ok": True, "command": payload})
            return

        _json_response(self, 404, {"ok": False, "error": "not_found"})

    def do_POST(self):
        if not _is_authorized(self):
            _json_response(self, 401, {"ok": False, "error": "unauthorized"})
            return

        parsed = urlparse(self.path)
        if parsed.path != "/telemetry":
            _json_response(self, 404, {"ok": False, "error": "not_found"})
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            data = json.loads(raw.decode("utf-8"))
            if not isinstance(data, dict):
                raise ValueError("Body must be a JSON object")
        except Exception as exc:
            _json_response(self, 400, {"ok": False, "error": f"invalid_json: {exc}"})
            return

        try:
            inserted = _store_telemetry(data)
            _json_response(self, 200, {"ok": True, "saved_fields": inserted})
        except Exception as exc:
            _json_response(self, 500, {"ok": False, "error": str(exc)})


def main():
    server = ThreadingHTTPServer((BRIDGE_HOST, BRIDGE_PORT), BridgeHandler)
    print(f"[WIFI_BRIDGE] Iniciado en http://{BRIDGE_HOST}:{BRIDGE_PORT}")
    print("[WIFI_BRIDGE] Endpoints: GET /health, POST /telemetry, GET /command")
    server.serve_forever()


if __name__ == "__main__":
    main()
