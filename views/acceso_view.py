import flet as ft
import threading
import time
from controllers.data_controller import DataController

class AccesoView(ft.Container):
    def __init__(self, page):
        super().__init__(expand=True)
        self.page = page

        # Controles visuales iniciales
        self.icono_barrera = ft.Icon(name=ft.Icons.GARAGE, size=100, color="red")
        self.lbl_estado = ft.Text("BARRERA CERRADA", size=20, weight="bold", color="red")
        self.lbl_distancia = ft.Text("Distancia sensor: -- cm", size=16)
        
        self.columna_historial = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)

        def actualizar_datos():
            try:
                # 1. LEER ESTADO
                estado = DataController.obtener_estado_barrera()
                abierta = estado.get("barrera_abierta", False)
                distancia = estado.get("distancia_detectada", 500)
                mensaje = estado.get("mensaje", "") # Aquí vendrá "BARRERA ABIERTA"

                self.lbl_distancia.value = f"Distancia sensor: {distancia} cm"

                # 2. CAMBIAR COLOR Y TEXTO SEGÚN ESTADO
                if abierta:
                    # ESTADO ABIERTO: VERDE
                    self.icono_barrera.name = ft.Icons.GARAGE
                    self.icono_barrera.color = "green"
                    self.lbl_estado.value = mensaje  # Mostrará "🚗 BARRERA ABIERTA"
                    self.lbl_estado.color = "green"
                else:
                    # ESTADO CERRADO: ROJO
                    self.icono_barrera.name = ft.Icons.GARAGE
                    self.icono_barrera.color = "red"
                    self.lbl_estado.value = mensaje
                    self.lbl_estado.color = "red"

                # 3. ACTUALIZAR HISTORIAL
                logs = DataController.obtener_historial_accesos()
                self.columna_historial.controls.clear()
                
                if not logs:
                    self.columna_historial.controls.append(ft.Text("Sin registros", italic=True))
                else:
                    for log in logs:
                        item = ft.ListTile(
                            leading=ft.Icon(ft.Icons.CHECK_CIRCLE, color="green"),
                            title=ft.Text(log.get("tipo", "Acceso"), weight="bold"),
                            subtitle=ft.Text(f"{log.get('hora')} - {log.get('evento')}")
                        )
                        self.columna_historial.controls.append(item)

                self.page.update()
            except Exception as e:
                print(f"Error UI: {e}")

        # Hilo de refresco
        def ciclo_refresco():
            while True:
                time.sleep(0.5) # Refresco rápido para que se note al instante
                if self.page: actualizar_datos()
        
        actualizar_datos() # Primera carga inmediata
        threading.Thread(target=ciclo_refresco, daemon=True).start()

        # Layout
        panel_estado = ft.Container(
            content=ft.Column([
                ft.Text("Estado del Acceso", size=20, weight="bold"),
                ft.Container(height=20),
                self.icono_barrera,
                self.lbl_estado,
                ft.Divider(),
                self.lbl_distancia
            ], horizontal_alignment="center"),
            bgcolor="white", padding=30, border_radius=10, expand=1
        )

        panel_historial = ft.Container(
            content=ft.Column([
                ft.Text("Registro de Entradas", size=20, weight="bold"),
                ft.Divider(),
                ft.Container(content=self.columna_historial, expand=True)
            ]),
            bgcolor="white", padding=30, border_radius=10, expand=1
        )

        self.content = ft.Container(
            content=ft.Column([
                ft.Container(content=ft.Text("Control de Accesos Inteligente", size=24, weight="bold"),
                             bgcolor="#ffffff", padding=20, border_radius=10, expand=False),
                ft.Row([panel_estado, panel_historial], expand=True)
            ], spacing=20),
            padding=20
        )