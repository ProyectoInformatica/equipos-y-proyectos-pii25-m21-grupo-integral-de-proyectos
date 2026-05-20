import flet as ft
from controllers.peticiones_controller import PeticionesController

class CrearPeticionView(ft.Container):
    def __init__(self, page, usuario):
        super().__init__(expand=True, padding=20)
        self.page = page
        self.usuario = usuario
        
        # Campos del formulario
        self.titulo_field = ft.TextField(
            label="Título de la petición",
            hint_text="Ej: Problema con la iluminación",
            width=600,
            max_length=100
        )
        
        self.descripcion_field = ft.TextField(
            label="Descripción",
            hint_text="Describe tu petición o problema en detalle...",
            width=600,
            multiline=True,
            min_lines=5,
            max_lines=10,
            max_length=1000
        )
        
        self.mensaje = ft.Text("", color="red", size=12)
        self.mensaje_exito = ft.Text("", color="green", size=12)
        
        # Botón de envío
        def enviar_peticion(e):
            titulo = self.titulo_field.value.strip()
            descripcion = self.descripcion_field.value.strip()
            
            # Usar controlador para crear petición (incluye validaciones)
            resultado = PeticionesController.crear_peticion(
                usuario_id=self.usuario["id"],
                titulo=titulo,
                descripcion=descripcion
            )
            
            if not resultado["success"]:
                self.mensaje.value = resultado["message"]
                self.mensaje_exito.value = ""
                page.update()
                return
            
            # Éxito
            request_id = resultado.get("request_id", 0)
            self.mensaje.value = ""
            self.mensaje_exito.value = f"✓ Petición enviada correctamente (ID: {request_id})"
            # Limpiar campos
            self.titulo_field.value = ""
            self.descripcion_field.value = ""
            page.update()
            
            # Mostrar snackbar
            page.snack_bar = ft.SnackBar(
                ft.Text("Petición enviada correctamente"),
                bgcolor="green"
            )
            page.snack_bar.open = True
            page.update()
        
        btn_enviar = ft.ElevatedButton(
            "Enviar Petición",
            on_click=enviar_peticion,
            bgcolor="blue",
            color="white",
            width=200,
            height=40
        )
        
        # Layout
        self.content = ft.Column(
            [
                ft.Container(
                    content=ft.Text("Crear Nueva Petición", size=28, weight="bold"),
                    padding=20,
                    bgcolor="#ffffff",
                    border_radius=10,
                    width=float("inf")
                ),
                ft.Container(height=20),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Completa el formulario para enviar tu petición:", size=16),
                            ft.Container(height=10),
                            self.titulo_field,
                            ft.Container(height=10),
                            self.descripcion_field,
                            ft.Container(height=10),
                            ft.Row([btn_enviar], alignment=ft.MainAxisAlignment.CENTER),
                            self.mensaje,
                            self.mensaje_exito
                        ],
                        spacing=10
                    ),
                    padding=30,
                    bgcolor="#ffffff",
                    border_radius=10,
                    width=float("inf")
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=0
        )
