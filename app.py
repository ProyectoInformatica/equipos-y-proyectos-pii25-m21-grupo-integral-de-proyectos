import flet as ft
import sys
import os

# Asegurar que la base de datos se inicialice al inicio
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
from database import get_connection  # Esto inicializa la BD automáticamente

# Inicializar la conexión (y por tanto la BD) al importar
_ = get_connection()

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
from views.crear_peticion_view import CrearPeticionView
from views.mis_peticiones_view import MisPeticionesView
from views.gestion_peticiones_view import GestionPeticionesView
from views.registrar_cliente_view import RegistrarClienteView

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

        # 2. Instanciar vistas según el rol
        if usuario["role"] == "cliente":
            # Vistas para cliente
            views = {
                "crear_peticion": lambda: CrearPeticionView(page, usuario),
                "mis_peticiones": lambda: MisPeticionesView(page, usuario)
            }
        else:
            # Vistas para admin/tecnico
            views = {
                "mapa": lambda: MapView(page), 
                "iluminacion": lambda: IluminacionView(page, usuario),
                "ambiental": lambda: AmbientalView(page, usuario),
                "emergencias": lambda: EmergenciasView(page, usuario),
                "acceso": lambda: AccesoView(page),
                "recursos": lambda: RecursosView(page),
                "dashboard": lambda: DashboardView(page),
                "notificaciones": lambda: NotificationsView(page),
                "gestion_peticiones": lambda: GestionPeticionesView(page, usuario),
                "registrar_cliente": lambda: RegistrarClienteView(page, usuario)
            }

        # 3. Controlador de navegación
        controller = NavigationController(page, content_container, views)

        # 4. Header (Sidebar lateral)
        # Estructura: Logo + Info + Menú (scrollable) + Cerrar sesión (fijo abajo)
        header = ft.Container(
            content=ft.Column(
                [
                    # LOGO (fijo arriba)
                    ft.Row([ft.Image(src="logo.png", width=120)], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Divider(height=20, color="#cccccc"),

                    # INFO USUARIO (fijo)
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"{usuario['name']}", weight="bold", size=14, text_align="center"),
                            ft.Text(f"Rol: {usuario['role'].upper()}", size=12, color="grey", text_align="center"),
                        ], horizontal_alignment="center"),
                        padding=10
                    ),
                    ft.Divider(height=10, color="#cccccc"),

                    # MENÚ (scrollable si es muy largo)
                    ft.Container(
                        content=ft.Column(
                            _crear_menu_segun_rol(usuario["role"], controller),
                            spacing=5,
                            scroll=ft.ScrollMode.AUTO
                        ),
                        expand=True
                    ),

                    # Separador
                    ft.Divider(height=20, color="#cccccc"),

                    # CERRAR SESIÓN (fijo abajo, siempre visible)
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
                expand=True,
                spacing=0
            ),
            bgcolor="#ffffff",
            border_radius=10,
            padding=20,
            margin=ft.Margin(10, 10, 0, 10),
            width=250,
        )

        main_container.content = ft.Row([header, content_container], vertical_alignment=ft.CrossAxisAlignment.START)
        
        # Ir a la vista inicial según el rol
        if usuario["role"] == "cliente":
            controller.go("crear_peticion")
        else:
            controller.go("dashboard")
        page.update()

    def _crear_boton_menu(texto, icono, vista, controller):
        return ft.Row([
            ft.Image(src=icono, width=25),
            ft.TextButton(content=ft.Text(texto, color="black"), on_click=lambda e: controller.go(vista))
        ])
    
    def _crear_menu_segun_rol(rol, controller):
        """Crea el menú según el rol del usuario"""
        if rol == "cliente":
            return [
                _crear_boton_menu("Crear Petición", "icon_notificaciones.png", "crear_peticion", controller),
                _crear_boton_menu("Mis Peticiones", "icon_notificaciones.png", "mis_peticiones", controller)
            ]
        else:
            # Menú para admin/tecnico
            menu_items = [
                _crear_boton_menu("Dashboard", "icon_dashboard.png", "dashboard", controller),
                _crear_boton_menu("Mapa de Zona", "icon_mapa.png", "mapa", controller),
                _crear_boton_menu("Control iluminación", "icon_iluminacion.png", "iluminacion", controller),
                _crear_boton_menu("Control ambiental", "icon_ambiental.png", "ambiental", controller),
                _crear_boton_menu("Gestión emergencias", "icon_emergencias.png", "emergencias", controller),
                _crear_boton_menu("Control acceso", "icon_acceso.png", "acceso", controller),
                _crear_boton_menu("Gestión recursos", "icon_recursos.png", "recursos", controller),
                _crear_boton_menu("Notificaciones", "icon_notificaciones.png", "notificaciones", controller)
            ]
            
            # Solo admin puede gestionar peticiones y registrar usuarios
            if rol == "admin":
                menu_items.append(_crear_boton_menu("Gestión Peticiones", "icon_notificaciones.png", "gestion_peticiones", controller))
                menu_items.append(_crear_boton_menu("Registrar Usuario", "icon_usuario.png", "registrar_cliente", controller))
            
            return menu_items

    def _reiniciar_login():
        # Limpiar y volver a cargar login
        main_container.content = LoginView(page, on_success=load_app).build()
        page.update()

    # Cargar login al iniciar
    _reiniciar_login()

ft.app(target=main, assets_dir="assets")