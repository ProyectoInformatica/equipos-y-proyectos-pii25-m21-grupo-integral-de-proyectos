import flet as ft

class IluminacionView(ft.Container):
    def __init__(self, page):
        # -------------------- CONTROLES --------------------
        control_op = ft.Text("Control por: ", weight=ft.FontWeight.BOLD)
        control_op_val = ft.Text("Manual")
        luminosidad_op = ft.Text("Luminosidad: ", weight=ft.FontWeight.BOLD)
        luminosidad_op_val = ft.Text("0")

        light_on = ft.Switch(value=False)
        umbral = ft.Slider(min=0, max=100, divisions=20, label="Umbral luz: {value}", value=50)
        umbral_text = ft.Text("Umbral actual: 50")
        light_status = ft.Text("", color="red", weight="bold")

        mapa = ft.Image(src="mapa_iluminacion_off.jpg", expand=True, fit=ft.ImageFit.COVER)

        # -------------------- FUNCIONES AUXILIARES --------------------
        def actualizar_imagen(estado):
            mapa.src = "mapa_iluminacion_on.jpg" if estado == "on" else "mapa_iluminacion_off.jpg"

        # -------------------- MANEJO DE HILOS --------------------
        def iniciar_hilo_umbral():
            """Inicia el hilo de control por umbral."""
            def loop_control_automatico():

             return "hilo"

        def iniciar_hilo_horario():

            return "hilo"

        def detener_hilos():
            """Detiene los hilos de modo natural cambiando el modo a Manual."""

        # -------------------- CAMBIO DE MODO --------------------
        def cambiar_modo(nuevo_modo):
            """Cambia entre los modos Manual / Umbral / Horario."""
            detener_hilos()  # Detiene los hilos anteriores

            if nuevo_modo == "Manual":
                control_op_val.value = "Manual"
                hilo_umbral = None
                hilo_horario = None

            elif nuevo_modo == "Umbral":
                control_op_val.value = "Umbral"
                modo_actual = "Umbral"
                hilo_umbral = iniciar_hilo_umbral()
                hilo_horario = None

            elif nuevo_modo == "Horario":
                control_op_val.value = "Horario"
                modo_actual = "Horario"
                hilo_horario = iniciar_hilo_horario()
                hilo_umbral = None

            page.update()

        # -------------------- EVENTOS UI --------------------
        def toggle_light(e):
            """Activa modo manual al usar el switch."""
            cambiar_modo("Manual")
            estado = "on"
            if estado == "on":
                actualizar_imagen("on")
            else:
                actualizar_imagen("off")
            page.update()

        light_on.on_change = toggle_light

        def cambiar_umbral(e):
            umbral_text.value = f"Umbral actual: {int(umbral.value)}"
            page.update()

        umbral.on_change = cambiar_umbral

        def control_automatico_click(e):
            """Activa modo Umbral al pulsar el botón."""
            cambiar_modo("Umbral")
            valor, estado = 28
            if estado == "error":
                light_status.value = "Error leyendo light.json"
                light_status.color = "orange"
            else:
                actualizar_imagen(estado)
            page.update()

        btn_auto = ft.ElevatedButton("Actualizar", on_click=control_automatico_click)

        # -------------------- HORARIO --------------------
        horas = [f"{i:02d}" for i in range(24)]
        minutos = [f"{i:02d}" for i in range(0, 60, 5)]
        inicio_hora = ft.Dropdown(label="Hora de inicio", options=[ft.dropdown.Option(h) for h in horas], expand=1)
        inicio_minuto = ft.Dropdown(label="Minuto de inicio", options=[ft.dropdown.Option(m) for m in minutos], expand=1)
        fin_hora = ft.Dropdown(label="Hora de fin", options=[ft.dropdown.Option(h) for h in horas], expand=1)
        fin_minuto = ft.Dropdown(label="Minuto de fin", options=[ft.dropdown.Option(m) for m in minutos], expand=1)

        def mostrar_valores(e):
            """Activa modo Horario al pulsar Confirmar."""
            cambiar_modo("Horario")

            h_inicio = inicio_hora.value or "00"
            m_inicio = inicio_minuto.value or "00"
            h_fin = fin_hora.value or "00"
            m_fin = fin_minuto.value or "00"

            if (int(h_fin), int(m_fin)) <= (int(h_inicio), int(m_inicio)):
                page.snack_bar = ft.SnackBar(ft.Text("⚠️ La hora de fin debe ser mayor que la de inicio."))
            else:
                horario = {
                    "hora_inicio": h_inicio,
                    "minuto_inicio": m_inicio,
                    "hora_fin": h_fin,
                    "minuto_fin": m_fin
                }
            page.snack_bar.open = True
            page.update()

        boton = ft.ElevatedButton("Confirmar", on_click=mostrar_valores)

        # -------------------- LAYOUT ORIGINAL --------------------
        control_panel_manual = ft.Container(
            content=ft.Column([
                ft.Row([ft.Text("Control manual", size=16, weight="bold")], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([light_on], alignment=ft.MainAxisAlignment.CENTER),
            ], spacing=10),
            padding=20,
            bgcolor="#ffffff",
            border_radius=10,
            expand=1
        )

        control_panel_umbral = ft.Container(
            content=ft.Column([
                ft.Row([ft.Text("Control por Umbral", size=16, weight="bold")], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([umbral_text], alignment=ft.MainAxisAlignment.CENTER),
                umbral,
                ft.Row([btn_auto], alignment=ft.MainAxisAlignment.CENTER),
                light_status,
            ], spacing=10),
            padding=20,
            bgcolor="#ffffff",
            border_radius=10,
            expand=2
        )

        control_panel_horario = ft.Container(
            content=ft.Column([
                ft.Row([ft.Text("Control por Horario", size=16, weight="bold")], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([inicio_hora, inicio_minuto], spacing=10),
                ft.Row([fin_hora, fin_minuto], spacing=10),
                ft.Row([boton], alignment=ft.MainAxisAlignment.CENTER)
            ], spacing=20),
            padding=20,
            bgcolor="#ffffff",
            border_radius=10,
            expand=2
        )

        panel_op_control = ft.Container(
            content=ft.Row([control_op, control_op_val], spacing=10),
            padding=20,
            bgcolor="#ffffff",
            border_radius=10,
            expand=1
        )

        panel_op_luminosidad = ft.Container(
            content=ft.Row([luminosidad_op, luminosidad_op_val],
                        spacing=10, alignment=ft.MainAxisAlignment.END),
            padding=20,
            bgcolor="#ffffff",
            border_radius=10,
            expand=1
        )

        panel_mapa = ft.Container(
            content=ft.Row([mapa], spacing=10),
            bgcolor="#ffffff",
            border_radius=10,
            expand=True
        )

        main_content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Text("Iluminación inteligente de calles y zonas comunes", size=24, weight="bold"),
                        bgcolor="#ffffff",
                        padding=20,
                        border_radius=10,
                        expand=True
                    ),   
                ]),
                ft.Row([panel_mapa]),
                ft.Row([panel_op_control, panel_op_luminosidad]),
                ft.Row([control_panel_manual, control_panel_umbral, control_panel_horario],
                    vertical_alignment=ft.CrossAxisAlignment.START)
                ],
                scroll=ft.ScrollMode.ADAPTIVE,  # <--- añade esto
                expand=True
            ),
            expand=True
        )

        super().__init__(
            
            content=main_content,
            expand=True
        )
