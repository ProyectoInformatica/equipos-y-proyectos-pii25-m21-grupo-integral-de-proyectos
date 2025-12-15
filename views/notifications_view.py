import flet as ft
import json
import os
import threading
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTIFICATIONS_FILE = os.path.join(BASE_DIR, "data", "notifications.json")

class NotificationsView(ft.Container):
    def __init__(self, page):
        super().__init__(expand=True, padding=20)
        self.page = page
        
        self.lista_alertas = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=10)

        self.content = ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, color="red", size=30),
                    ft.Text("Centro de Notificaciones y Alertas", size=24, weight="bold")
                ], alignment="center"),
                bgcolor="white",
                padding=20,
                border_radius=10,
                width=float("inf"), # Ocupa todo el ancho
                shadow=ft.BoxShadow(blur_radius=5, color="#1A000000")
            ),
            ft.Container(height=10), # Espacio separador

            # Contenedor de la lista
            ft.Container(
                content=self.lista_alertas,
                expand=True
            ),
            
            # Botón de acción
            ft.Row([
                ft.ElevatedButton("Borrar Historial", icon=ft.Icons.DELETE, 
                                  color="white", bgcolor="red", 
                                  on_click=self.borrar_historial)
            ], alignment="center")
        ])

        # Iniciar hilo de actualización
        threading.Thread(target=self._update_loop, daemon=True).start()

    def _leer_notificaciones(self):
        if not os.path.exists(NOTIFICATIONS_FILE): return []
        try:
            with open(NOTIFICATIONS_FILE, "r") as f: return json.load(f)
        except: return []

    def borrar_historial(self, e):
        try:
            with open(NOTIFICATIONS_FILE, "w") as f: json.dump([], f)
            self.page.snack_bar = ft.SnackBar(ft.Text("Historial borrado"))
            self.page.snack_bar.open = True
            self.page.update()
            self._refrescar_ui()
        except: pass

    def _refrescar_ui(self):
        datos = self._leer_notificaciones()
        self.lista_alertas.controls.clear()

        if not datos:
            self.lista_alertas.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=60, color="green"),
                        ft.Text("Sin alertas registradas", size=18, color="grey")
                    ], horizontal_alignment="center"),
                    alignment=ft.alignment.center,
                    padding=50
                )
            )
        else:
            for n in datos:
                # Icono y color según nivel
                icono = ft.Icons.INFO
                color_icono = "blue"
                bgcolor = "#e3f2fd" # azul claro

                if n.get("nivel") == "crítico":
                    icono = ft.Icons.WARNING
                    color_icono = "red"
                    bgcolor = "#ffebee" # rojo claro
                elif n.get("nivel") == "advertencia":
                    icono = ft.Icons.WARNING_AMBER
                    color_icono = "orange"
                    bgcolor = "#fff3e0" # naranja claro

                # Tarjeta de cada notificación individual
                card = ft.Container(
                    content=ft.Row([
                        ft.Icon(icono, color=color_icono, size=30),
                        ft.Column([
                            ft.Text(n.get("titulo", "Alerta"), weight="bold", size=16),
                            ft.Text(n.get("mensaje", ""), size=14),
                            ft.Text(n.get("hora", ""), size=12, color="grey")
                        ], expand=True)
                    ]),
                    bgcolor=bgcolor,
                    padding=15,
                    border_radius=10,
                    shadow=ft.BoxShadow(blur_radius=2, color="#1A000000") # Sutil sombra para cada alerta
                )
                self.lista_alertas.controls.append(card)

        if self.page: self.page.update()

    def _update_loop(self):
        while True:
            if self.page:
                try:
                    self._refrescar_ui()
                except:
                    pass
            time.sleep(3)