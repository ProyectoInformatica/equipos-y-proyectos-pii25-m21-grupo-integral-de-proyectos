import flet as ft
import matplotlib.pyplot as plt
import matplotlib
import io
import base64
import datetime
import threading
import time

# IMPORTAMOS EL CONTROLADOR
from controllers.data_controller import DataController

matplotlib.use('Agg')

def generar_grafica(x, y, titulo, ylabel):
    if not x or not y: return ""
    fig, ax = plt.subplots(figsize=(6, 3))
    colorGraf = "#458ce9" if ylabel == "km/h" else "darkblue"

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
    plt.close(fig)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode()


class EmergenciasView(ft.Container):
    def __init__(self, page):
        super().__init__(expand=True)
        self.page = page

        # --- IMÁGENES DE GRÁFICAS ---
        self.img_viento = ft.Image(src_base64="", border_radius=10, expand=1, fit=ft.ImageFit.CONTAIN)
        self.img_humo = ft.Image(src_base64="", border_radius=10, expand=1, fit=ft.ImageFit.CONTAIN)

        # --- CARGAR CONFIGURACIÓN GUARDADA ---
        config_actual = DataController.obtener_config_alertas()

        # --- DEFINICIÓN DE CONTROLES ---
        
        # 1. HUMO (0 a 100 nivel de opacidad/partículas)
        val_humo = config_actual.get("humo_max", 25)
        self.umbral_humo = ft.Slider(min=0, max=100, divisions=20, label="{value}", value=val_humo)
        self.txt_humo = ft.Text(f"Alerta actual: {int(self.umbral_humo.value)}")

        # 2. VIENTO (0 a 120 km/h)
        val_viento = config_actual.get("viento_max", 50)
        self.umbral_viento = ft.Slider(min=0, max=120, divisions=24, label="{value} km/h", value=val_viento)
        self.txt_viento = ft.Text(f"Alerta actual: {int(self.umbral_viento.value)} km/h")

        # --- EVENTOS INTERACTIVOS ---
        def on_change_humo(e):
            self.txt_humo.value = f"Alerta actual: {int(self.umbral_humo.value)}"
            self.page.update()

        def on_change_viento(e):
            self.txt_viento.value = f"Alerta actual: {int(self.umbral_viento.value)} km/h"
            self.page.update()

        self.umbral_humo.on_change = on_change_humo
        self.umbral_viento.on_change = on_change_viento

        # --- FUNCIÓN DE GUARDADO ---
        def guardar_y_actualizar(e):
            # 1. Leemos config actual para no borrar la de temperatura/aire
            config = DataController.obtener_config_alertas()
            
            # 2. Actualizamos solo los valores de emergencia
            config["humo_max"] = int(self.umbral_humo.value)
            config["viento_max"] = int(self.umbral_viento.value)

            # 3. Guardamos
            if DataController.guardar_config_alertas(config):
                self.page.snack_bar = ft.SnackBar(ft.Text("✅ Alertas de seguridad actualizadas"), bgcolor="green")
            else:
                self.page.snack_bar = ft.SnackBar(ft.Text("❌ Error guardando configuración"), bgcolor="red")
            self.page.snack_bar.open = True
            
            # 4. Refrescamos gráficas
            cargar_datos()

        # --- LÓGICA DE DATOS Y GRÁFICAS ---
        def cargar_datos(e=None):
            datos = DataController.obtener_datos_emergencia()
            d_viento = datos["viento"]
            d_humo = datos["humo"]

            if d_viento:
                # Formato H:M:S para ver cambios rápidos
                horas = [datetime.datetime.strptime(x["hora"], "%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S") for x in d_viento]
                self.img_viento.src_base64 = generar_grafica(horas, [x["value"] for x in d_viento], "Viento 24h", "km/h")
            
            if d_humo:
                horas_h = [datetime.datetime.strptime(x["hora"], "%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S") for x in d_humo]
                self.img_humo.src_base64 = generar_grafica(horas_h, [x["value"] for x in d_humo], "Humo 24h", "IAQ")

            self.page.update()

        # --- HILO AUTOMÁTICO ---
        def auto_refresh_loop():
            while True:
                time.sleep(10)
                try: cargar_datos()
                except: pass
        
        threading.Thread(target=auto_refresh_loop, daemon=True).start()
        cargar_datos() # Carga inicial
        
        # --- UI LAYOUT ---
        btn_humo = ft.ElevatedButton("Guardar Configuración", on_click=guardar_y_actualizar)
        btn_viento = ft.ElevatedButton("Guardar Configuración", on_click=guardar_y_actualizar)

        # Checkboxes visuales
        check_mail = ft.Checkbox(label="Notificar por correo")
        check_tel = ft.Checkbox(label="Notificar por teléfono")
        check_mail_v = ft.Checkbox(label="Notificar por correo")
        check_tel_v = ft.Checkbox(label="Notificar por teléfono")

        control_panel_humo = ft.Container(
            content=ft.Column([
                ft.Text("Alerta por humo", size=16, weight="bold"),
                self.txt_humo,
                self.umbral_humo,
                check_mail, check_tel,
                btn_humo
            ], spacing=10, horizontal_alignment="center"), 
            padding=20, bgcolor="#ffffff", border_radius=10, expand=1
        )

        control_panel_viento = ft.Container(
            content=ft.Column([
                ft.Text("Alerta por viento", size=16, weight="bold"),
                self.txt_viento,
                self.umbral_viento,
                check_mail_v, check_tel_v,
                btn_viento
            ], spacing=10, horizontal_alignment="center"), 
            padding=20, bgcolor="#ffffff", border_radius=10, expand=1
        )

        self.content = ft.Container(
            content=ft.Column([
                ft.Container(content=ft.Text("Gestión de emergencias y seguridad", size=24, weight="bold"),
                        bgcolor="#ffffff", padding=20, border_radius=10, expand=True),   
                ft.Row([self.img_viento, self.img_humo]),
                ft.Container(content=ft.Text("Configuración de alertas", size=16, weight="bold"),
                        bgcolor="#ffffff", padding=20, border_radius=10, expand=True),   
                ft.Row([control_panel_viento, control_panel_humo],vertical_alignment=ft.CrossAxisAlignment.START),
                ], scroll=ft.ScrollMode.ADAPTIVE
            )
        )