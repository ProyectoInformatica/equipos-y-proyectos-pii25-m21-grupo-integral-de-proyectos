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

    if ylabel == "km/h":
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


class EmergenciasView(ft.Container):
    def __init__(self, page):

        # ---------------------------------------
        # CARGAR JSONS
        # ---------------------------------------
        BASE = os.path.dirname(os.path.abspath(__file__))

        def cargar_json(rel_path):
            ruta = os.path.join(BASE, "..", rel_path)  # sube un nivel si 'views' está dentro de Proyecto-Informatica
            with open(ruta, "r") as f:
                return json.load(f)

        datos_viento = cargar_json("data/envviento.json")
        datos_humo = cargar_json("data/envhumo.json")

        # ---------------------------------------
        # EXTRAER HORAS Y VALORES
        # ---------------------------------------
        # Se asume que el JSON tiene formato:
        # { "hora": "2025-11-23 00:00:00", "value": 123 }

        horas = [datetime.datetime.strptime(x["hora"], "%Y-%m-%d %H:%M:%S").strftime("%H:%M") for x in datos_viento]

        viento = [x["value"] for x in datos_viento]
        humo = [x["value"] for x in datos_humo]

        # ---------------------------------------
        # GENERAR GRÁFICAS
        # ---------------------------------------
        img_viento = generar_grafica(horas, viento, "Viento durante 24h", "km/h")
        img_humo = generar_grafica(horas, humo, "Humo durante 24h", "IAQ")

        # ---------------------------------------
        # MOSTRAR EN FLET
        # ---------------------------------------

        def control_automatico_click(e):
            page.update()

        umbral_humo = ft.Slider(min=0, max=100, divisions=20, label="{value}", value=25)
        umbral_text_humo = ft.Text("Alerta actual: 25")
        btn_humo = ft.ElevatedButton("Actualizar", on_click=control_automatico_click)

        # Campo para correo y teléfono
        correo_input_humo = ft.TextField(label="Correo electrónico", visible=False, expand=True)
        telefono_input_humo = ft.TextField(label="Número de teléfono", visible=False, expand=True)
        
        # Checkboxes para notificaciones
        checkbox_correo_humo = ft.Checkbox(label="Notificar por correo")
        checkbox_telefono_humo = ft.Checkbox(label="Notificar por teléfono")
        
        # Funciones para mostrar/ocultar campos según checkbox
        def on_checkbox_change_humo(e):
            correo_input_humo.visible = checkbox_correo_humo.value
            telefono_input_humo.visible = checkbox_telefono_humo.value
            page.update()  # Actualiza la interfaz
        
        checkbox_correo_humo.on_change = on_checkbox_change_humo
        checkbox_telefono_humo.on_change = on_checkbox_change_humo

        control_panel_humo = ft.Container(
            content=ft.Column([
                ft.Row([ft.Text("Alerta por humo", size=16, weight="bold")], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([umbral_text_humo], alignment=ft.MainAxisAlignment.CENTER),
                umbral_humo,
                ft.Row([checkbox_correo_humo]),
                ft.Row([correo_input_humo]),
                ft.Row([checkbox_telefono_humo]),
                ft.Row([telefono_input_humo]),
                ft.Row([btn_humo], alignment=ft.MainAxisAlignment.CENTER)
            ], spacing=10),
            padding=20,
            bgcolor="#ffffff",
            border_radius=10,
            expand=1
        )

        umbral_viento = ft.Slider(min=0, max=100, divisions=20, label="Umbral luz: {value}", value=50)
        umbral_text_viento = ft.Text("Alerta actual: 50 km/h")
        btn_viento = ft.ElevatedButton("Actualizar", on_click=control_automatico_click)

        # Campo para correo y teléfono
        correo_input_viento = ft.TextField(label="Correo electrónico", visible=False, expand=True)
        telefono_input_viento = ft.TextField(label="Número de teléfono", visible=False, expand=True)
        
        # Checkboxes para notificaciones
        checkbox_correo_viento = ft.Checkbox(label="Notificar por correo")
        checkbox_telefono_viento = ft.Checkbox(label="Notificar por teléfono")
        
        # Funciones para mostrar/ocultar campos según checkbox
        def on_checkbox_change_viento(e):
            correo_input_viento.visible = checkbox_correo_viento.value
            telefono_input_viento.visible = checkbox_telefono_viento.value
            page.update()  # Actualiza la interfaz
        
        checkbox_correo_viento.on_change = on_checkbox_change_viento
        checkbox_telefono_viento.on_change = on_checkbox_change_viento

        control_panel_viento = ft.Container(
            content=ft.Column([
                ft.Row([ft.Text("Alerta por viento", size=16, weight="bold")], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([umbral_text_viento], alignment=ft.MainAxisAlignment.CENTER),
                umbral_viento,
                ft.Row([checkbox_correo_viento]),
                ft.Row([correo_input_viento]),
                ft.Row([checkbox_telefono_viento]),
                ft.Row([telefono_input_viento]),
                ft.Row([btn_viento], alignment=ft.MainAxisAlignment.CENTER)
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
                        content=ft.Text("Gestión de emergencias y seguridad", size=24, weight="bold"),
                        bgcolor="#ffffff",
                        padding=20,
                        border_radius=10,
                        expand=True
                    ),   
                ]),
                ft.Row([
                    ft.Image(src_base64=img_viento, border_radius=10, expand=1, fit=ft.ImageFit.CONTAIN),
                    ft.Image(src_base64=img_humo, border_radius=10, expand=1, fit=ft.ImageFit.CONTAIN),
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
                ft.Row([control_panel_viento, control_panel_humo],vertical_alignment=ft.CrossAxisAlignment.START),
                ],
                scroll=ft.ScrollMode.ADAPTIVE,  # <--- añade esto
                alignment=ft.MainAxisAlignment.START
            )
        )

        super().__init__(content=main_content, expand=True)
