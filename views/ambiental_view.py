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

matplotlib.use('Agg') # Importante para evitar errores de hilos

def generar_grafica(x, y, titulo, ylabel):
    """Genera imagen base64 de una gráfica matplotlib."""
    if not x or not y: return ""
    
    fig, ax = plt.subplots(figsize=(6, 3))
    colorGraf = "cyan"
    if ylabel == "°C": colorGraf = "#e97547"
    elif ylabel == "%": colorGraf = "#458ce9"
    else: colorGraf = "darkblue"

    ax.plot(x, y, marker="o", color=colorGraf)
    ax.set_title(titulo)
    ax.set_xlabel("Hora")
    ax.set_ylabel(ylabel)
    ax.grid(True)
    
    # Ajustes eje X
    plt.xticks(rotation=45)
    if len(x) > 10:
        ax.set_xticks(range(0, len(x), 4))
        ax.set_xticklabels([x[i] for i in range(0, len(x), 4)])

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    plt.close(fig) 
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode()


class AmbientalView(ft.Container):
    def __init__(self, page):
        super().__init__(expand=True, padding=20)
        # CORRECCIÓN: Usamos un nombre distinto para no chocar con la propiedad 'page' de Flet
        self.page_ref = page 

        # --- CONTROLES VISUALES ---
        self.img_temp = ft.Image(src_base64="", border_radius=10, expand=1, fit=ft.ImageFit.CONTAIN)
        self.img_hum = ft.Image(src_base64="", border_radius=10, expand=1, fit=ft.ImageFit.CONTAIN)
        self.img_iaq = ft.Image(src_base64="", border_radius=10, expand=1, fit=ft.ImageFit.CONTAIN)

        # --- CARGA CONFIGURACIÓN ---
        config_inicial = DataController.obtener_config_alertas()

        # 1. TEMPERATURA
        self.umbral_temp = ft.Slider(min=0, max=50, divisions=50, label="{value}ºC", value=config_inicial.get("temp_max", 35))
        self.txt_temp = ft.Text(f"Alerta actual: {int(self.umbral_temp.value)}ºC")
        
        # 2. HUMEDAD
        self.umbral_hum = ft.Slider(min=0, max=100, divisions=20, label="{value}%", value=config_inicial.get("hum_max", 70))
        self.txt_hum = ft.Text(f"Alerta actual: {int(self.umbral_hum.value)}%")

        # 3. AIRE
        self.umbral_aire = ft.Slider(min=0, max=300, divisions=60, label="{value}", value=config_inicial.get("iaq_max", 100))
        self.txt_aire = ft.Text(f"Alerta actual: {int(self.umbral_aire.value)}")

        # --- EVENTOS VISUALES ---
        def on_change_temp(e):
            self.txt_temp.value = f"Alerta actual: {int(self.umbral_temp.value)}ºC"
            self.page_ref.update()

        def on_change_hum(e):
            self.txt_hum.value = f"Alerta actual: {int(self.umbral_hum.value)}%"
            self.page_ref.update()

        def on_change_aire(e):
            self.txt_aire.value = f"Alerta actual: {int(self.umbral_aire.value)}"
            self.page_ref.update()

        self.umbral_temp.on_change = on_change_temp
        self.umbral_hum.on_change = on_change_hum
        self.umbral_aire.on_change = on_change_aire

        # GUARDAR CAMBIOS ---
        def guardar_cambios(e):
            config = DataController.obtener_config_alertas()
            config["temp_max"] = int(self.umbral_temp.value)
            config["hum_max"] = int(self.umbral_hum.value)
            config["iaq_max"] = int(self.umbral_aire.value)

            if DataController.guardar_config_alertas(config):
                self.page_ref.snack_bar = ft.SnackBar(ft.Text("Configuración ambiental guardada"), bgcolor="green")
            else:
                self.page_ref.snack_bar = ft.SnackBar(ft.Text("Error al guardar"), bgcolor="red")
            
            self.page_ref.snack_bar.open = True
            cargar_y_actualizar_graficos() # Actualiza y refresca la página

        # LÓGICA GRÁFICAS 
        def cargar_y_actualizar_graficos(e=None):
            try:
                datos = DataController.obtener_datos_ambientales()
                
                if datos["temp"]:
                    horas = [datetime.datetime.strptime(x["hora"], "%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S") for x in datos["temp"]]
                    self.img_temp.src_base64 = generar_grafica(horas, [x["value"] for x in datos["temp"]], "Temperatura 24h", "°C")
                    self.img_hum.src_base64 = generar_grafica(horas, [x["value"] for x in datos["hum"]], "Humedad 24h", "%")
                    self.img_iaq.src_base64 = generar_grafica(horas, [x["value"] for x in datos["iaq"]], "Calidad Aire (IAQ)", "IAQ")
                
                # Usamos page_ref para evitar el error de NoneType
                if self.page_ref: 
                    self.page_ref.update()
            except Exception as e:
                print(f"Error actualizando gráficas: {e}")

        # HILO AUTOMÁTICO
        def auto_refresh_loop():
            while True:
                time.sleep(10)
                # Verificamos si la página sigue activa antes de actualizar
                if self.page_ref: 
                    try: cargar_y_actualizar_graficos()
                    except: pass
        
        threading.Thread(target=auto_refresh_loop, daemon=True).start()
        cargar_y_actualizar_graficos()

        # UI LAYOUT
        # Botones de guardar
        btn_temp = ft.ElevatedButton("Guardar Configuración", on_click=guardar_cambios)
        btn_hum = ft.ElevatedButton("Guardar Configuración", on_click=guardar_cambios)
        btn_aire = ft.ElevatedButton("Guardar Configuración", on_click=guardar_cambios)

        # Checkboxes
        self.check_mail_temp = ft.Checkbox(label="Notificar por correo")
        self.check_tel_temp = ft.Checkbox(label="Notificar por teléfono")
        self.check_mail_hum = ft.Checkbox(label="Notificar por correo")
        self.check_tel_hum = ft.Checkbox(label="Notificar por teléfono")
        self.check_mail_aire = ft.Checkbox(label="Notificar por correo")
        self.check_tel_aire = ft.Checkbox(label="Notificar por teléfono")

        # PANEL 1: TEMPERATURA
        control_panel_temperatura = ft.Container(
            content=ft.Column([
                ft.Text("Alerta por temperatura", size=16, weight="bold"),
                self.txt_temp,
                self.umbral_temp,
                self.check_mail_temp, 
                self.check_tel_temp,
                btn_temp
            ], spacing=10, horizontal_alignment="center"), 
            padding=20, bgcolor="#ffffff", border_radius=10, expand=1,
            shadow=ft.BoxShadow(blur_radius=5, color="#1A000000")
        )

        # PANEL 2: HUMEDAD
        control_panel_humedad = ft.Container(
            content=ft.Column([
                ft.Text("Alerta por humedad", size=16, weight="bold"),
                self.txt_hum,
                self.umbral_hum,
                self.check_mail_hum, 
                self.check_tel_hum,
                btn_hum
            ], spacing=10, horizontal_alignment="center"), 
            padding=20, bgcolor="#ffffff", border_radius=10, expand=1,
            shadow=ft.BoxShadow(blur_radius=5, color="#1A000000")
        )

        # PANEL 3: AIRE
        control_panel_aire = ft.Container(
            content=ft.Column([
                ft.Text("Alerta por calidad del aire", size=16, weight="bold"),
                self.txt_aire,
                self.umbral_aire,
                self.check_mail_aire, 
                self.check_tel_aire,
                btn_aire
            ], spacing=10, horizontal_alignment="center"), 
            padding=20, bgcolor="#ffffff", border_radius=10, expand=1,
            shadow=ft.BoxShadow(blur_radius=5, color="#1A000000")
        )

        # Contenido Principal
        self.content = ft.Column([
            # Encabezado estilo unificado
            ft.Container(
                content=ft.Text("Control ambiental de la zona", size=24, weight="bold"),
                bgcolor="white", 
                padding=20, 
                border_radius=10, 
                width=float("inf"),
                shadow=ft.BoxShadow(blur_radius=5, color="#1A000000")
            ),
            ft.Container(height=10),
            
            # Gráficas
            ft.Row([self.img_temp, self.img_hum, self.img_iaq]),
            
            ft.Container(height=20),
            ft.Container(
                content=ft.Text("Configuración de alertas", size=20, weight="bold"),
                padding=5
            ),
            
            # Paneles de control
            ft.Row([control_panel_temperatura, control_panel_humedad, control_panel_aire],
                   vertical_alignment=ft.CrossAxisAlignment.START),
            
        ], scroll=ft.ScrollMode.AUTO)