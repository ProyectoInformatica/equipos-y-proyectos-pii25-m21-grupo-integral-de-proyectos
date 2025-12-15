import flet as ft
import threading
import time
from controllers.data_controller import DataController
from controllers.scheduler import guardar_horario

class IluminacionView(ft.Container):
    def __init__(self, page):
        super().__init__(expand=True)
        self.page = page

        # CONTROLES 
        control_op = ft.Text("Control por: ", weight=ft.FontWeight.BOLD)
        control_op_val = ft.Text("Manual")
        luminosidad_op = ft.Text("Luminosidad: ", weight=ft.FontWeight.BOLD)
        luminosidad_op_val = ft.Text("0")

        light_on = ft.Switch(value=False)
        umbral = ft.Slider(min=0, max=100, divisions=20, label="{value}", value=50)
        umbral_text = ft.Text("Umbral actual: 50")
        light_status = ft.Text("", color="red", weight="bold")

        mapa = ft.Image(src="mapa_iluminacion_off.jpg", expand=True, fit=ft.ImageFit.COVER)

        # LÓGICA DE ACTUALIZACIÓN VISUAL 
        def actualizar_interfaz_datos():
            try:
                # 1. Luminosidad (Siempre se actualiza)
                luminosidad_actual = DataController.obtener_luminosidad()
                luminosidad_op_val.value = str(luminosidad_actual)
                
                # 2. Control Lógico según el MODO
                modo = control_op_val.value
                
                if modo == "Umbral":
                    # Lógica visual para Umbral
                    if int(luminosidad_actual) < int(umbral.value):
                        mapa.src = "mapa_iluminacion_on.jpg"
                        light_status.value = "Luces ENCENDIDAS (Por Sensor)"
                        light_status.color = "green"
                    else:
                        mapa.src = "mapa_iluminacion_off.jpg"
                        light_status.value = "Luces APAGADAS (Por Sensor)"
                        light_status.color = "red"

                elif modo == "Horario":
                    # Lógica visual para Horario (Leemos el estado real del scheduler)
                    estado_real = DataController.obtener_estado_luz()
                    
                    if estado_real == "on":
                        mapa.src = "mapa_iluminacion_on.jpg"
                        light_status.value = "Luces ENCENDIDAS (Por Horario)"
                        light_status.color = "green"
                    else:
                        mapa.src = "mapa_iluminacion_off.jpg"
                        light_status.value = "Luces APAGADAS (Por Horario)"
                        light_status.color = "red"
                
                # (Si es Manual, no tocamos nada, el Switch manda)
                
                page.update()
            except Exception as e:
                print(f"Error UI: {e}")

        #  HILO AUTOMÁTICO 
        def ciclo_actualizacion_automatica():
            while True:
                time.sleep(2)
                if page: actualizar_interfaz_datos()

        threading.Thread(target=ciclo_actualizacion_automatica, daemon=True).start()

        # EVENTOS
        def cambiar_modo(nuevo_modo):
            control_op_val.value = nuevo_modo
            page.update()

        def toggle_light(e):
            cambiar_modo("Manual")
            mapa.src = "mapa_iluminacion_on.jpg" if light_on.value else "mapa_iluminacion_off.jpg"
            light_status.value = "Control Manual"
            light_status.color = "blue"
            page.update()

        light_on.on_change = toggle_light

        def control_automatico_click(e):
            cambiar_modo("Umbral")
            actualizar_interfaz_datos()

        def cambiar_umbral(e):
            umbral_text.value = f"Umbral actual: {int(umbral.value)}"
            if control_op_val.value == "Umbral": actualizar_interfaz_datos()
            else: page.update()

        umbral.on_change = cambiar_umbral
        btn_auto = ft.ElevatedButton("Actualizar", on_click=control_automatico_click)

        # SECCIÓN HORARIO 
        horas = [f"{i:02d}" for i in range(24)]
        minutos = [f"{i:02d}" for i in range(0, 60, 5)]
        
        inicio_hora = ft.Dropdown(label="Hora inicio", options=[ft.dropdown.Option(h) for h in horas], value="19", expand=1)
        inicio_minuto = ft.Dropdown(label="Minuto inicio", options=[ft.dropdown.Option(m) for m in minutos], value="30", expand=1)
        fin_hora = ft.Dropdown(label="Hora fin", options=[ft.dropdown.Option(h) for h in horas], value="06", expand=1)
        fin_minuto = ft.Dropdown(label="Minuto fin", options=[ft.dropdown.Option(m) for m in minutos], value="30", expand=1)

        def accion_confirmar_horario(e):
            cambiar_modo("Horario")
            h_ini, m_ini = inicio_hora.value, inicio_minuto.value
            h_fin, m_fin = fin_hora.value, fin_minuto.value

            if guardar_horario(h_ini, m_ini, h_fin, m_fin):
                page.snack_bar = ft.SnackBar(ft.Text(f"Horario activo: {h_ini}:{m_ini} a {h_fin}:{m_fin}"), bgcolor="green")
                light_status.value = "Esperando sincronización..."
                light_status.color = "orange"
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Error al guardar"), bgcolor="red")
            
            page.snack_bar.open = True
            page.update()

        boton_confirmar = ft.ElevatedButton("Confirmar", on_click=accion_confirmar_horario)

        # LAYOUT
        control_panel_manual = ft.Container(
            content=ft.Column([
                ft.Row([ft.Text("Control manual", size=16, weight="bold")], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([light_on], alignment=ft.MainAxisAlignment.CENTER),
            ], spacing=10), padding=20, bgcolor="#ffffff", border_radius=10, expand=1
        )

        control_panel_umbral = ft.Container(
            content=ft.Column([
                ft.Row([ft.Text("Control por Umbral", size=16, weight="bold")], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([umbral_text], alignment=ft.MainAxisAlignment.CENTER),
                umbral,
                ft.Row([btn_auto], alignment=ft.MainAxisAlignment.CENTER),
                light_status,
            ], spacing=10), padding=20, bgcolor="#ffffff", border_radius=10, expand=2
        )

        control_panel_horario = ft.Container(
            content=ft.Column([
                ft.Row([ft.Text("Control por Horario", size=16, weight="bold")], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([inicio_hora, inicio_minuto], spacing=10),
                ft.Row([fin_hora, fin_minuto], spacing=10),
                ft.Row([boton_confirmar], alignment=ft.MainAxisAlignment.CENTER)
            ], spacing=20), padding=20, bgcolor="#ffffff", border_radius=10, expand=2
        )

        panel_op_control = ft.Container(
            content=ft.Row([control_op, control_op_val], spacing=10),
            padding=20, bgcolor="#ffffff", border_radius=10, expand=1
        )

        panel_op_luminosidad = ft.Container(
            content=ft.Row([luminosidad_op, luminosidad_op_val],
                        spacing=10, alignment=ft.MainAxisAlignment.END),
            padding=20, bgcolor="#ffffff", border_radius=10, expand=1
        )

        panel_mapa = ft.Container(
            content=ft.Row([mapa], spacing=10),
            bgcolor="#ffffff", border_radius=10, expand=True
        )

        main_content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(content=ft.Text("Iluminación inteligente de calles y zonas comunes", size=24, weight="bold"),
                        bgcolor="#ffffff", padding=20, border_radius=10, expand=True),   
                ]),
                ft.Row([panel_mapa]),
                ft.Row([panel_op_control, panel_op_luminosidad]),
                ft.Row([control_panel_manual, control_panel_umbral, control_panel_horario],
                    vertical_alignment=ft.CrossAxisAlignment.START)
                ], scroll=ft.ScrollMode.ADAPTIVE, expand=True
            ), expand=True
        )

        self.content = main_content