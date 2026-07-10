import flet as ft
import matplotlib.pyplot as plt
import matplotlib
import io
import base64
import datetime
import threading
import time

from controllers.data_controller import DataController

matplotlib.use('Agg')

def generar_grafica(x, y, titulo, ylabel):
    if not x or not y: return ""
    fig, ax = plt.subplots(figsize=(6, 3))
    try:
        colorGraf = "#458ce9" if ylabel == "km/h" else "darkblue"

        if len(x) != len(y):
            min_len = min(len(x), len(y))
            x = x[:min_len]
            y = y[:min_len]

        ax.plot(x, y, marker="o", color=colorGraf)
        ax.set_title(titulo)
        ax.set_xlabel("Hora")
        ax.set_ylabel(ylabel)
        ax.grid(True)
        plt.xticks(rotation=45)
        
        if len(x) > 10:
            ax.set_xticks(range(0, len(x), 4))
            ax.set_xticklabels([x[i] for i in range(0, len(x), 4)])

        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", bbox_inches="tight")
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode()
    finally:
        plt.close(fig)


class EmergenciasView(ft.Container):
    def __init__(self, page, usuarioApp):
        super().__init__(expand=True)
        self.page = page
        self.activo = True

        empty_png = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
        self.img_viento = ft.Image(src_base64=empty_png, border_radius=10, expand=1, fit=ft.ImageFit.CONTAIN)
        self.img_humo = ft.Image(src_base64=empty_png, border_radius=10, expand=1, fit=ft.ImageFit.CONTAIN)

        config_actual = DataController.obtener_config_alertas()

        val_humo = config_actual.get("humo_max", 25)
        self.umbral_humo = ft.Slider(min=0, max=100, divisions=20, label="{value}", value=val_humo)
        self.txt_humo = ft.Text(f"Alerta actual: {int(self.umbral_humo.value)}")

        val_viento = config_actual.get("viento_max", 50)
        self.umbral_viento = ft.Slider(min=0, max=120, divisions=24, label="{value} km/h", value=val_viento)
        self.txt_viento = ft.Text(f"Alerta actual: {int(self.umbral_viento.value)} km/h")

        def on_change_humo(e):
            self.txt_humo.value = f"Alerta actual: {int(self.umbral_humo.value)}"
            self.page.update()

        def on_change_viento(e):
            self.txt_viento.value = f"Alerta actual: {int(self.umbral_viento.value)} km/h"
            self.page.update()

        self.umbral_humo.on_change = on_change_humo
        self.umbral_viento.on_change = on_change_viento

        def guardar_y_actualizar(e):
            config = DataController.obtener_config_alertas()
            config["humo_max"] = int(self.umbral_humo.value)
            config["viento_max"] = int(self.umbral_viento.value)

            if DataController.guardar_config_alertas(config):
                self.page.snack_bar = ft.SnackBar(ft.Text("✅ Alertas de seguridad actualizadas"), bgcolor="green")
            else:
                self.page.snack_bar = ft.SnackBar(ft.Text("❌ Error guardando configuración"), bgcolor="red")
            self.page.snack_bar.open = True
            cargar_datos()

        def cargar_datos(e=None):
            datos = DataController.obtener_datos_emergencia()
            d_viento = datos["viento"]
            d_humo = datos["humo"]

            if d_viento:
                horas = [datetime.datetime.strptime(x["hora"], "%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S") for x in d_viento]
                self.img_viento.src_base64 = generar_grafica(horas, [x["value"] for x in d_viento], "Viento 24h", "km/h")
            
            if d_humo:
                horas_h = [datetime.datetime.strptime(x["hora"], "%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S") for x in d_humo]
                self.img_humo.src_base64 = generar_grafica(horas_h, [x["value"] for x in d_humo], "Humo 24h", "IAQ")

            if self.page: self.page.update()

        def auto_refresh_loop():
            while True:
                time.sleep(10)
                if not getattr(self, 'activo', True): break
                try: cargar_datos()
                except: pass
        
        threading.Thread(target=auto_refresh_loop, daemon=True).start()
        cargar_datos()
        
        btn_humo = ft.ElevatedButton("Guardar Configuración", on_click=guardar_y_actualizar)
        btn_viento = ft.ElevatedButton("Guardar Configuración", on_click=guardar_y_actualizar)

        control_panel_humo = ft.Container(
            content=ft.Column([
                ft.Text("Alerta por humo", size=16, weight="bold"),
                self.txt_humo, self.umbral_humo, btn_humo
            ], spacing=10, horizontal_alignment="center"), 
            padding=20, bgcolor="#ffffff", border_radius=10, expand=1
        )

        control_panel_viento = ft.Container(
            content=ft.Column([
                ft.Text("Alerta por viento", size=16, weight="bold"),
                self.txt_viento, self.umbral_viento, btn_viento
            ], spacing=10, horizontal_alignment="center"), 
            padding=20, bgcolor="#ffffff", border_radius=10, expand=1
        )

        if usuarioApp["role"] != "admin":
            self.content = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(content=ft.Text("Gestión de emergencias y seguridad", size=24, weight="bold"),
                                bgcolor="#ffffff", padding=20, border_radius=10, expand=True),   
                    ]),
                    ft.Row([self.img_viento, self.img_humo]),
                    ft.Row([
                        ft.Container(content=ft.Text("Configuración de alertas", size=16, weight="bold"),
                                bgcolor="#ffffff", padding=20, border_radius=10, expand=True),   
                    ]),
                    ft.Row([control_panel_humo],vertical_alignment=ft.CrossAxisAlignment.START),
                    ], scroll=ft.ScrollMode.ADAPTIVE
                )
            )
        else:
            self.content = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(content=ft.Text("Gestión de emergencias y seguridad", size=24, weight="bold"),
                                bgcolor="#ffffff", padding=20, border_radius=10, expand=True),   
                    ]),
                    ft.Row([self.img_viento, self.img_humo]),
                    ft.Row([
                        ft.Container(content=ft.Text("Configuración de alertas", size=16, weight="bold"),
                                bgcolor="#ffffff", padding=20, border_radius=10, expand=True),   
                    ]),
                    ft.Row([control_panel_viento],vertical_alignment=ft.CrossAxisAlignment.START),
                    ], scroll=ft.ScrollMode.ADAPTIVE
                )
            )

    def matar_hilos(self):
        self.activo = False