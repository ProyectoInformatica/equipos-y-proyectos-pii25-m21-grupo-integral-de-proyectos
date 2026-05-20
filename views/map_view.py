import flet as ft
import os
import sys
import threading
import time
from datetime import datetime

# Importar controladores
from controllers.data_controller import DataController


class MapView(ft.Container):
    def __init__(self, page=None): 
        super().__init__()
        self.page = page
        self.expand = True 
        self.padding = 20
        self.running = True
        
        # Estado actual para estadísticas
        self.current_state = {
            "lights": False,
            "barriers": False,
            "water_flow": 0.0,
            "water_alert": False,
            "last_update": datetime.now().strftime("%H:%M:%S")
        }
        
        # Configuración de tipos de marcadores
        self.marker_configs = {
            "light": {
                "icon": "assets/icon_iluminacion.png",
                "size": 40,
                "count": 2,
                "colors": {"on": ("yellow100", "orange"), "off": ("grey200", "grey600")},
                "dialog_title": "Gestionar Iluminación",
                "dialog_handler": self._light_dialog_handler,
                "name": "Iluminación"
            },
            "barrier": {
                "icon": "assets/icon_acceso.png",
                "size": 42,
                "count": 2,
                "colors": {"on": ("green100", "green600"), "off": ("red100", "red600")},
                "dialog_title": "Control de Accesos",
                "dialog_handler": self._barrier_dialog_handler,
                "name": "Accesos"
            },
            "water": {
                "icon": "assets/icon_recursos.png",
                "size": 40,
                "count": 2,
                "colors": {"on": ("blue100", "blue600"), "off": ("red100", "red600")},
                "dialog_title": "Gestión de Suministro de Agua",
                "dialog_handler": self._water_dialog_handler,
                "name": "Agua"
            }
        }

        # Crear marcadores dinámicamente
        self.markers = {}
        for marker_type, config in self.marker_configs.items():
            self.markers[marker_type] = [
                self._create_marker_container(config["icon"], config["size"], marker_type)
                for _ in range(config["count"])
            ]

        self.content = self._build_ui()

    def _create_marker_container(self, icon_src, size, marker_type):
        container = ft.Container(
            content=ft.Image(src=icon_src, width=size, height=size, fit=ft.ImageFit.CONTAIN),
            bgcolor="white",
            border_radius=50,
            padding=8,
            border=ft.border.all(2, "grey400"),
            data=marker_type
        )
        return container

    def did_mount(self):
        self.running = True
        self.th = threading.Thread(target=self.update_map_state, daemon=True)
        self.th.start()

    def will_unmount(self):
        self.running = False

    def matar_hilos(self):
        self.running = False

    def update_map_state(self):
        while self.running:
            # Actualizar luces
            light_state = DataController.obtener_estado_luz()
            is_on = light_state.upper() == "ON"
            self.current_state["lights"] = is_on
            colors = self.marker_configs["light"]["colors"]["on" if is_on else "off"]
            for marker in self.markers["light"]:
                self._update_marker_style(marker, colors[0], colors[1])

            # Actualizar barreras (tomar la primera barrera como referencia, o combinar ambas)
            access_data = DataController.obtener_estado_barreras()
            # Si hay múltiples barreras, considerar abierta si alguna lo está
            is_open = False
            if isinstance(access_data, dict):
                for barrera, estado in access_data.items():
                    if isinstance(estado, dict) and estado.get("barrera_abierta", False):
                        is_open = True
                        break
            self.current_state["barriers"] = is_open
            colors = self.marker_configs["barrier"]["colors"]["on" if is_open else "off"]
            for marker in self.markers["barrier"]:
                self._update_marker_style(marker, colors[0], colors[1])

            # Actualizar agua
            # Obtener flujo de agua desde recursos
            recursos_agua = DataController.obtener_datos_agua()
            flujo = recursos_agua[0]["value"] if recursos_agua else 0.0
            hay_fuga = flujo > 5.0
            self.current_state["water_flow"] = flujo
            self.current_state["water_alert"] = hay_fuga
            colors = self.marker_configs["water"]["colors"]["off" if hay_fuga else "on"]
            for marker in self.markers["water"]:
                self._update_marker_style(marker, colors[0], colors[1])
            
            self.current_state["last_update"] = datetime.now().strftime("%H:%M:%S")
            self._update_stats_panel()
            
            try:
                self.update()
            except:
                break
            time.sleep(1)

    def _update_marker_style(self, control, bgcolor, border_color):
        control.bgcolor = bgcolor
        control.border = ft.border.all(3, border_color)

    def _update_stats_panel(self):
        if hasattr(self, 'stats_panel'):
            # Actualizar texto de estadísticas
            light_status = "ACTIVA" if self.current_state["lights"] else "INACTIVA"
            self.stats_light_text.value = light_status
            self.stats_light_text.color = "green" if self.current_state["lights"] else "black"
            
            barrier_status = "ABIERTA" if self.current_state["barriers"] else "CERRADA"
            self.stats_barrier_text.value = barrier_status
            self.stats_barrier_text.color = "green" if self.current_state["barriers"] else "red"
            
            water_status = "ALERTA" if self.current_state["water_alert"] else "NORMAL"
            self.stats_water_text.value = f"{water_status} ({self.current_state['water_flow']:.1f} L/min)"
            self.stats_water_text.color = "red" if self.current_state["water_alert"] else "green"
            
            self.stats_update_text.value = f"Última actualización: {self.current_state['last_update']}"

    def _show_dialog(self, title, content, actions=None):
        dlg = ft.AlertDialog(
            title=ft.Text(title, size=20, weight="bold"),
            content=content,
            actions=actions or [],
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=10)
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def _close_dialog(self):
        self.page.dialog.open = False
        self.page.update()

    def _show_snackbar(self, message, bgcolor="blue"):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Row([
                ft.Icon(name="check_circle", color="white"),
                ft.Text(message, color="white", weight="bold")
            ], tight=True),
            bgcolor=bgcolor,
            duration=3000
        )
        self.page.snack_bar.open = True
        self.page.update()

    def _light_dialog_handler(self):
        def set_light(state):
            DataController.guardar_estado_luz_manual("on" if state else "off")
            self._close_dialog()
            self._show_snackbar(f"Luces {'ENCENDIDAS' if state else 'APAGADAS'} manualmente", 
                              "orange" if state else "grey")

        def set_auto(e):
            DataController.guardar_estado_luz_manual("off")  # Desactivar modo manual
            self._close_dialog()
            self._show_snackbar("Luces en modo AUTOMÁTICO", "blue")

        content = ft.Container(
            content=ft.Column([
                ft.Text("Seleccione una acción manual:", size=14),
                ft.Row([
                    ft.ElevatedButton(
                        "Encender", 
                        icon="light_mode", 
                        on_click=lambda _: set_light(True), 
                        bgcolor="orange",
                        color="white"
                    ),
                    ft.ElevatedButton(
                        "Apagar", 
                        icon="nightlight_round", 
                        on_click=lambda _: set_light(False), 
                        bgcolor="grey600",
                        color="white"
                    ),
                ], alignment="center", spacing=10),
                ft.Divider(height=20),
                ft.OutlinedButton(
                    "Restaurar Automático", 
                    width=250, 
                    on_click=set_auto
                ),
            ], tight=True, horizontal_alignment="center", spacing=10),
            width=350,
            padding=20
        )
        
        self._show_dialog("Gestionar Iluminación", content, 
                         [ft.TextButton("Cancelar", on_click=lambda _: self._close_dialog())])

    def _barrier_dialog_handler(self):
        def set_barrier(state):
            # Por defecto modificar la barrera "norte", puedes ajustar según necesites
            DataController.guardar_manual_barrera("norte", True, state)
            self._close_dialog()
            self._show_snackbar(f"Barrera {'ABIERTA' if state else 'CERRADA'} manualmente",
                              "green" if state else "red")

        def set_auto(e):
            DataController.guardar_manual_barrera("norte", False, False)
            self._close_dialog()
            self._show_snackbar("Barrera en modo AUTOMÁTICO", "blue")

        content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.ElevatedButton(
                        "Abrir", 
                        icon="lock_open", 
                        on_click=lambda _: set_barrier(True), 
                        bgcolor="green",
                        color="white"
                    ),
                    ft.ElevatedButton(
                        "Cerrar", 
                        icon="lock_outline", 
                        on_click=lambda _: set_barrier(False), 
                        bgcolor="red",
                        color="white"
                    ),
                ], alignment="center", spacing=10),
                ft.Divider(height=20),
                ft.OutlinedButton(
                    "Modo Automático", 
                    width=250, 
                    on_click=set_auto
                ),
            ], tight=True, horizontal_alignment="center", spacing=10),
            width=350,
            padding=20
        )
        
        self._show_dialog("Control de Accesos", content, 
                         [ft.TextButton("Cancelar", on_click=lambda _: self._close_dialog())])

    def _water_dialog_handler(self):
        flujo = get_latest_resource_value("water")
        hay_fuga = flujo > 5.0
        
        def set_valve(state):
            # Nota: No hay tabla específica para water_manual_state en la BD
            # Si necesitas esta funcionalidad, deberías añadirla a database.py
            # Por ahora solo mostramos el mensaje
            self._close_dialog()
            accion = "SUMINISTRO RESTAURADO" if state else "CORTE DE SUMINISTRO"
            self._show_snackbar(f"{accion} realizado manualmente", "green" if state else "red")

        content = ft.Container(
            content=ft.Column([
                ft.Container(
                    bgcolor="red50" if hay_fuga else "blue50",
                    padding=15,
                    border_radius=10,
                    content=ft.Row([
                        ft.Icon(name="water_drop", color="red" if hay_fuga else "blue", size=30),
                        ft.Text(f"Flujo Actual: {flujo:.2f} L/min", weight="bold", size=16),
                    ], spacing=15, alignment="center")
                ),
                ft.Text("Control de Válvula Principal:", size=12),
                ft.Row([
                    ft.ElevatedButton(
                        "Cerrar Suministro", 
                        icon="block", 
                        on_click=lambda _: set_valve(False), 
                        bgcolor="red",
                        color="white"
                    ),
                    ft.OutlinedButton(
                        "Abrir Válvula", 
                        icon="check_circle",
                        on_click=lambda _: set_valve(True)
                    ),
                ], alignment="center", spacing=10),
            ], tight=True, horizontal_alignment="center", spacing=10),
            width=400,
            padding=20
        )
        
        self._show_dialog("Gestión de Suministro de Agua", content, 
                         [ft.TextButton("Cancelar", on_click=lambda _: self._close_dialog())])

    def toggle_lights_dialog(self, e):
        self._light_dialog_handler()

    def toggle_barrier_dialog(self, e):
        self._barrier_dialog_handler()

    def toggle_water_dialog(self, e):
        self._water_dialog_handler()

    def _create_stats_panel(self):
        self.stats_light_text = ft.Text("INACTIVA", size=14, weight="bold", color="black")
        self.stats_barrier_text = ft.Text("CERRADA", size=14, weight="bold", color="red")
        self.stats_water_text = ft.Text("NORMAL (0.0 L/min)", size=14, weight="bold", color="green")
        self.stats_update_text = ft.Text("Última actualización: --:--:--", size=11, color="grey", italic=True)
        
        return ft.Container(
            bgcolor="#ffffff",
            padding=20,
            border_radius=10,
            content=ft.Column([
                ft.Row([
                    ft.Icon(name="dashboard", size=20, color="blueGrey700"),
                    ft.Text("Estado del Sistema", size=16, weight="bold", color="blueGrey800")
                ], spacing=10),
                ft.Divider(height=15, thickness=1),
                ft.Row([
                    ft.Icon(name="light_mode", size=20, color="orange"),
                    ft.Column([
                        ft.Text("Iluminación", size=12, color="grey600"),
                        self.stats_light_text
                    ], spacing=2, tight=True)
                ], spacing=10),
                ft.Row([
                    ft.Icon(name="security", size=20, color="blue"),
                    ft.Column([
                        ft.Text("Accesos", size=12, color="grey600"),
                        self.stats_barrier_text
                    ], spacing=2, tight=True)
                ], spacing=10),
                ft.Row([
                    ft.Icon(name="water_drop", size=20, color="blue"),
                    ft.Column([
                        ft.Text("Suministro de Agua", size=12, color="grey600"),
                        self.stats_water_text
                    ], spacing=2, tight=True)
                ], spacing=10),
                ft.Divider(height=10),
                self.stats_update_text
            ], spacing=8, tight=True),
            expand=1
        )

    def _build_ui(self):
        # Header similar a iluminacion_view
        header = ft.Container(
            content=ft.Text("Mapa Interactivo de Zona", size=24, weight="bold"),
            bgcolor="#ffffff",
            padding=20,
            border_radius=10,
            expand=True
        )

        # Mapa base - estilo simple
        map_image = ft.Image(
            src="assets/mapa_iluminacion_off.jpg", 
            fit=ft.ImageFit.COVER,
            expand=True
        )

        # Crear marcadores con configuración
        marker_configs = [
            ("Iluminación", self.markers["light"][0], self.toggle_lights_dialog, {"top": 30, "left": 100}),
            # ("Farola 2", self.markers["light"][1], self.toggle_lights_dialog, {"top": 100, "right": 100}),
            ("Acceso Sur", self.markers["barrier"][0], self.toggle_barrier_dialog, {"bottom": 10, "left": 280, "right": 0, "alignment": ft.alignment.center}),
            ("Acceso Norte", self.markers["barrier"][1], self.toggle_barrier_dialog, {"top": 10, "left": 480, "right": 0, "alignment": ft.alignment.center}),
            ("Agua A", self.markers["water"][0], self.toggle_water_dialog, {"bottom": 50, "left": 80}),
            ("Riego", self.markers["water"][1], self.toggle_water_dialog, {"bottom": 150, "right": 20}),
        ]

        # Crear marcadores
        markers = []
        for label, marker, handler, position in marker_configs:
            marker_widget = self._create_marker_widget(label, marker, handler)
            markers.append(ft.Container(
                content=marker_widget,
                **position
            ))

        # Panel de estadísticas
        self.stats_panel = self._create_stats_panel()

        # Leyenda - estilo simple
        legend_card = ft.Container(
            bgcolor="#ffffff",
            padding=20,
            border_radius=10,
            content=ft.Column([
                ft.Row([
                    ft.Icon(name="info", size=20, color="blueGrey700"),
                    ft.Text("Leyenda", weight="bold", size=16, color="blueGrey800")
                ], spacing=8),
                ft.Divider(height=12, thickness=1),
                self._legend_item("yellow", "Luz ON", "orange"),
                self._legend_item("grey", "Luz OFF", "black"),
                self._legend_item("green", "Abierto", None),
                self._legend_item("red", "Cerrado", None),
                self._legend_item("blue", "Agua OK", "blue"),
                self._legend_item("red", "Alerta", "red"),
                ft.Divider(height=10),
                ft.Container(height=15)
            ], spacing=8, tight=True),
            expand=1
        )

        # Contenedor del mapa con marcadores
        panel_mapa = ft.Container(
            content=ft.Stack([
                map_image,
                *markers
            ]),
            bgcolor="#ffffff",
            border_radius=10,
            expand=True
        )

        # Layout principal - similar a iluminacion_view
        main_content = ft.Container(
            content=ft.Column([
                ft.Row([header]),
                ft.Row([panel_mapa]),
                ft.Row([
                    self.stats_panel,
                    legend_card
                ], vertical_alignment=ft.CrossAxisAlignment.START)
            ], scroll=ft.ScrollMode.ADAPTIVE, expand=True, spacing=10),
            expand=True
        )

        return main_content

    def _create_marker_widget(self, label, status_control, on_click_handler):
        marker_container = ft.Container(
            content=ft.Column([
                status_control,
                ft.Container(
                    content=ft.Text(label, size=10, weight="bold", color="white"), 
                    bgcolor="black87",
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    border_radius=5
                )
            ], horizontal_alignment="center", spacing=4, tight=True)
        )

        return ft.GestureDetector(
            mouse_cursor=ft.MouseCursor.CLICK,
            on_tap=on_click_handler,
            content=marker_container
        )

    def _legend_item(self, color, text, border_color):
        border = ft.border.all(2, border_color) if border_color else ft.border.all(1, "grey400")
        return ft.Row([
            ft.Container(
                width=14,
                height=14,
                bgcolor=color,
                border=border,
                border_radius=3
            ),
            ft.Text(text, size=12, color="black")
        ], spacing=10, tight=True)
