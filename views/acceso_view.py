import flet as ft
import threading
import time
from controllers.data_controller import DataController

# Claves internas y etiquetas para cada barrera
BARRERAS_CONFIG = [
    {"id": "entrada-norte", "label": "Entrada Norte", "seccion": "Norte"},
    {"id": "salida-norte",  "label": "Salida Norte",  "seccion": "Norte"},
    {"id": "entrada-sur",   "label": "Entrada Sur",   "seccion": "Sur"},
    {"id": "salida-sur",    "label": "Salida Sur",    "seccion": "Sur"},
]

# Posiciones de los botones del mapa (1159 x 376 px)
MAPA_POSICIONES = {
    "entrada-norte": {"left": 860, "top": 15},
    "salida-norte":  {"left": 730, "top": 15},
    "entrada-sur":   {"left": 860, "top": 295},
    "salida-sur":    {"left": 730, "top": 295},
}


class AccesoView(ft.Container):
    def __init__(self, page):
        super().__init__(expand=True)
        self.page = page
        self.activo = True

        # Construir widgets por barrera
        self._sw_manual   = {}  # barrera_id -> Switch modo manual
        self._sw_abrir    = {}  # barrera_id -> Switch abrir
        self._cont_status = {}  # barrera_id -> Container icono
        self._lbl_status  = {}  # barrera_id -> Text estado
        self._btn_mapa    = {}  # barrera_id -> Container boton mapa

        # Historial
        self.columna_historial = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        self.lbl_contador_historial = ft.Text("", size=12, color="grey600", italic=True)

        # ── Inicializar widgets por barrera ────────────────────
        for cfg in BARRERAS_CONFIG:
            bid = cfg["id"]
            estado_manual = DataController.obtener_manual_barrera(bid)

            sw_manual = ft.Switch(
                label="Activar Control Manual",
                value=estado_manual.get("modo_manual", False),
                active_color="blue",
            )
            sw_abrir = ft.Switch(
                label="Mantener Barrera Abierta",
                value=estado_manual.get("abrir", False),
                disabled=not sw_manual.value,
                active_color="green",
            )

            def make_handler(barrera_id, sw_m, sw_a):
                def handler(e):
                    sw_a.disabled = not sw_m.value
                    if not sw_m.value:
                        sw_a.value = False
                    DataController.guardar_manual_barrera(barrera_id, sw_m.value, sw_a.value)
                    self.page.update()
                return handler

            handler = make_handler(bid, sw_manual, sw_abrir)
            sw_manual.on_change = handler
            sw_abrir.on_change  = handler

            self._sw_manual[bid]   = sw_manual
            self._sw_abrir[bid]    = sw_abrir
            self._cont_status[bid] = ft.Container(
                content=ft.Image(src="icon_acceso_off.png", width=50, height=50),
                bgcolor="red300", padding=10, border_radius=5,
                alignment=ft.alignment.center,
            )
            self._lbl_status[bid] = ft.Text("Barrera Cerrada", weight="bold", color="red600")

        # ── Botones del mapa ───────────────────────────────────
        def toggle_access(e):
            bid = e.control.data
            estados = DataController.obtener_estado_barreras()
            abierta_actual = estados.get(bid, {}).get("barrera_abierta", False)
            nueva = not abierta_actual
            DataController.guardar_manual_barrera(bid, True, nueva)
            self._sw_manual[bid].value = True
            self._sw_abrir[bid].value  = nueva
            self._sw_abrir[bid].disabled = False
            actualizar_datos()

        for cfg in BARRERAS_CONFIG:
            bid = cfg["id"]
            pos = MAPA_POSICIONES[bid]
            btn = ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Image(src="icon_acceso_off.png", width=30, height=30),
                        shape=ft.BoxShape.CIRCLE,
                        bgcolor="red300",
                        border=ft.border.all(3, "white"),
                        shadow=ft.BoxShadow(blur_radius=10, color="black45"),
                        width=55, height=55,
                        alignment=ft.alignment.center,
                    ),
                    ft.Container(
                        content=ft.Text(cfg["label"], size=11, weight="bold", color="white"),
                        bgcolor="black",
                        padding=ft.padding.symmetric(vertical=2, horizontal=8),
                        border_radius=5,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                left=pos["left"],
                top=pos["top"],
                on_click=toggle_access,
                data=bid,
            )
            btn.mouse_cursor = ft.MouseCursor.CLICK
            self._btn_mapa[bid] = btn

        # ── Lógica de refresco ─────────────────────────────────
        def actualizar_datos():
            try:
                estados  = DataController.obtener_estado_barreras()
                manuales = DataController.obtener_manual_barreras()

                for cfg in BARRERAS_CONFIG:
                    bid = cfg["id"]
                    manual = manuales.get(bid, {})
                    modo_manual = manual.get("modo_manual", False)
                    abrir       = manual.get("abrir", False)

                    # Sincronizar switches
                    if self._sw_manual[bid].value != modo_manual:
                        self._sw_manual[bid].value = modo_manual
                    if self._sw_abrir[bid].value != abrir:
                        self._sw_abrir[bid].value = abrir
                    self._sw_abrir[bid].disabled = not modo_manual

                    # Estado de la barrera
                    estado   = estados.get(bid, {})
                    mensaje = estado.get("mensaje", "BARRERA CERRADA")
                    abierta = abrir if modo_manual else estado.get("barrera_abierta", False)

                    if abierta:
                        self._cont_status[bid].bgcolor = "green"
                        if isinstance(self._cont_status[bid].content, ft.Image):
                            self._cont_status[bid].content.src = "icon_acceso_on.png"
                        self._lbl_status[bid].value = "BARRERA ABIERTA" if modo_manual else mensaje
                        self._lbl_status[bid].color = "green"
                    else:
                        self._cont_status[bid].bgcolor = "red300"
                        if isinstance(self._cont_status[bid].content, ft.Image):
                            self._cont_status[bid].content.src = "icon_acceso_off.png"
                        self._lbl_status[bid].value = "BARRERA CERRADA" if modo_manual else mensaje
                        self._lbl_status[bid].color = "red600"

                    # Botón del mapa
                    circulo = self._btn_mapa[bid].content.controls[0]
                    if abierta:
                        circulo.bgcolor = "green"
                        circulo.content.src = "icon_acceso_on.png"
                    else:
                        circulo.bgcolor = "red300"
                        circulo.content.src = "icon_acceso_off.png"

                # Historial
                logs = DataController.obtener_historial_accesos()
                self.columna_historial.controls.clear()
                total = len(logs) if logs else 0
                self.lbl_contador_historial.value = f"Total: {total} registros"

                if not logs:
                    self.columna_historial.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Icon(ft.Icons.HISTORY, size=60, color="grey400"),
                                ft.Text("Sin registros de acceso", size=16, color="grey600", italic=True),
                            ], horizontal_alignment="center", spacing=10),
                            alignment=ft.alignment.center,
                            padding=40,
                        )
                    )
                else:
                    for log in logs:
                        tipo_acceso = log.get("tipo", "Acceso")
                        barrera_log = log.get("barrera", "").upper()

                        if "Manual" in tipo_acceso:
                            icon, color_icono, bgcolor_card, color_barrera = (
                                ft.Icons.ADMIN_PANEL_SETTINGS, "blue600", "#e3f2fd", "blue700")
                        elif "Emergencia" in tipo_acceso or "Viento" in tipo_acceso:
                            icon, color_icono, bgcolor_card, color_barrera = (
                                ft.Icons.WARNING, "red600", "#ffebee", "red700")
                        else:
                            icon, color_icono, bgcolor_card, color_barrera = (
                                ft.Icons.DIRECTIONS_CAR, "green600", "#e8f5e9", "green700")

                        hora_display = log.get("hora", "")
                        try:
                            if " " in hora_display:
                                hora_display = hora_display.split(" ")[1]
                        except:
                            pass

                        card = ft.Container(
                            content=ft.Row([
                                ft.Container(
                                    content=ft.Icon(icon, color=color_icono, size=32),
                                    bgcolor="white", padding=12, border_radius=8,
                                    width=56, height=56, alignment=ft.alignment.center,
                                ),
                                ft.Column([
                                    ft.Row([
                                        ft.Text(tipo_acceso, size=16, weight="bold", color="grey900"),
                                        ft.Container(expand=True),
                                        ft.Container(
                                            content=ft.Text(barrera_log or "N/A", size=12, weight="bold", color="white"),
                                            bgcolor=color_barrera,
                                            padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                            border_radius=12,
                                        ),
                                    ], spacing=10),
                                    ft.Row([
                                        ft.Icon(ft.Icons.ACCESS_TIME, size=16, color="grey600"),
                                        ft.Text(hora_display, size=14, color="grey700"),
                                    ], spacing=5),
                                    ft.Row([
                                        ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=16, color="green600"),
                                        ft.Text(log.get("evento", "Acceso Permitido"), size=13, color="grey600"),
                                    ], spacing=5),
                                ], spacing=4, expand=True, tight=True),
                            ], spacing=15, vertical_alignment="center"),
                            bgcolor=bgcolor_card, padding=15, border_radius=10,
                            border=ft.border.all(1, color="grey300"),
                            shadow=ft.BoxShadow(blur_radius=2, color="grey300", spread_radius=0),
                        )
                        self.columna_historial.controls.append(card)

                self.page.update()
            except Exception as e:
                print(f"Error UI acceso: {e}")

        def ciclo_refresco():
            while True:
                time.sleep(0.5)
                if not getattr(self, 'activo', True):
                    break
                if self.page:
                    actualizar_datos()

        actualizar_datos()
        threading.Thread(target=ciclo_refresco, daemon=True).start()

        # ── Construir paneles ──────────────────────────────────
        def _panel_barrera(cfg):
            bid = cfg["id"]
            return ft.Container(
                content=ft.Column([
                    ft.Text(cfg["label"], size=18, weight="bold"),
                    ft.Divider(),
                    ft.Container(
                        content=ft.Column([
                            self._cont_status[bid],
                            self._lbl_status[bid],
                        ], horizontal_alignment="center", spacing=10),
                        alignment=ft.alignment.center,
                        expand=True,
                    ),
                    ft.Divider(),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Panel de Operador", weight="bold", size=14),
                            self._sw_manual[bid],
                            self._sw_abrir[bid],
                            ft.Text("(Activa ambos para abrir)", size=11, italic=True, color="grey"),
                        ], spacing=8),
                        bgcolor="#f0f2f5", padding=15, border_radius=10,
                    ),
                ], horizontal_alignment="center", spacing=10),
                bgcolor="white", padding=20, border_radius=10,
                expand=1, alignment=ft.alignment.top_center,
            )

        # Fila Norte (Entrada + Salida)
        fila_norte = ft.Row(
            controls=[_panel_barrera(BARRERAS_CONFIG[0]), _panel_barrera(BARRERAS_CONFIG[1])],
            spacing=20, expand=False,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
        # Fila Sur (Entrada + Salida)
        fila_sur = ft.Row(
            controls=[_panel_barrera(BARRERAS_CONFIG[2]), _panel_barrera(BARRERAS_CONFIG[3])],
            spacing=20, expand=False,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        # Cabeceras de sección
        def _seccion_header(titulo):
            return ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.DIRECTIONS_CAR, color="blueGrey700"),
                    ft.Text(titulo, size=18, weight="bold", color="blueGrey800"),
                ], spacing=8),
                bgcolor="#f5f5f5", padding=ft.padding.symmetric(horizontal=20, vertical=10),
                border_radius=8,
            )

        # Mapa
        ANCHO_MAPA, ALTO_MAPA = 1159, 376
        mapa_stack = ft.Stack(
            controls=[
                ft.Image(src="mapa_iluminacion_off.jpg", width=ANCHO_MAPA, height=ALTO_MAPA,
                         fit=ft.ImageFit.CONTAIN),
                *[self._btn_mapa[b["id"]] for b in BARRERAS_CONFIG],
            ],
            width=ANCHO_MAPA, height=ALTO_MAPA,
        )
        panel_mapa = ft.Container(
            content=ft.Row([mapa_stack], scroll=ft.ScrollMode.ADAPTIVE),
            expand=True, border_radius=10, bgcolor="#ffffff", padding=10,
        )

        # Historial
        panel_historial = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.HISTORY, size=28, color="blueGrey700"),
                    ft.Text("Historial de Accesos de Vehículos", size=22, weight="bold"),
                    ft.Container(expand=True),
                    ft.Container(content=self.lbl_contador_historial, padding=ft.padding.only(right=10)),
                ], alignment="center", spacing=10),
                ft.Divider(height=1),
                ft.Container(content=self.columna_historial, expand=True, padding=ft.padding.only(top=10)),
            ], spacing=10, expand=True),
            bgcolor="white", padding=25, border_radius=10,
            expand=True, width=float("inf"),
            shadow=ft.BoxShadow(blur_radius=5, color="#1A000000"),
        )

        self.content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Text("Control de Accesos Inteligente", size=24, weight="bold"),
                        bgcolor="#ffffff", padding=20, border_radius=10, expand=True,
                    ),
                ]),
                ft.Row([panel_mapa]),
                _seccion_header("Acceso Norte — Entrada y Salida"),
                fila_norte,
                _seccion_header("Acceso Sur — Entrada y Salida"),
                fila_sur,
                ft.Row([panel_historial], expand=True, width=float("inf")),
            ], scroll=ft.ScrollMode.ADAPTIVE, spacing=20),
            padding=20,
        )

    def matar_hilos(self):
        self.activo = False
