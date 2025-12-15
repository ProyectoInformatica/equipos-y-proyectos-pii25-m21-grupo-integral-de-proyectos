import flet as ft
import threading
import time
from controllers.data_controller import DataController

class MapView(ft.Container):
    def __init__(self, page):
        super().__init__(expand=True, padding=20)
        self.page = page

        # ICONOS DEL MAPA (Sensores) 
        self.icon_barrera = self._crear_marcador(ft.Icons.GARAGE, "Barrera Principal", 50, 250)
        self.icon_farola = self._crear_marcador(ft.Icons.LIGHTBULB, "Farolas Calle", 200, 100)
        self.icon_humo = self._crear_marcador(ft.Icons.FIRE_EXTINGUISHER, "Sensor Incendio", 350, 150)
        self.icon_agua = self._crear_marcador(ft.Icons.WATER_DROP, "Suministro Agua", 300, 300)
        self.icon_viento = self._crear_marcador(ft.Icons.AIR, "Anemómetro", 500, 50)

        # Contenedor del Mapa
        self.mapa_container = ft.Stack(
            [
                ft.Image(
                    src="mapa_iluminacion_off.jpg",
                    width=600,
                    height=400,
                    fit=ft.ImageFit.FILL,
                    border_radius=10,
                    opacity=0.8
                ),
                self.icon_barrera,
                self.icon_farola,
                self.icon_humo,
                self.icon_agua,
                self.icon_viento
            ],
            width=600,
            height=400,
        )

        self.info_panel = ft.Text("Selecciona un sensor en el mapa...", italic=True)

        self.content = ft.Column([
            ft.Container(
                content=ft.Text("Mapa General de la Zona", size=24, weight="bold"),
                bgcolor="white",
                padding=20,
                border_radius=10,
                width=float("inf"), # Ocupa todo el ancho
                shadow=ft.BoxShadow(blur_radius=5, color="#1A000000")
            ),
            ft.Container(height=10), # Espacio
            
            ft.Row([
                # Columna Izquierda: Mapa
                ft.Container(
                    content=self.mapa_container,
                    border=ft.border.all(2, "#cccccc"),
                    border_radius=10,
                    padding=5,
                    bgcolor="white"
                ),
                # Columna Derecha: Leyenda / Detalles
                ft.Container(
                    content=ft.Column([
                        ft.Text("Estado en Tiempo Real", weight="bold", size=18),
                        ft.Divider(),
                        self.info_panel,
                        ft.Divider(),
                        ft.Row([ft.Icon(ft.Icons.CIRCLE, color="green", size=15), ft.Text("Normal")]),
                        ft.Row([ft.Icon(ft.Icons.CIRCLE, color="orange", size=15), ft.Text("Activo/Aviso")]),
                        ft.Row([ft.Icon(ft.Icons.CIRCLE, color="red", size=15), ft.Text("Alerta/Cerrado")]),
                    ]),
                    padding=20,
                    bgcolor="white",
                    border_radius=10,
                    expand=True, # Para que ocupe el resto del espacio a la derecha
                    shadow=ft.BoxShadow(blur_radius=5, color="#1A000000")
                )
            ], vertical_alignment=ft.CrossAxisAlignment.START, expand=True)
        ], scroll=ft.ScrollMode.AUTO)

        threading.Thread(target=self._update_loop, daemon=True).start()

    def _crear_marcador(self, icon_name, tooltip_text, left, top):
        icon = ft.Icon(icon_name, color="grey", size=30)
        return ft.Container(
            content=ft.Container(
                content=icon,
                bgcolor="white",
                border_radius=50,
                padding=5,
                shadow=ft.BoxShadow(blur_radius=5, color="#1A000000"),
                tooltip=tooltip_text, 
            ),
            left=left,
            top=top,
        )

    def _actualizar_estado_icono(self, container_posicion, color, tooltip_text):
        container_circulo = container_posicion.content
        icon_control = container_circulo.content
        icon_control.color = color
        container_circulo.tooltip = tooltip_text

    def _update_ui(self):
        try:
            # 1. BARRERA
            acc = DataController.obtener_estado_barrera()
            if acc["barrera_abierta"]:
                self._actualizar_estado_icono(self.icon_barrera, "green", "Barrera: ABIERTA")
            else:
                self._actualizar_estado_icono(self.icon_barrera, "red", "Barrera: CERRADA")

            # 2. ILUMINACIÓN
            luz = DataController.obtener_estado_luz()
            if luz == "on":
                self._actualizar_estado_icono(self.icon_farola, "orange", "Farolas: ENCENDIDAS")
            else:
                self._actualizar_estado_icono(self.icon_farola, "grey", "Farolas: APAGADAS")

            # 3. HUMO
            emerg = DataController.obtener_datos_emergencia()
            humo_val = 0
            if emerg["humo"] and len(emerg["humo"]) > 0:
                humo_val = emerg["humo"][-1]["value"]
            
            if humo_val > 25:
                self._actualizar_estado_icono(self.icon_humo, "red", f"¡HUMO DETECTADO! ({humo_val})")
            else:
                self._actualizar_estado_icono(self.icon_humo, "green", f"Humo: Normal ({humo_val})")

            # 4. AGUA
            agua = DataController.obtener_datos_agua()
            flujo = 0
            if agua and len(agua) > 0:
                flujo = agua[-1]["value"]
            
            if flujo > 45:
                self._actualizar_estado_icono(self.icon_agua, "red", f"¡FUGA! ({flujo} L/min)")
            else:
                self._actualizar_estado_icono(self.icon_agua, "blue", f"Agua: {flujo} L/min")

            # 5. VIENTO
            viento_val = 0
            if emerg["viento"] and len(emerg["viento"]) > 0:
                viento_val = emerg["viento"][-1]["value"]

            if viento_val > 50:
                self._actualizar_estado_icono(self.icon_viento, "red", f"¡VIENTO FUERTE! ({viento_val} km/h)")
            else:
                self._actualizar_estado_icono(self.icon_viento, "green", f"Viento: {viento_val} km/h")
            
            self.page.update()

        except Exception as e:
            print(f"Error Mapa: {e}")

    def _update_loop(self):
        while True:
            if self.page:
                self._update_ui()
            time.sleep(2)