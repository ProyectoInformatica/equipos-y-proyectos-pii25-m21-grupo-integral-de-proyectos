import flet as ft
from controllers.usuarios_controller import UsuariosController

class RegistrarClienteView(ft.Container):
    def __init__(self, page, usuario):
        super().__init__(expand=True, padding=20)
        self.page = page
        self.usuario = usuario
        
        # Campos del formulario
        self.username_field = ft.TextField(
            label="Nombre de usuario",
            hint_text="Ej: cliente3",
            width=400,
            max_length=50,
            autofocus=True
        )
        
        self.password_field = ft.TextField(
            label="Contraseña",
            hint_text="Mínimo 4 caracteres",
            width=400,
            password=True,
            can_reveal_password=True,
            max_length=100
        )
        
        self.name_field = ft.TextField(
            label="Nombre completo",
            hint_text="Ej: Juan Pérez",
            width=400,
            max_length=100
        )
        
        self.role_field = ft.Dropdown(
            label="Rol",
            options=[
                ft.dropdown.Option("cliente", "Cliente"),
                ft.dropdown.Option("tecnico", "Técnico"),
                ft.dropdown.Option("admin", "Administrador")
            ],
            value="cliente",
            width=400
        )
        
        self.mensaje = ft.Text("", color="red", size=12)
        self.mensaje_exito = ft.Text("", color="green", size=12)
        
        # Botón de registro
        def registrar_usuario(e):
            username = self.username_field.value.strip()
            password = self.password_field.value.strip()
            name = self.name_field.value.strip()
            role = self.role_field.value
            
            # Validar campos
            if not username:
                self.mensaje.value = "Por favor, ingresa un nombre de usuario"
                self.mensaje_exito.value = ""
                page.update()
                return
            
            if not password:
                self.mensaje.value = "Por favor, ingresa una contraseña"
                self.mensaje_exito.value = ""
                page.update()
                return
            
            if len(password) < 4:
                self.mensaje.value = "La contraseña debe tener al menos 4 caracteres"
                self.mensaje_exito.value = ""
                page.update()
                return
            
            if not name:
                self.mensaje.value = "Por favor, ingresa un nombre completo"
                self.mensaje_exito.value = ""
                page.update()
                return
            
            if not role:
                self.mensaje.value = "Por favor, selecciona un rol"
                self.mensaje_exito.value = ""
                page.update()
                return
            
            # Crear usuario usando controlador
            try:
                resultado = UsuariosController.registrar_usuario(username, password, role, name)
                
                if resultado["success"]:
                    self.mensaje.value = ""
                    self.mensaje_exito.value = f"✓ {resultado['message']}"
                    # Limpiar campos
                    self.username_field.value = ""
                    self.password_field.value = ""
                    self.name_field.value = ""
                    self.role_field.value = "cliente"
                    page.update()
                    
                    # Mostrar snackbar
                    page.snack_bar = ft.SnackBar(
                        ft.Text(resultado["message"]),
                        bgcolor="green"
                    )
                    page.snack_bar.open = True
                    page.update()
                    
                    # Actualizar lista de usuarios
                    self.actualizar_lista_usuarios()
                else:
                    self.mensaje.value = resultado["message"]
                    self.mensaje_exito.value = ""
                    page.update()
            except Exception as ex:
                self.mensaje.value = f"Error: {str(ex)}"
                self.mensaje_exito.value = ""
                page.update()
        
        btn_registrar = ft.ElevatedButton(
            "Registrar Usuario",
            on_click=registrar_usuario,
            bgcolor="blue",
            color="white",
            width=200,
            height=40
        )
        
        # Lista de usuarios existentes
        self.lista_usuarios = ft.Column(
            spacing=5,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
        
        # Layout
        self.content = ft.Column(
            [
                # Título
                ft.Container(
                    content=ft.Text("Registrar Nuevo Usuario", size=28, weight="bold"),
                    padding=20,
                    bgcolor="#ffffff",
                    border_radius=10,
                    width=float("inf")
                ),
                ft.Container(height=20),
                
                # Formulario y lista en dos columnas
                ft.Row(
                    [
                        # Formulario
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Completa el formulario para registrar un nuevo usuario:", size=16),
                                    ft.Container(height=10),
                                    self.username_field,
                                    ft.Container(height=10),
                                    self.password_field,
                                    ft.Container(height=10),
                                    self.name_field,
                                    ft.Container(height=10),
                                    self.role_field,
                                    ft.Container(height=10),
                                    ft.Row([btn_registrar], alignment=ft.MainAxisAlignment.CENTER),
                                    self.mensaje,
                                    self.mensaje_exito
                                ],
                                spacing=10
                            ),
                            padding=30,
                            bgcolor="#ffffff",
                            border_radius=10,
                            width=450
                        ),
                        
                        # Lista de usuarios
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Usuarios Registrados", size=18, weight="bold"),
                                    ft.Container(height=10),
                                    self.lista_usuarios
                                ],
                                spacing=10
                            ),
                            padding=20,
                            bgcolor="#ffffff",
                            border_radius=10,
                            expand=True
                        )
                    ],
                    spacing=20,
                    expand=True
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
            expand=True
        )
        
        # Cargar lista de usuarios al iniciar
        self.actualizar_lista_usuarios()
    
    def actualizar_lista_usuarios(self):
        """Actualiza la lista de usuarios registrados"""
        self.lista_usuarios.controls.clear()
        
        try:
            usuarios = UsuariosController.obtener_todos_usuarios()
            
            if not usuarios:
                self.lista_usuarios.controls.append(
                    ft.Text("No hay usuarios registrados", size=14, color="grey")
                )
            else:
                # Agrupar por rol
                usuarios_por_rol = {}
                for usuario in usuarios:
                    rol = usuario.get("role", "sin_rol")
                    if rol not in usuarios_por_rol:
                        usuarios_por_rol[rol] = []
                    usuarios_por_rol[rol].append(usuario)
                
                # Mostrar por rol
                for rol in ["admin", "tecnico", "cliente"]:
                    if rol in usuarios_por_rol:
                        # Título del rol
                        rol_nombre = {
                            "admin": "Administradores",
                            "tecnico": "Técnicos",
                            "cliente": "Clientes"
                        }.get(rol, rol.capitalize())
                        
                        self.lista_usuarios.controls.append(
                            ft.Container(
                                content=ft.Text(
                                    rol_nombre,
                                    size=16,
                                    weight="bold",
                                    color="grey700"
                                ),
                                padding=ft.Padding(0, 10, 0, 5)
                            )
                        )
                        
                        # Usuarios de este rol
                        for usuario in usuarios_por_rol[rol]:
                            tarjeta = ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text(
                                            usuario.get("name", "Sin nombre"),
                                            size=14,
                                            weight="bold"
                                        ),
                                        ft.Text(
                                            f"Usuario: {usuario.get('username', 'N/A')}",
                                            size=12,
                                            color="grey600"
                                        )
                                    ],
                                    spacing=5
                                ),
                                padding=10,
                                bgcolor="#f5f5f5",
                                border_radius=5,
                                border=ft.border.all(1, "#e0e0e0")
                            )
                            self.lista_usuarios.controls.append(tarjeta)
                        
                        self.lista_usuarios.controls.append(
                            ft.Container(height=10)
                        )
            
            self.page.update()
        except Exception as e:
            self.lista_usuarios.controls.append(
                ft.Text(
                    f"Error al cargar usuarios: {str(e)}",
                    size=14,
                    color="red"
                )
            )
            self.page.update()
