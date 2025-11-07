import flet as ft

def main(page: ft.Page):
    page.title = "Módulo de iluminación inteligente"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#f0f0f0"
    page.scroll = ft.ScrollMode.ADAPTIVE  # permite desplazarse verticalmente
    

    # Estado de luz
    light_on = ft.Switch(label="Encendido manual", value=False)
    intensidad = ft.Slider(min=0, max=100, divisions=10, label="{value}%", value=50)

    # Funciones
    def toggle_light(e):
        if light_on.value:
            light_status.value = "Luz encendida"
            light_status.color = "green"
        else:
            light_status.value = "Luz apagada"
            light_status.color = "red"
        page.update()

    def cambiar_intensidad(e):
        light_intensity.value = f"Intensidad: {int(intensidad.value)}%"
        page.update()

    light_on.on_change = toggle_light
    intensidad.on_change = cambiar_intensidad

    # Indicadores
    light_status = ft.Text("Luz apagada", color="red", weight=ft.FontWeight.BOLD)
    light_intensity = ft.Text("Intensidad: 50%", color="blue")

    # Imagen del mapa (ajustada a ancho del contenedor)
    mapa = ft.Image(
        src="mapa_iluminacion.jpg",
        width=900,  # se adapta a pantallas grandes
        height=500,
        fit=ft.ImageFit.CONTAIN,
        border_radius=10
    )

    # Panel lateral (menú)
    menu_items = [
        "Dashboard",
        "Modulo Iluminación Inteligente",
        "Mod. Control Nivel Central",
        "Mod. Control Emergencia",
        "Mod. Gestión de Recursos",
        "Config. Software",
        "Panel de Acciones",
    ]
    sidebar = ft.Container(
        bgcolor="#ffffff",
        width=220,
        padding=15,
        height=page.height,
        content=ft.Column(
            [ft.Text("⚙️ GIP", size=22, weight="bold")] +
            [ft.Text(item, size=13) for item in menu_items],
            spacing=10,
            alignment=ft.MainAxisAlignment.START,
        )
    )

    # Panel de control inferior
    control_panel = ft.Container(
        content=ft.Column([
            ft.Text("Panel de control para iluminación", size=16, weight="bold"),
            light_on,
            intensidad,
            light_status,
            light_intensity,
        ], spacing=10),
        padding=20,
        bgcolor="#ffffff",
        border_radius=10,
        width=450
    )

       
    # Esta parte del calendario hay que implementarla en otra parte del código
    # (Creo que en scheduler.py)
       # --- Calendario y horarios automáticos ---
    fecha_programada = ft.Text("Fecha no seleccionada")
    hora_programada = ft.Text("Hora no seleccionada")

    def seleccionar_fecha(e):
        fecha_programada.value = f"Fecha seleccionada: {e.control.value}"
        page.update()

    def seleccionar_hora(e):
        hora_programada.value = f"Hora seleccionada: {e.control.value}"
        page.update()

    date_picker = ft.DatePicker(on_change=seleccionar_fecha)
    time_picker = ft.TimePicker(on_change=seleccionar_hora)

    # Botones para abrir los pickers
    calendario_controls = ft.Column([
        ft.Text("Configuración de horarios automáticos", size=16, weight="bold"),
        ft.ElevatedButton("Seleccionar fecha", on_click=lambda e: date_picker.pick_date()),
        ft.ElevatedButton("Seleccionar hora", on_click=lambda e: time_picker.pick_time()),
        fecha_programada,
        hora_programada,

    ])
    # (En siguientes sprint se guardará en JSON y se ejecutará automáticamente)
    # --- Calendario y horarios automáticos ---
    fecha_programada = ft.Text("Fecha no seleccionada")
    hora_programada = ft.Text("Hora no seleccionada")

    def seleccionar_fecha(e):
        fecha_programada.value = f" Fecha seleccionada: {e.control.value}"
        page.update()

    def seleccionar_hora(e):
        hora_programada.value = f" Hora seleccionada: {e.control.value}"
        page.update()

    # Crear pickers
    date_picker = ft.DatePicker(on_change=seleccionar_fecha)
    time_picker = ft.TimePicker(on_change=seleccionar_hora)

    # Agregar los pickers a la página
    page.overlay.append(date_picker)
    page.overlay.append(time_picker)

    # Botones para abrirlos
    calendario_controls = ft.Column([
        ft.Text("Configuración de horarios automáticos", size=16, weight="bold"),
        ft.ElevatedButton("Seleccionar fecha", on_click=lambda e: page.open(date_picker)),
        ft.ElevatedButton("Seleccionar hora", on_click=lambda e: page.open(time_picker)),
        fecha_programada,
        hora_programada,
    ])

    calendario = ft.Container(
        bgcolor="#ffffff",
        padding=20,
        border_radius=10,
        width=400,
        content=calendario_controls
    )
    # (Versión básica: solo muestra la selección, no guarda todavía)
    # Esta parte del calendario hay que implementarla en otra parte del código
    # Fila inferior con scroll si es necesario
    bottom_row = ft.ResponsiveRow([
        ft.Container(control_panel, col={"xs": 12, "md": 6}),
        ft.Container(calendario, col={"xs": 12, "md": 6}),
    ], spacing=20)

    # Contenido principal desplazable
    main_content = ft.Container(
        content=ft.Column([
            ft.Text("Módulo de iluminación inteligente", size=24, weight="bold"),
            mapa,
            bottom_row
        ], spacing=20, scroll=ft.ScrollMode.AUTO),
        expand=True,
        padding=30,
    )

    # Layout general con menú fijo a la izquierda
    layout = ft.Row(
        [sidebar, main_content],
        spacing=10,
        expand=True,
    )

    page.add(layout)

ft.app(target=main, view=ft.AppView.WEB_BROWSER, assets_dir=".")
