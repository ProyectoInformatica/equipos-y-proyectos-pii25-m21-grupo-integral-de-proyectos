import flet as ft
import threading
import time
import os
from datetime import datetime
from controllers.data_controller import DataController
from controllers.scheduler import guardar_horario

class IluminacionView(ft.Container):
    def __init__(self, page, usuarioApp):
        super().__init__(expand=True)
        self.page = page
        self.activo = True

        # CONTROLES 
        control_op = ft.Text("Control por: ", weight=ft.FontWeight.BOLD)
        control_op_val = ft.Text("Manual")
        luminosidad_op = ft.Text("Luminosidad: ", weight=ft.FontWeight.BOLD)
        luminosidad_op_val = ft.Text("0")

        light_on = ft.Switch(value=False)
        
        # Cargar umbral desde light_config al iniciar usando DataController
        umbral_inicial = 50
        try:
            umbral_inicial = DataController.obtener_umbral_luminosidad()
        except Exception as ex:
            print(f"Error cargando umbral: {ex}")
        
        umbral = ft.Slider(min=0, max=100, divisions=20, label="{value}", value=umbral_inicial)
        umbral_text = ft.Text(f"Umbral actual: {umbral_inicial}")
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
                        DataController.guardar_estado_luz_automatico("on", "UMBRAL")
                    else:
                        mapa.src = "mapa_iluminacion_off.jpg"
                        light_status.value = "Luces APAGADAS (Por Sensor)"
                        light_status.color = "red"
                        DataController.guardar_estado_luz_automatico("off", "UMBRAL")

                elif modo == "Horario":
                    # Lógica visual para Horario (Calculamos si debería estar encendido)
                    try:
                        schedule_data = DataController.obtener_horario()
                        h_ini = int(schedule_data.get("hora_inicio", 0))
                        m_ini = int(schedule_data.get("minuto_inicio", 0))
                        h_fin = int(schedule_data.get("hora_fin", 0))
                        m_fin = int(schedule_data.get("minuto_fin", 0))
                        
                        ahora = datetime.now()
                        inicio_min = h_ini * 60 + m_ini
                        fin_min = h_fin * 60 + m_fin
                        actual_min = ahora.hour * 60 + ahora.minute
                        
                        # Calcular si está dentro del horario
                        dentro_horario = False
                        if fin_min < inicio_min:  # Cruza medianoche
                            dentro_horario = actual_min >= inicio_min or actual_min < fin_min
                        else:
                            dentro_horario = inicio_min <= actual_min < fin_min
                        
                        estado_esperado = "on" if dentro_horario else "off"
                        
                        if estado_esperado == "on":
                            mapa.src = "mapa_iluminacion_on.jpg"
                            light_status.value = "Luces ENCENDIDAS (Por Horario)"
                            light_status.color = "green"
                            DataController.guardar_estado_luz_automatico("on", "HORARIO")
                        else:
                            mapa.src = "mapa_iluminacion_off.jpg"
                            light_status.value = "Luces APAGADAS (Por Horario)"
                            light_status.color = "red"
                            DataController.guardar_estado_luz_automatico("off", "HORARIO")
                    except Exception as e:
                        print(f"Error calculando horario: {e}")
                        # Fallback: leer estado actual
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
                if not getattr(self, 'activo', True): break
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
            DataController.guardar_estado_luz_manual("on" if light_on.value else "off")
            page.update()

        light_on.on_change = toggle_light

        def control_automatico_click(e):
            cambiar_modo("Umbral")
            # Guardar umbral usando DataController
            try:
                resultado = DataController.guardar_umbral_luminosidad(int(umbral.value))
                if not resultado["success"]:
                    print(f"Error guardando umbral: {resultado['message']}")
            except Exception as ex:
                print(f"Error guardando umbral: {ex}")
            actualizar_interfaz_datos()

        def cambiar_umbral(e):
            umbral_text.value = f"Umbral actual: {int(umbral.value)}"
            # Guardar umbral en light_config cuando cambia
            from database import set_light_config
            try:
                set_light_config("umbral_luminosidad", str(int(umbral.value)))
            except Exception as ex:
                print(f"Error guardando umbral: {ex}")
            if control_op_val.value == "Umbral": actualizar_interfaz_datos()
            else: page.update()

        umbral.on_change = cambiar_umbral
        btn_auto = ft.ElevatedButton("Actualizar", on_click=control_automatico_click)

        # SECCIÓN HORARIO 
        horas = [f"{i:02d}" for i in range(24)]
        minutos = [f"{i:02d}" for i in range(0, 60, 5)]
        
        # Cargar horario desde la base de datos usando DataController
        horario_actual = DataController.obtener_horario()
        h_ini_default = f"{horario_actual.get('hora_inicio', 19):02d}"
        m_ini_default = f"{horario_actual.get('minuto_inicio', 30):02d}"
        h_fin_default = f"{horario_actual.get('hora_fin', 6):02d}"
        m_fin_default = f"{horario_actual.get('minuto_fin', 30):02d}"
        
        inicio_hora = ft.Dropdown(label="Hora inicio", options=[ft.dropdown.Option(h) for h in horas], value=h_ini_default, expand=1)
        inicio_minuto = ft.Dropdown(label="Minuto inicio", options=[ft.dropdown.Option(m) for m in minutos], value=m_ini_default, expand=1)
        fin_hora = ft.Dropdown(label="Hora fin", options=[ft.dropdown.Option(h) for h in horas], value=h_fin_default, expand=1)
        fin_minuto = ft.Dropdown(label="Minuto fin", options=[ft.dropdown.Option(m) for m in minutos], value=m_fin_default, expand=1)

        def accion_confirmar_horario(e):
            cambiar_modo("Horario")
            h_ini, m_ini = inicio_hora.value, inicio_minuto.value
            h_fin, m_fin = fin_hora.value, fin_minuto.value

            # Validar que todos los valores estén presentes
            if h_ini is None or m_ini is None or h_fin is None or m_fin is None:
                page.snack_bar = ft.SnackBar(ft.Text("Por favor, completa todos los campos del horario"), bgcolor="red")
                page.snack_bar.open = True
                page.update()
                return

            # Convertir a enteros y validar
            try:
                h_ini_int = int(h_ini)
                m_ini_int = int(m_ini)
                h_fin_int = int(h_fin)
                m_fin_int = int(m_fin)
            except (ValueError, TypeError):
                page.snack_bar = ft.SnackBar(ft.Text("Error: valores de horario inválidos"), bgcolor="red")
                page.snack_bar.open = True
                page.update()
                return

            if guardar_horario(h_ini_int, m_ini_int, h_fin_int, m_fin_int):
                page.snack_bar = ft.SnackBar(ft.Text(f"Horario activo: {h_ini}:{m_ini} a {h_fin}:{m_fin}"), bgcolor="green")
                light_status.value = "Esperando sincronización..."
                light_status.color = "orange"
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Error al guardar horario"), bgcolor="red")
            
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

        if usuarioApp["role"] != "admin":
            main_content = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(content=ft.Text("Iluminación inteligente de calles y zonas comunes", size=24, weight="bold"),
                            bgcolor="#ffffff", padding=20, border_radius=10, expand=True),   
                    ]),
                    ft.Row([panel_mapa]),
                    ft.Row([panel_op_control, panel_op_luminosidad]),
                    ], scroll=ft.ScrollMode.ADAPTIVE, expand=True
                ), expand=True
            )
        else:
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

        # main_content = ft.Container(
        #     content=ft.Column([
        #         ft.Row([
        #             ft.Container(content=ft.Text("Iluminación inteligente de calles y zonas comunes" + usuarioApp["role"], size=24, weight="bold"),
        #                 bgcolor="#ffffff", padding=20, border_radius=10, expand=True),   
        #         ]),
        #         ft.Row([panel_mapa]),
        #         ft.Row([panel_op_control, panel_op_luminosidad]),
        #         ft.Row([control_panel_manual, control_panel_umbral, control_panel_horario],
        #             vertical_alignment=ft.CrossAxisAlignment.START)
        #         ], scroll=ft.ScrollMode.ADAPTIVE, expand=True
        #     ), expand=True
        # )

        self.content = main_content

    def matar_hilos(self):
        self.activo = False