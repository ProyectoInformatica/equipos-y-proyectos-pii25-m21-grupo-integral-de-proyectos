import flet as ft
from controllers.auth import AuthController

class LoginView:
    def __init__(self, page, on_success):
        self.page = page
        self.on_success = on_success # Función callback que recibe el usuario

        self.username = ft.TextField(label="Usuario", color="black", width=250)
        self.password = ft.TextField(label="Contraseña", color="black", password=True, can_reveal_password=True, width=250)
        self.message = ft.Text("", color="red")

    def login_action(self, e):
        user_val = self.username.value.strip()
        pass_val = self.password.value.strip()

        # Usamos el controlador real
        usuario_autenticado = AuthController.login(user_val, pass_val)

        if usuario_autenticado:
            # Login correcto: Llamamos a on_success pasando los datos del usuario
            self.on_success(usuario_autenticado)
        else:
            self.message.value = "Usuario o contraseña incorrectos"
            self.page.update()

    def build(self):
        login_panel = ft.Container(
            content=ft.Column(
                [
                    ft.Image(src="logo.png", width=100),
                    ft.Text("Iniciar sesión", size=24, weight=ft.FontWeight.BOLD, color="black"),
                    self.username,
                    self.password,
                    ft.ElevatedButton(
                        "Entrar",
                        on_click=self.login_action,
                        color="white",
                        bgcolor="black",
                        width=100,
                        height=40
                    ),
                    self.message
                ],
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            width=300,
            height=360,
            bgcolor="#ffffff",
            border_radius=10,
            padding=20,
            alignment=ft.alignment.center,
            shadow=ft.BoxShadow(blur_radius=10, color="#1A000000")
        )

        return ft.Container(
            content=login_panel,
            expand=True,
            alignment=ft.alignment.center,
            bgcolor="#dddddd" 
        )