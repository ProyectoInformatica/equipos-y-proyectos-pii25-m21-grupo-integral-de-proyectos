import flet as ft

class DashboardView(ft.Container):
    def __init__(self, page):
        super().__init__(
            content=ft.Column(
                [
                    ft.Text("Bienvenido al Dashboard", size=28),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            expand=True
        )
