import flet as ft

class LoginView:
    def __init__(self, page, on_success):
        self.page = page
        self.on_success = on_success

        self.username = ft.TextField(label="Usuario", color="black", width=250)
        self.password = ft.TextField(label="Contraseña", color="black", password=True, can_reveal_password=True, width=250)
        self.message = ft.Text("", color="red")

    def login_action(self, e):
        user = self.username.value.strip()
        pwd = self.password.value.strip()
        if user == "admin" and pwd == "1234":
            self.on_success()
        else:
            self.message.value = "❌ Usuario o contraseña incorrectos"
            self.page.update()

    def build(self):
        # Contenedor fijo de 300px
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
            height=330,               # altura fija
            bgcolor="#ffffff",
            border_radius=10,
            padding=20,
            alignment=ft.alignment.center  # centra el contenido dentro del container
        )

        # Contenedor padre que ocupa toda la pantalla, para centrar vertical y horizontalmente
        return ft.Container(
            content=login_panel,
            expand=True,               # ocupa toda la pantalla
            alignment=ft.alignment.center
        )
