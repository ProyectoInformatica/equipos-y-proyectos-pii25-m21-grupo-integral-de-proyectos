import flet as ft

from controllers.navigation_controller import NavigationController

from views.login_view import LoginView
from views.iluminacion_view import IluminacionView
from views.ambiental_view import AmbientalView
from views.emergencias_view import EmergenciasView
from views.acceso_view import AccesoView
from views.recursos_view import RecursosView
from views.dashboard_view import DashboardView
from views.notifications_view import NotificationsView
from views.map_view import MapView

def main(page: ft.Page):
    page.window.maximized = True
    page.window_icon = "icono.ico"
    page.title = "Grupo Integral de Proyectos"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = "#dddddd"

    # Contenedor principal
    main_container = ft.Container(expand=True)
    page.add(main_container)

    # Función para cargar la app tras login
    # RECIBE EL OBJETO USUARIO
    def load_app(usuario):
        
        # 1. Contenedor de vistas
        content_container = ft.Container(
            expand=True,
            border_radius=10,
            margin=ft.Margin(0, 10, 10, 10) 
        )

        # 2. Instanciar vistas
        views = {
            "mapa": MapView(page), 
            "iluminacion": IluminacionView(page),
            "ambiental": AmbientalView(page),
            "emergencias": EmergenciasView(page),
            "acceso": AccesoView(page),
            "recursos": RecursosView(page),
            "dashboard": DashboardView(page),
            "notificaciones": NotificationsView(page)
        }

        # 3. Controlador de navegación
        controller = NavigationController(page, content_container, views)

        # 4. Header (Sidebar lateral)
        header = ft.Container(
            content=ft.Column(
                [
                    # LOGO
                    ft.Row([ft.Image(src="logo.png", width=120)], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Divider(height=20, color="#cccccc"),

                    # INFO USUARIO (NUEVO)
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"{usuario['name']}", weight="bold", size=14, text_align="center"),
                            ft.Text(f"Rol: {usuario['role'].upper()}", size=12, color="grey", text_align="center"),
                        ], horizontal_alignment="center"),
                        padding=10
                    ),
                    ft.Divider(height=10, color="#cccccc"),

                    # MENÚ
                    ft.Column(
                        [
                            _crear_boton_menu("Dashboard", "icon_dashboard.png", "dashboard", controller),
                            _crear_boton_menu("Mapa de Zona", "icon_mapa.png", "mapa", controller),
                            _crear_boton_menu("Control iluminación", "icon_iluminacion.png", "iluminacion", controller),
                            _crear_boton_menu("Control ambiental", "icon_ambiental.png", "ambiental", controller),
                            _crear_boton_menu("Gestión emergencias", "icon_emergencias.png", "emergencias", controller),
                            _crear_boton_menu("Control acceso", "icon_acceso.png", "acceso", controller),
                            _crear_boton_menu("Gestión recursos", "icon_recursos.png", "recursos", controller),
                            _crear_boton_menu("Notificaciones", "icon_notificaciones.png", "notificaciones", controller)
                        ],
                        spacing=5
                    ),

                    ft.Container(expand=True),
                    ft.Divider(height=20, color="#cccccc"),

                    # CERRAR SESIÓN (Recargar página simulado)
                    ft.Row(
                        [
                            ft.Image(src="icon_usuario.png", width=25),
                            ft.TextButton(
                                content=ft.Text("Cerrar sesión", color="black"),
                                on_click=lambda e: _reiniciar_login()
                            )
                        ],
                        alignment=ft.MainAxisAlignment.START
                    )
                ],
                expand=True
            ),
            bgcolor="#ffffff",
            border_radius=10,
            padding=20,
            margin=ft.Margin(10, 10, 0, 10),
            width=250,
        )

        main_container.content = ft.Row([header, content_container], vertical_alignment=ft.CrossAxisAlignment.START)
        controller.go("dashboard")
        page.update()

    def _crear_boton_menu(texto, icono, vista, controller):
        return ft.Row([
            ft.Image(src=icono, width=25),
            ft.TextButton(content=ft.Text(texto, color="black"), on_click=lambda e: controller.go(vista))
        ])

    def _reiniciar_login():
        # Limpiar y volver a cargar login
        main_container.content = LoginView(page, on_success=load_app).build()
        page.update()

    # Cargar login al iniciar
    _reiniciar_login()

ft.app(target=main, assets_dir="assets")