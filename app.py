import flet as ft

from controllers.navigation_controller import NavigationController

from views.login_view import LoginView
from views.iluminacion_view import IluminacionView
from views.ambiental_view import AmbientalView
from views.emergencias_view import EmergenciasView
from views.acceso_view import AccesoView
from views.recursos_view import RecursosView
from views.dashboard_view import DashboardView

def main(page: ft.Page):
    page.window.maximized = True
    page.window_icon = "icono.ico"
    page.title = "Grupo Integral de Proyectos"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = "#dddddd"

    # Contenedor principal donde se mostrará login o la app
    main_container = ft.Container(expand=True)
    page.add(main_container)

    # --- función para cargar la app tras login ---
    def load_app():
        # 1. Crear contenedor donde se cargan las vistas internas
        content_container = ft.Container(
            expand=True,
            #bgcolor="#ffffff",
            border_radius=10,
            margin=ft.Margin(0, 10, 10, 10) 
        )

        # 2. Instanciar vistas
        views = {
            "iluminacion": IluminacionView(page),
            "ambiental":AmbientalView(page),
            "emergencias":EmergenciasView(page),
            "acceso":AccesoView(page),
            "recursos":RecursosView(page),
            "dashboard":DashboardView(page)
        }

        # 3. Controlador de navegación
        controller = NavigationController(page, content_container, views)

        # 4. Header
        header = ft.Container(
            content=ft.Column(
                [
                    # ────────────── LOGO ──────────────
                    ft.Row(
                        [ft.Image(src="logo.png", width=120)],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),

                    # ────────────── DIVISOR ──────────────
                    ft.Divider(height=20, color="#cccccc"),

                    # ────────────── MENÚ SUPERIOR ──────────────
                    ft.Column(
                        [
                            ft.Row([
                                ft.Image(src="icon_dashboard.png", width=25),
                                ft.TextButton(
                                    content=ft.Text("Dashboard", color="black"),
                                    on_click=lambda e: controller.go("dashboard")
                                )
                            ]),
                            ft.Row([
                                ft.Image(src="icon_iluminacion.png", width=25),
                                ft.TextButton(
                                    content=ft.Text("Control iluminación", color="black"),
                                    on_click=lambda e: controller.go("iluminacion")
                                )
                            ]),
                            ft.Row([
                                ft.Image(src="icon_ambiental.png", width=25),
                                ft.TextButton(
                                    content=ft.Text("Control ambiental", color="black"),
                                    on_click=lambda e: controller.go("ambiental")
                                )
                            ]),
                            ft.Row([
                                ft.Image(src="icon_emergencias.png", width=25),
                                ft.TextButton(
                                    content=ft.Text("Gestión emergencias", color="black"),
                                    on_click=lambda e: controller.go("emergencias")
                                )
                            ]),
                            ft.Row([
                                ft.Image(src="icon_acceso.png", width=25),
                                ft.TextButton(
                                    content=ft.Text("Control acceso", color="black"),
                                    on_click=lambda e: controller.go("acceso")
                                )
                            ]),
                            ft.Row([
                                ft.Image(src="icon_recursos.png", width=25),
                                ft.TextButton(
                                    content=ft.Text("Gestión recursos", color="black"),
                                    on_click=lambda e: controller.go("recursos")
                                )
                            ]),
                        ],
                        spacing=10
                    ),

                    # Esto empuja el botón hacia abajo
                    ft.Container(expand=True),

                    # ────────────── DIVISOR ──────────────
                    ft.Divider(height=20, color="#cccccc"),

                    # ────────────── BOTÓN CERRAR SESIÓN ──────────────
                    ft.Row(
                        [
                            ft.Image(src="icon_usuario.png", width=25),
                            ft.TextButton(
                                content=ft.Text("Cerrar sesión", color="black"),
                                on_click=lambda e: controller.confirm_exit()
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


        # 5. Reemplazar login con la app
        main_container.content = ft.Row([
            header,
            content_container
        ],vertical_alignment=ft.CrossAxisAlignment.START)

        controller.go("dashboard")
        page.update()

    # --- cargar login al iniciar ---
    login_view = LoginView(page, on_success=load_app)
    main_container.content = login_view.build()
    page.update()

ft.app(target=main, assets_dir="assets")