import flet as ft
import threading
import time
from controllers.data_controller import DataController

class AccesoView(ft.Container):
    def __init__(self, page):
        super().__init__(expand=True)
        self.page = page

        # CONTROLES VISUALES 
        # Icono inicial (Cerrado)
        self.icono_barrera = ft.Icon(name=ft.Icons.GARAGE, size=100, color="red")
        self.lbl_estado = ft.Text("BARRERA CERRADA", size=20, weight="bold", color="red")
        self.lbl_distancia = ft.Text("Distancia sensor: -- cm", size=16)
        
        self.columna_historial = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)

        # CONTROLES MANUALES 
        estado_manual = DataController.obtener_manual_barrera()
        
        self.switch_manual = ft.Switch(
            label="Activar Control Manual", 
            value=estado_manual.get("modo_manual", False),
            active_color="blue"
        )
        self.switch_abrir = ft.Switch(
            label="Mantener Barrera Abierta", 
            value=estado_manual.get("abrir", False),
            disabled=not self.switch_manual.value,
            active_color="green"
        )

        # EVENTOS 
        def guardar_estado_manual(e):
            self.switch_abrir.disabled = not self.switch_manual.value
            
            if not self.switch_manual.value:
                self.switch_abrir.value = False
            
            DataController.guardar_manual_barrera(
                self.switch_manual.value, 
                self.switch_abrir.value
            )
            self.page.update()

        self.switch_manual.on_change = guardar_estado_manual
        self.switch_abrir.on_change = guardar_estado_manual

        # LÓGICA DE ACTUALIZACIÓN DE DATOS
        def actualizar_datos():
            try:
                # 1. ESTADO DE BARRERA
                estado = DataController.obtener_estado_barrera()
                abierta = estado.get("barrera_abierta", False)
                distancia = estado.get("distancia_detectada", 500)
                mensaje = estado.get("mensaje", "")

                self.lbl_distancia.value = f"Distancia sensor: {distancia} cm"

                if abierta:
                    # Icono Coche pasando (Verde)
                    self.icono_barrera.name = ft.Icons.DIRECTIONS_CAR 
                    self.icono_barrera.color = "green"
                    self.lbl_estado.value = mensaje
                    self.lbl_estado.color = "green"
                else:
                    # Icono Garaje cerrado (Rojo)
                    self.icono_barrera.name = ft.Icons.GARAGE
                    self.icono_barrera.color = "red"
                    
                    if self.switch_manual.value and not abierta:
                        self.lbl_estado.value = "MANUAL: CERRADA"
                    else:
                        self.lbl_estado.value = mensaje
                    self.lbl_estado.color = "red"

                # 2. HISTORIAL
                logs = DataController.obtener_historial_accesos()
                self.columna_historial.controls.clear()
                
                if not logs:
                    self.columna_historial.controls.append(ft.Text("Sin registros", italic=True))
                else:
                    for log in logs:
                        icon = ft.Icons.CHECK_CIRCLE
                        color = "green"
                        if log.get("tipo") == "Apertura Manual":
                            icon = ft.Icons.ADMIN_PANEL_SETTINGS
                            color = "blue"
                            
                        item = ft.ListTile(
                            leading=ft.Icon(icon, color=color),
                            title=ft.Text(log.get("tipo", "Acceso"), weight="bold"),
                            subtitle=ft.Text(f"{log.get('hora')} - {log.get('evento')}")
                        )
                        self.columna_historial.controls.append(item)

                self.page.update()
            except Exception as e:
                print(f"Error UI: {e}")

        def ciclo_refresco():
            while True:
                time.sleep(0.5)
                if self.page: actualizar_datos()
        
        # Carga inicial inmediata
        actualizar_datos()
        threading.Thread(target=ciclo_refresco, daemon=True).start()

        # LAYOUT 
        panel_estado = ft.Container(
            content=ft.Column([
                ft.Text("Estado del Acceso", size=20, weight="bold"),
                ft.Container(height=20),
                self.icono_barrera,
                self.lbl_estado,
                ft.Divider(),
                self.lbl_distancia,
                ft.Divider(),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Panel de Operador", weight="bold"),
                        self.switch_manual,
                        self.switch_abrir,
                        ft.Text("(Activa ambos para abrir)", size=12, italic=True, color="grey")
                    ]),
                    bgcolor="#f0f2f5", padding=10, border_radius=10
                )
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
                ft.Row([
                    ft.Container(content=ft.Text("Control de Accesos Inteligente", size=24, weight="bold"),
                                 bgcolor="#ffffff", padding=20, border_radius=10, expand=True),
                ]),
                ft.Row([panel_estado, panel_historial], expand=True)
            ], spacing=20),
            padding=20
        )