import flet as ft
import threading
import time
from controllers.data_controller import DataController

class DashboardView(ft.Container):
    def __init__(self, page):
        super().__init__(expand=True, padding=20)
        self.page = page

        # Elementos de la UI (Tarjetas de Resumen)
        self.card_iluminacion = self._build_info_card("Iluminación", ft.Icons.LIGHTBULB, "Cargando...", "grey")
        self.card_ambiental = self._build_info_card("Temperatura", ft.Icons.THERMOSTAT, "-- °C", "blue")
        self.card_acceso = self._build_info_card("Acceso", ft.Icons.GARAGE, "Estado: --", "grey")
        self.card_recursos = self._build_info_card("Agua", ft.Icons.WATER_DROP, "-- L/min", "blue")
        self.card_emergencia = self._build_info_card("Alertas", ft.Icons.WARNING, "Sistema OK", "green")

        # Contenedor principal
        self.content = ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Text("Panel de Control General", size=24, weight="bold"),
                ]),
                bgcolor="white",
                padding=20,
                border_radius=10,
                width=float("inf"), 
                shadow=ft.BoxShadow(blur_radius=5, color="#1A000000")
            ),
            ft.Container(height=10),
            
            # Grid de Tarjetas de Información
            ft.ResponsiveRow([
                ft.Column([self.card_iluminacion], col={"sm": 6, "md": 4}),
                ft.Column([self.card_ambiental], col={"sm": 6, "md": 4}),
                ft.Column([self.card_acceso], col={"sm": 6, "md": 4}),
                ft.Column([self.card_recursos], col={"sm": 6, "md": 4}),
                ft.Column([self.card_emergencia], col={"sm": 12, "md": 8}),
            ], spacing=20)
        ], scroll=ft.ScrollMode.AUTO)

        # Iniciar hilo de actualización
        threading.Thread(target=self._update_loop, daemon=True).start()

    def _build_info_card(self, title, icon, value, color):
        """Constructor de tarjetas informativas."""
        lbl_value = ft.Text(value, size=20, weight="bold", color=color)
        icon_control = ft.Icon(icon, size=40, color=color)
        
        card = ft.Container(
            content=ft.Column([
                ft.Row([
                    icon_control,
                    ft.Text(title, size=16, color="grey")
                ], alignment="spaceBetween"),
                ft.Container(height=10),
                lbl_value
            ]),
            bgcolor="white",
            padding=20,
            border_radius=10,
            shadow=ft.BoxShadow(blur_radius=5, color="#1A000000") 
        )
        
        card.lbl_value = lbl_value
        card.icon_control = icon_control
        return card

    def _update_ui(self):
        try:
            # 1. ILUMINACIÓN
            luz_estado = DataController.obtener_estado_luz()
            lux = DataController.obtener_luminosidad()
            if luz_estado == "on":
                self.card_iluminacion.lbl_value.value = f"ENCENDIDO ({int(lux)}%)"
                self.card_iluminacion.lbl_value.color = "orange"
                self.card_iluminacion.icon_control.color = "orange"
            else:
                self.card_iluminacion.lbl_value.value = f"APAGADO ({int(lux)}%)"
                self.card_iluminacion.lbl_value.color = "grey"
                self.card_iluminacion.icon_control.color = "grey"

            # 2. AMBIENTAL
            datos_env = DataController.obtener_datos_ambientales()
            if datos_env["temp"] and len(datos_env["temp"]) > 0:
                temp_val = datos_env["temp"][-1]["value"]
                self.card_ambiental.lbl_value.value = f"{temp_val} °C"
            
            # 3. ACCESO
            datos_acceso = DataController.obtener_estado_barrera()
            abierta = datos_acceso.get("barrera_abierta", False)
            if abierta:
                self.card_acceso.lbl_value.value = "BARRERA ABIERTA"
                self.card_acceso.lbl_value.color = "green"
                self.card_acceso.icon_control.name = ft.Icons.NO_MEETING_ROOM
                self.card_acceso.icon_control.color = "green"
            else:
                self.card_acceso.lbl_value.value = "BARRERA CERRADA"
                self.card_acceso.lbl_value.color = "red"
                self.card_acceso.icon_control.name = ft.Icons.GARAGE
                self.card_acceso.icon_control.color = "red"

            # 4. RECURSOS
            datos_agua = DataController.obtener_datos_agua()
            if datos_agua and len(datos_agua) > 0:
                flujo = datos_agua[-1]["value"]
                self.card_recursos.lbl_value.value = f"{flujo} L/min"
                if flujo > 45: 
                    self.card_recursos.lbl_value.color = "red"
                    self.card_recursos.icon_control.color = "red"
                else:
                    self.card_recursos.lbl_value.color = "blue"
                    self.card_recursos.icon_control.color = "blue"

            # 5. EMERGENCIAS
            datos_emergencia = DataController.obtener_datos_emergencia()
            
            config = DataController.obtener_config_alertas()
            limite_humo = config.get("humo_max", 25)
            limite_viento = config.get("viento_max", 50)
            
            alerta = False
            msg = "Sistema Normal"
            
            if datos_emergencia["humo"] and datos_emergencia["humo"][-1]["value"] > limite_humo:
                alerta = True
                val = datos_emergencia["humo"][-1]["value"]
                msg = f"¡ALERTA DE HUMO! ({val})"
            elif datos_emergencia["viento"] and datos_emergencia["viento"][-1]["value"] > limite_viento:
                alerta = True
                val = datos_emergencia["viento"][-1]["value"]
                msg = f"¡VIENTO FUERTE! ({val} km/h)"

            if alerta:
                self.card_emergencia.lbl_value.value = msg
                self.card_emergencia.lbl_value.color = "red"
                self.card_emergencia.icon_control.color = "red"
                self.card_emergencia.icon_control.name = ft.Icons.WARNING
            else:
                self.card_emergencia.lbl_value.value = "Sin incidencias activas"
                self.card_emergencia.lbl_value.color = "green"
                self.card_emergencia.icon_control.color = "green"
                self.card_emergencia.icon_control.name = ft.Icons.CHECK_CIRCLE

            self.page.update()
        except Exception as e:
            print(f"Error Dashboard: {e}")

    def _update_loop(self):
        while True:
            if self.page:
                self._update_ui()
            time.sleep(2)