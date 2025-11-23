import flet as ft

class AccesoView(ft.Container):
    def __init__(self, page):
        super().__init__(
            content=ft.Column(
                [
                    ft.Text("Bienvenido al Control Acceso", size=28),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            expand=True
        )
