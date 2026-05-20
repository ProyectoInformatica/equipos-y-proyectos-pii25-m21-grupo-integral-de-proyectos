import flet as ft
from controllers.peticiones_controller import PeticionesController
from datetime import datetime

class MisPeticionesView(ft.Container):
    def __init__(self, page, usuario):
        super().__init__(expand=True, padding=20)
        self.page = page
        self.usuario = usuario
        
        # Contenedor para la lista de peticiones
        self.peticiones_container = ft.Column(
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
        
        # Título con botón de actualizar
        self.titulo = ft.Container(
            content=ft.Row(
                [
                    ft.Text("Mis Peticiones", size=28, weight="bold", expand=True),
                    ft.ElevatedButton(
                        "Actualizar",
                        icon=ft.Icons.REFRESH,
                        on_click=lambda e: self.cargar_peticiones(),
                        bgcolor="blue",
                        color="white"
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=20,
            bgcolor="#ffffff",
            border_radius=10,
            width=float("inf")
        )
        
        # Contenedor principal
        self.content = ft.Column(
            [
                self.titulo,
                ft.Container(height=20),
                ft.Container(
                    content=self.peticiones_container,
                    padding=20,
                    bgcolor="#ffffff",
                    border_radius=10,
                    expand=True
                )
            ],
            spacing=0,
            expand=True
        )
        
        # Cargar peticiones al iniciar
        self.cargar_peticiones()
    
    def cargar_peticiones(self):
        """Carga las peticiones del cliente desde la base de datos"""
        self.peticiones_container.controls.clear()
        
        try:
            peticiones = PeticionesController.obtener_peticiones_cliente(self.usuario["id"])
            
            if not peticiones:
                self.peticiones_container.controls.append(
                    ft.Container(
                        content=ft.Text(
                            "No tienes peticiones enviadas aún.",
                            size=16,
                            color="grey",
                            text_align="center"
                        ),
                        padding=40,
                        alignment=ft.alignment.center
                    )
                )
            else:
                for peticion in peticiones:
                    # Determinar color según estado
                    estado_color = {
                        "Pendiente": "orange",
                        "En proceso": "blue",
                        "Resuelta": "green"
                    }.get(peticion["estado"], "grey")
                    
                    # Formatear fecha
                    try:
                        fecha_obj = datetime.strptime(peticion["timestamp"], "%Y-%m-%d %H:%M:%S")
                        fecha_formateada = fecha_obj.strftime("%d/%m/%Y %H:%M")
                    except:
                        fecha_formateada = peticion["timestamp"]
                    
                    # Crear tarjeta de petición
                    tarjeta = ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text(
                                            peticion["titulo"],
                                            size=18,
                                            weight="bold",
                                            expand=True
                                        ),
                                        ft.Container(
                                            content=ft.Text(
                                                peticion["estado"],
                                                size=12,
                                                weight="bold",
                                                color="white"
                                            ),
                                            bgcolor=estado_color,
                                            padding=ft.Padding(8, 4, 8, 4),
                                            border_radius=5
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                ),
                                ft.Divider(height=10, color="transparent"),
                                ft.Text(
                                    peticion["descripcion"],
                                    size=14,
                                    color="grey700"
                                ),
                                ft.Divider(height=10, color="transparent"),
                                ft.Row(
                                    [
                                        ft.Text(
                                            f"Enviada: {fecha_formateada}",
                                            size=12,
                                            color="grey",
                                            italic=True
                                        ),
                                        ft.Container(expand=True),
                                        ft.Text(
                                            f"ID: {peticion['id']}",
                                            size=12,
                                            color="grey",
                                            italic=True
                                        )
                                    ]
                                )
                            ],
                            spacing=5
                        ),
                        padding=20,
                        bgcolor="#f5f5f5",
                        border_radius=10,
                        border=ft.border.all(1, "#e0e0e0")
                    )
                    
                    self.peticiones_container.controls.append(tarjeta)
            
            self.page.update()
        except Exception as e:
            self.peticiones_container.controls.append(
                ft.Container(
                    content=ft.Text(
                        f"Error al cargar peticiones: {str(e)}",
                        size=14,
                        color="red"
                    ),
                    padding=20
                )
            )
            self.page.update()
