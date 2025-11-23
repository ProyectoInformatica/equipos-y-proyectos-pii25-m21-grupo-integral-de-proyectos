import flet as ft
import matplotlib.pyplot as plt
import io
import base64
import os
import json
import datetime

def generar_grafica(x, y, titulo, ylabel):
    """Genera imagen base64 de una gráfica matplotlib."""
    fig, ax = plt.subplots(figsize=(6, 3))

    colorGraf = "cyan"

    if ylabel == "°C":
        colorGraf = "#e97547"
    elif ylabel == "%":
        colorGraf = "#458ce9"
    else:
        colorGraf = "darkblue"


    ax.plot(x, y, marker="o", color=colorGraf)
    ax.set_title(titulo)
    ax.set_xlabel("Hora")
    ax.set_ylabel(ylabel)
    ax.grid(True)

    # Rotar etiquetas del eje X para mejor lectura
    plt.xticks(rotation=45)

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode()


class AmbientalView(ft.Container):
    def __init__(self, page):

        # ---------------------------------------
        # CARGAR JSONS
        # ---------------------------------------
        BASE = os.path.dirname(os.path.abspath(__file__))

        def cargar_json(rel_path):
            ruta = os.path.join(BASE, "..", rel_path)  # sube un nivel si 'views' está dentro de Proyecto-Informatica
            with open(ruta, "r") as f:
                return json.load(f)

        datos_temp = cargar_json("data/envtemperatura.json")
        datos_hum = cargar_json("data/envhumedad.json")
        datos_iaq = cargar_json("data/envcalidadaire.json")

        # ---------------------------------------
        # EXTRAER HORAS Y VALORES
        # ---------------------------------------
        # Se asume que el JSON tiene formato:
        # { "hora": "2025-11-23 00:00:00", "value": 123 }

        horas = [datetime.datetime.strptime(x["hora"], "%Y-%m-%d %H:%M:%S").strftime("%H:%M") for x in datos_temp]

        temperatura = [x["value"] for x in datos_temp]
        humedad = [x["value"] for x in datos_hum]
        iaq = [x["value"] for x in datos_iaq]

        # ---------------------------------------
        # GENERAR GRÁFICAS
        # ---------------------------------------
        img_temp = generar_grafica(horas, temperatura, "Temperatura durante 24h", "°C")
        img_hum = generar_grafica(horas, humedad, "Humedad durante 24h", "%")
        img_iaq = generar_grafica(horas, iaq, "Calidad del aire (IAQ) durante 24h", "IAQ")

        # ---------------------------------------
        # MOSTRAR EN FLET
        # ---------------------------------------

        def control_automatico_click(e):
            page.update()

        umbral_temp = ft.Slider(min=0, max=60, divisions=20, label="{value}", value=30)
        umbral_text_temp = ft.Text("Alerta actual: 35°")  
        btn_temp = ft.ElevatedButton("Actualizar", on_click=control_automatico_click)

        # Campo para correo y teléfono
        correo_input_temp = ft.TextField(label="Correo electrónico", visible=False, expand=True)
        telefono_input_temp = ft.TextField(label="Número de teléfono", visible=False, expand=True)
        
        # Checkboxes para notificaciones
        checkbox_correo_temp = ft.Checkbox(label="Notificar por correo")
        checkbox_telefono_temp = ft.Checkbox(label="Notificar por teléfono")
        
        # Funciones para mostrar/ocultar campos según checkbox
        def on_checkbox_change_temp(e):
            correo_input_temp.visible = checkbox_correo_temp.value
            telefono_input_temp.visible = checkbox_telefono_temp.value
            page.update()  # Actualiza la interfaz
        
        checkbox_correo_temp.on_change = on_checkbox_change_temp
        checkbox_telefono_temp.on_change = on_checkbox_change_temp

        control_panel_temperatura = ft.Container(
            content=ft.Column([
                ft.Row([ft.Text("Alerta por temperatura", size=16, weight="bold")], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([umbral_text_temp], alignment=ft.MainAxisAlignment.CENTER),
                umbral_temp,
                ft.Row([checkbox_correo_temp]),
                ft.Row([correo_input_temp]),
                ft.Row([checkbox_telefono_temp]),
                ft.Row([telefono_input_temp]),
                ft.Row([btn_temp], alignment=ft.MainAxisAlignment.CENTER)
            ], spacing=10),
            padding=20,
            bgcolor="#ffffff",
            border_radius=10,
            expand=1
        )

        umbral_hum = ft.Slider(min=0, max=100, divisions=20, label="{value}", value=50)
        umbral_text_hum = ft.Text("Alerta actual: 50%")
        btn_hum = ft.ElevatedButton("Actualizar", on_click=control_automatico_click)

        # Campo para correo y teléfono
        correo_input_hum = ft.TextField(label="Correo electrónico", visible=False, expand=True)
        telefono_input_hum = ft.TextField(label="Número de teléfono", visible=False, expand=True)
        
        # Checkboxes para notificaciones
        checkbox_correo_hum = ft.Checkbox(label="Notificar por correo")
        checkbox_telefono_hum = ft.Checkbox(label="Notificar por teléfono")
        
        # Funciones para mostrar/ocultar campos según checkbox
        def on_checkbox_change_hum(e):
            correo_input_hum.visible = checkbox_correo_hum.value
            telefono_input_hum.visible = checkbox_telefono_hum.value
            page.update()  # Actualiza la interfaz
        
        checkbox_correo_hum.on_change = on_checkbox_change_hum
        checkbox_telefono_hum.on_change = on_checkbox_change_hum

        control_panel_humedad = ft.Container(
            content=ft.Column([
                ft.Row([ft.Text("Alerta por humedad", size=16, weight="bold")], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([umbral_text_hum], alignment=ft.MainAxisAlignment.CENTER),
                umbral_hum,
                ft.Row([checkbox_correo_hum]),
                ft.Row([correo_input_hum]),
                ft.Row([checkbox_telefono_hum]),
                ft.Row([telefono_input_hum]),
                ft.Row([btn_hum], alignment=ft.MainAxisAlignment.CENTER)
            ], spacing=10),
            padding=20,
            bgcolor="#ffffff",
            border_radius=10,
            expand=1
        )

        umbral_aire = ft.Slider(min=0, max=150, divisions=20, label="Umbral luz: {value}", value=85)
        umbral_text_aire = ft.Text("Alerta actual: 85")
        btn_aire = ft.ElevatedButton("Actualizar", on_click=control_automatico_click)

        # Campo para correo y teléfono
        correo_input_aire = ft.TextField(label="Correo electrónico", visible=False, expand=True)
        telefono_input_aire = ft.TextField(label="Número de teléfono", visible=False, expand=True)
        
        # Checkboxes para notificaciones
        checkbox_correo_aire = ft.Checkbox(label="Notificar por correo")
        checkbox_telefono_aire = ft.Checkbox(label="Notificar por teléfono")
        
        # Funciones para mostrar/ocultar campos según checkbox
        def on_checkbox_change_aire(e):
            correo_input_aire.visible = checkbox_correo_aire.value
            telefono_input_aire.visible = checkbox_telefono_aire.value
            page.update()  # Actualiza la interfaz
        
        checkbox_correo_aire.on_change = on_checkbox_change_aire
        checkbox_telefono_aire.on_change = on_checkbox_change_aire

        control_panel_aire = ft.Container(
            content=ft.Column([
                ft.Row([ft.Text("Alerta por calidad del aire", size=16, weight="bold")], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([umbral_text_aire], alignment=ft.MainAxisAlignment.CENTER),
                umbral_aire,
                ft.Row([checkbox_correo_aire]),
                ft.Row([correo_input_aire]),
                ft.Row([checkbox_telefono_aire]),
                ft.Row([telefono_input_aire]),
                ft.Row([btn_aire], alignment=ft.MainAxisAlignment.CENTER)
            ], spacing=10),
            padding=20,
            bgcolor="#ffffff",
            border_radius=10,
            expand=1
        )

        main_content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Text("Control ambiental de la zona", size=24, weight="bold"),
                        bgcolor="#ffffff",
                        padding=20,
                        border_radius=10,
                        expand=True
                    ),   
                ]),
                ft.Row([
                    ft.Image(src_base64=img_temp, border_radius=10, expand=1, fit=ft.ImageFit.CONTAIN),
                    ft.Image(src_base64=img_hum, border_radius=10, expand=1, fit=ft.ImageFit.CONTAIN),
                    ft.Image(src_base64=img_iaq, border_radius=10, expand=1, fit=ft.ImageFit.CONTAIN),
                ]),
                ft.Row([
                    ft.Container(
                        content=ft.Text("Configuración de alertas", size=16, weight="bold"),
                        bgcolor="#ffffff",
                        padding=20,
                        border_radius=10,
                        expand=True
                    ),   
                ]),
                ft.Row([control_panel_temperatura, control_panel_humedad, control_panel_aire],vertical_alignment=ft.CrossAxisAlignment.START),
                ],
                scroll=ft.ScrollMode.ADAPTIVE,  # <--- añade esto
                alignment=ft.MainAxisAlignment.START
            )
        )

        super().__init__(content=main_content, expand=True)
