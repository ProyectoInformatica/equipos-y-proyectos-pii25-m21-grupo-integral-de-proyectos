import flet as ft
from controllers.peticiones_controller import PeticionesController
from datetime import datetime

class GestionPeticionesView(ft.Container):
    def __init__(self, page, usuario):
        super().__init__(expand=True, padding=20)
        self.page = page
        self.usuario = usuario
        
        # Filtro de estado
        self.filtro_estado = ft.Dropdown(
            label="Filtrar por estado",
            options=[
                ft.dropdown.Option("Todos"),
                ft.dropdown.Option("Pendiente"),
                ft.dropdown.Option("En proceso"),
                ft.dropdown.Option("Resuelta")
            ],
            value="Todos",
            width=200,
            on_change=lambda e: self.cargar_peticiones()
        )
        
        # Contenedor para la lista de peticiones
        self.peticiones_container = ft.Column(
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
        
        # Título y controles
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Text("Gestión de Peticiones de Clientes", size=28, weight="bold"),
                    ft.Container(expand=True),
                    self.filtro_estado,
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
                header,
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
        """Carga todas las peticiones de clientes desde la base de datos"""
        self.peticiones_container.controls.clear()
        
        try:
            todas_peticiones = PeticionesController.obtener_todas_peticiones()
            
            # Aplicar filtro
            filtro = self.filtro_estado.value
            if filtro and filtro != "Todos":
                peticiones = [p for p in todas_peticiones if p["estado"] == filtro]
            else:
                peticiones = todas_peticiones
            
            if not peticiones:
                self.peticiones_container.controls.append(
                    ft.Container(
                        content=ft.Text(
                            "No hay peticiones" + (f" con estado '{filtro}'" if filtro != "Todos" else ""),
                            size=16,
                            color="grey",
                            text_align="center"
                        ),
                        padding=40,
                        alignment=ft.alignment.center
                    )
                )
            else:
                # Mostrar contador
                self.peticiones_container.controls.append(
                    ft.Container(
                        content=ft.Text(
                            f"Total: {len(peticiones)} petición(es)" + (f" - Estado: {filtro}" if filtro != "Todos" else ""),
                            size=14,
                            color="grey",
                            weight="bold"
                        ),
                        padding=ft.Padding(0, 0, 0, 10)
                    )
                )
                
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
                    
                    # Dropdown para cambiar estado
                    estado_dropdown = ft.Dropdown(
                        value=peticion["estado"],
                        options=[
                            ft.dropdown.Option("Pendiente"),
                            ft.dropdown.Option("En proceso"),
                            ft.dropdown.Option("Resuelta")
                        ],
                        width=150,
                        on_change=lambda e, p_id=peticion["id"]: self.cambiar_estado(p_id, e.control.value)
                    )
                    
                    # Crear tarjeta de petición
                    tarjeta = ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Column(
                                            [
                                                ft.Text(
                                                    peticion["titulo"],
                                                    size=18,
                                                    weight="bold",
                                                    expand=True
                                                ),
                                                ft.Text(
                                                    f"Cliente: {peticion.get('nombre_usuario', peticion.get('usuario', 'N/A'))} ({peticion.get('usuario', 'N/A')})",
                                                    size=12,
                                                    color="grey600"
                                                )
                                            ],
                                            expand=True
                                        ),
                                        ft.Container(
                                            content=ft.Column(
                                                [
                                                    ft.Text("Estado:", size=12, color="grey"),
                                                    estado_dropdown
                                                ],
                                                spacing=5,
                                                horizontal_alignment=ft.CrossAxisAlignment.END
                                            )
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
            print(f"Error en gestion_peticiones_view: {e}")
    
    def cambiar_estado(self, request_id: int, nuevo_estado: str):
        """Cambia el estado de una petición"""
        try:
            resultado = PeticionesController.actualizar_estado(request_id, nuevo_estado)
            if resultado["success"]:
                # Mostrar mensaje de éxito
                self.page.snack_bar = ft.SnackBar(
                    ft.Text(f"Estado actualizado a: {nuevo_estado}"),
                    bgcolor="green"
                )
                self.page.snack_bar.open = True
                
                # Recargar peticiones
                self.cargar_peticiones()
            else:
                self.page.snack_bar = ft.SnackBar(
                    ft.Text(resultado["message"]),
                    bgcolor="red"
                )
                self.page.snack_bar.open = True
                self.page.update()
        except Exception as e:
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"Error: {str(e)}"),
                bgcolor="red"
            )
            self.page.snack_bar.open = True
            self.page.update()
            print(f"Error cambiando estado: {e}")
