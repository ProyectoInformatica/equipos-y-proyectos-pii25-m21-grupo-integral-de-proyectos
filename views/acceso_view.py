import flet as ft
import requests
import threading
import time
from controllers.data_controller import DataController

class AccesoView(ft.Container):
    def __init__(self, page):
        super().__init__(expand=True)
        self.page = page
        self.activo = True

        # CONTROLES VISUALES 
        # Icono inicial (Cerrado)
        self.icono_barrera = ft.Icon(name=ft.Icons.GARAGE, size=100, color="red")
        self.lbl_estado = ft.Text("BARRERA CERRADA", size=20, weight="bold", color="red")
        self.lbl_distancia = ft.Text("Distancia sensor: -- cm", size=16)
        
        self.columna_historial = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        self.lbl_contador_historial = ft.Text("", size=12, color="grey600", italic=True)

        # CONTROLES MANUALES NORTE
        estado_manual_norte = DataController.obtener_manual_barrera("norte")
        
        self.switch_manual_norte = ft.Switch(
            label="Activar Control Manual", 
            value=estado_manual_norte.get("modo_manual", False),
            active_color="blue"
        )
        self.switch_abrir_norte = ft.Switch(
            label="Mantener Barrera Abierta", 
            value=estado_manual_norte.get("abrir", False),
            disabled=not self.switch_manual_norte.value,
            active_color="green"
        )

        # EVENTOS NORTE
        def guardar_estado_manual_norte(e):
            self.switch_abrir_norte.disabled = not self.switch_manual_norte.value
            
            if not self.switch_manual_norte.value:
                self.switch_abrir_norte.value = False
            
            DataController.guardar_manual_barrera(
                "norte",
                self.switch_manual_norte.value, 
                self.switch_abrir_norte.value
            )
            self.page.update()

        self.switch_manual_norte.on_change = guardar_estado_manual_norte
        self.switch_abrir_norte.on_change = guardar_estado_manual_norte

        # CONTROLES MANUALES SUR
        estado_manual_sur = DataController.obtener_manual_barrera("sur")
        
        self.switch_manual_sur = ft.Switch(
            label="Activar Control Manual", 
            value=estado_manual_sur.get("modo_manual", False),
            active_color="blue"
        )
        self.switch_abrir_sur = ft.Switch(
            label="Mantener Barrera Abierta", 
            value=estado_manual_sur.get("abrir", False),
            disabled=not self.switch_manual_sur.value,
            active_color="green"
        )

        # EVENTOS SUR
        def guardar_estado_manual_sur(e):
            self.switch_abrir_sur.disabled = not self.switch_manual_sur.value
            
            if not self.switch_manual_sur.value:
                self.switch_abrir_sur.value = False
            
            DataController.guardar_manual_barrera(
                "sur",
                self.switch_manual_sur.value, 
                self.switch_abrir_sur.value
            )
            self.page.update()

        self.switch_manual_sur.on_change = guardar_estado_manual_sur
        self.switch_abrir_sur.on_change = guardar_estado_manual_sur

        # Definimos los contenedores de estado como atributos de clase ANTES de actualizar_datos
        self.cont_status_norte = ft.Container(
            content=ft.Image(src="icon_acceso_off.png", width=50, height=50),
            bgcolor="red300", padding=10, border_radius=5, alignment=ft.alignment.center
        )
        self.lbl_status_norte = ft.Text("Barrera Cerrada", weight="bold", color="red600")
        self.lbl_distancia_norte = ft.Text("Distancia Sensor: 500 cm", size=14)

        self.cont_status_sur = ft.Container(
            content=ft.Image(src="icon_acceso_off.png", width=50, height=50),
            bgcolor="red300", padding=10, border_radius=5, alignment=ft.alignment.center
        )
        self.lbl_status_sur = ft.Text("Barrera Cerrada", weight="bold", color="red600")
        self.lbl_distancia_sur = ft.Text("Distancia Sensor: 500 cm", size=14)

        # LÓGICA DE ACTUALIZACIÓN DE DATOS
        def actualizar_datos():
            try:
                # 1. ESTADO DE AMBAS BARRERAS
                estados = DataController.obtener_estado_barreras()
                
                # Leer estado manual del backend para sincronizar switches
                manual_norte = DataController.obtener_manual_barrera("norte")
                manual_sur = DataController.obtener_manual_barrera("sur")
                
                # Sincronizar switches Norte con el backend
                modo_manual_norte = manual_norte.get("modo_manual", False)
                abrir_norte = manual_norte.get("abrir", False)
                if self.switch_manual_norte.value != modo_manual_norte:
                    self.switch_manual_norte.value = modo_manual_norte
                if self.switch_abrir_norte.value != abrir_norte:
                    self.switch_abrir_norte.value = abrir_norte
                self.switch_abrir_norte.disabled = not modo_manual_norte
                
                # Sincronizar switches Sur con el backend
                modo_manual_sur = manual_sur.get("modo_manual", False)
                abrir_sur = manual_sur.get("abrir", False)
                if self.switch_manual_sur.value != modo_manual_sur:
                    self.switch_manual_sur.value = modo_manual_sur
                if self.switch_abrir_sur.value != abrir_sur:
                    self.switch_abrir_sur.value = abrir_sur
                self.switch_abrir_sur.disabled = not modo_manual_sur
                
                # Actualizar Barrera Norte
                estado_norte = estados.get("norte", {})
                distancia_norte = estado_norte.get("distancia_detectada", 500)
                mensaje_norte = estado_norte.get("mensaje", "BARRERA CERRADA")
                
                # Si está en modo manual, usar el estado manual directamente
                if modo_manual_norte:
                    abierta_norte = abrir_norte
                else:
                    abierta_norte = estado_norte.get("barrera_abierta", False)
                
                self.lbl_distancia_norte.value = f"Distancia Sensor: {distancia_norte} cm"
                
                if abierta_norte:
                    self.cont_status_norte.bgcolor = "green"
                    if isinstance(self.cont_status_norte.content, ft.Image):
                        self.cont_status_norte.content.src = "icon_acceso_on.png"
                    self.lbl_status_norte.value = "BARRERA ABIERTA" if modo_manual_norte else mensaje_norte
                    self.lbl_status_norte.color = "green"
                else:
                    self.cont_status_norte.bgcolor = "red300"
                    if isinstance(self.cont_status_norte.content, ft.Image):
                        self.cont_status_norte.content.src = "icon_acceso_off.png"
                    self.lbl_status_norte.value = "BARRERA CERRADA" if modo_manual_norte else mensaje_norte
                    self.lbl_status_norte.color = "red600"
                
                # Actualizar Barrera Sur
                estado_sur = estados.get("sur", {})
                distancia_sur = estado_sur.get("distancia_detectada", 500)
                mensaje_sur = estado_sur.get("mensaje", "BARRERA CERRADA")
                
                # Si está en modo manual, usar el estado manual directamente
                if modo_manual_sur:
                    abierta_sur = abrir_sur
                else:
                    abierta_sur = estado_sur.get("barrera_abierta", False)
                
                self.lbl_distancia_sur.value = f"Distancia Sensor: {distancia_sur} cm"
                
                if abierta_sur:
                    self.cont_status_sur.bgcolor = "green"
                    if isinstance(self.cont_status_sur.content, ft.Image):
                        self.cont_status_sur.content.src = "icon_acceso_on.png"
                    self.lbl_status_sur.value = "BARRERA ABIERTA" if modo_manual_sur else mensaje_sur
                    self.lbl_status_sur.color = "green"
                else:
                    self.cont_status_sur.bgcolor = "red300"
                    if isinstance(self.cont_status_sur.content, ft.Image):
                        self.cont_status_sur.content.src = "icon_acceso_off.png"
                    self.lbl_status_sur.value = "BARRERA CERRADA" if modo_manual_sur else mensaje_sur
                    self.lbl_status_sur.color = "red600"
                
                # Actualizar botones del mapa si existen
                if hasattr(self, 'btn_acceso_norte') and hasattr(self, 'btn_acceso_sur'):
                    # Norte
                    btn_norte_circulo = self.btn_acceso_norte.content.controls[0]
                    if abierta_norte:
                        btn_norte_circulo.bgcolor = "green"
                        btn_norte_circulo.content.src = "icon_acceso_on.png"
                    else:
                        btn_norte_circulo.bgcolor = "red300"
                        btn_norte_circulo.content.src = "icon_acceso_off.png"
                    
                    # Sur
                    btn_sur_circulo = self.btn_acceso_sur.content.controls[0]
                    if abierta_sur:
                        btn_sur_circulo.bgcolor = "green"
                        btn_sur_circulo.content.src = "icon_acceso_on.png"
                    else:
                        btn_sur_circulo.bgcolor = "red300"
                        btn_sur_circulo.content.src = "icon_acceso_off.png"

                # 2. HISTORIAL DE ACCESOS DE VEHÍCULOS
                logs = DataController.obtener_historial_accesos()
                self.columna_historial.controls.clear()
                
                # Actualizar contador
                total_registros = len(logs) if logs else 0
                self.lbl_contador_historial.value = f"Total: {total_registros} registros"
                
                if not logs:
                    self.columna_historial.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Icon(ft.Icons.HISTORY, size=60, color="grey400"),
                                ft.Text("Sin registros de acceso", size=16, color="grey600", italic=True)
                            ], horizontal_alignment="center", spacing=10),
                            alignment=ft.alignment.center,
                            padding=40
                        )
                    )
                else:
                    for log in logs:
                        # Determinar icono y colores según el tipo de acceso
                        tipo_acceso = log.get("tipo", "Acceso")
                        barrera_log = log.get("barrera", "").upper()
                        
                        if "Manual" in tipo_acceso:
                            icon = ft.Icons.ADMIN_PANEL_SETTINGS
                            color_icono = "blue600"
                            bgcolor_card = "#e3f2fd"  # azul claro
                            color_barrera = "blue700"
                        elif "Emergencia" in tipo_acceso or "Viento" in tipo_acceso:
                            icon = ft.Icons.WARNING
                            color_icono = "red600"
                            bgcolor_card = "#ffebee"  # rojo claro
                            color_barrera = "red700"
                        else:
                            icon = ft.Icons.DIRECTIONS_CAR
                            color_icono = "green600"
                            bgcolor_card = "#e8f5e9"  # verde claro
                            color_barrera = "green700"
                        
                        # Formatear hora
                        hora_completa = log.get("hora", "")
                        hora_display = hora_completa
                        if hora_completa:
                            try:
                                # Formatear: "2025-12-11 19:59:54" -> "19:59:54"
                                if " " in hora_completa:
                                    hora_display = hora_completa.split(" ")[1]
                            except:
                                pass
                        
                        # Crear tarjeta de acceso
                        card_acceso = ft.Container(
                            content=ft.Row([
                                # Icono
                                ft.Container(
                                    content=ft.Icon(icon, color=color_icono, size=32),
                                    bgcolor="white",
                                    padding=12,
                                    border_radius=8,
                                    width=56,
                                    height=56,
                                    alignment=ft.alignment.center
                                ),
                                # Información
                                ft.Column([
                                    ft.Row([
                                        ft.Text(
                                            tipo_acceso,
                                            size=16,
                                            weight="bold",
                                            color="grey900"
                                        ),
                                        ft.Container(expand=True),
                                        ft.Container(
                                            content=ft.Text(
                                                barrera_log if barrera_log else "N/A",
                                                size=12,
                                                weight="bold",
                                                color="white"
                                            ),
                                            bgcolor=color_barrera,
                                            padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                            border_radius=12
                                        )
                                    ], spacing=10),
                                    ft.Row([
                                        ft.Icon(ft.Icons.ACCESS_TIME, size=16, color="grey600"),
                                        ft.Text(hora_display, size=14, color="grey700")
                                    ], spacing=5),
                                    ft.Row([
                                        ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=16, color="green600"),
                                        ft.Text(log.get("evento", "Acceso Permitido"), size=13, color="grey600")
                                    ], spacing=5)
                                ], spacing=4, expand=True, tight=True),
                            ], spacing=15, vertical_alignment="center"),
                            bgcolor=bgcolor_card,
                            padding=15,
                            border_radius=10,
                            border=ft.border.all(1, color="grey300"),
                            shadow=ft.BoxShadow(blur_radius=2, color="grey300", spread_radius=0)
                        )
                        
                        self.columna_historial.controls.append(card_acceso)

                self.page.update()
            except Exception as e:
                print(f"Error UI: {e}")

        def ciclo_refresco():
            while True:
                time.sleep(0.5)
                if not getattr(self, 'activo', True): break
                if self.page: actualizar_datos()
        
        # Carga inicial inmediata (después de que se definan los atributos)
        actualizar_datos()
        threading.Thread(target=ciclo_refresco, daemon=True).start()

        # Paneles de estado para cada barrera
        panel_norte = ft.Container(
            content=ft.Column([
                ft.Text("Acceso Norte", size=20, weight="bold"),
                ft.Divider(),
                ft.Container(
                    content=ft.Column([
                        self.cont_status_norte,
                        self.lbl_status_norte,
                        ft.Divider(),
                        self.lbl_distancia_norte
                    ], horizontal_alignment="center", spacing=10),
                    alignment=ft.alignment.center,
                    expand=True
                ),
                ft.Divider(),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Panel de Operador", weight="bold", size=14),
                        self.switch_manual_norte,
                        self.switch_abrir_norte,
                        ft.Text("(Activa ambos para abrir)", size=11, italic=True, color="grey")
                    ], spacing=8),
                    bgcolor="#f0f2f5", padding=15, border_radius=10
                )
            ], horizontal_alignment="center", spacing=10),
            bgcolor="white", 
            padding=20, 
            border_radius=10, 
            expand=1,
            alignment=ft.alignment.top_center
        )

        panel_sur = ft.Container(
            content=ft.Column([
                ft.Text("Acceso Sur", size=20, weight="bold"),
                ft.Divider(),
                ft.Container(
                    content=ft.Column([
                        self.cont_status_sur,
                        self.lbl_status_sur,
                        ft.Divider(),
                        self.lbl_distancia_sur
                    ], horizontal_alignment="center", spacing=10),
                    alignment=ft.alignment.center,
                    expand=True
                ),
                ft.Divider(),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Panel de Operador", weight="bold", size=14),
                        self.switch_manual_sur,
                        self.switch_abrir_sur,
                        ft.Text("(Activa ambos para abrir)", size=11, italic=True, color="grey")
                    ], spacing=8),
                    bgcolor="#f0f2f5", padding=15, border_radius=10
                )
            ], horizontal_alignment="center", spacing=10),
            bgcolor="white", 
            padding=20, 
            border_radius=10, 
            expand=1,
            alignment=ft.alignment.top_center
        )

        panel_historial = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.HISTORY, size=28, color="blueGrey700"),
                    ft.Text("Historial de Accesos de Vehículos", size=22, weight="bold"),
                    ft.Container(expand=True),
                    ft.Container(
                        content=self.lbl_contador_historial,
                        padding=ft.padding.only(right=10)
                    )
                ], alignment="center", spacing=10),
                ft.Divider(height=1),
                ft.Container(
                    content=self.columna_historial,
                    expand=True,
                    padding=ft.padding.only(top=10)
                )
            ], spacing=10, expand=True),
            bgcolor="white",
            padding=25,
            border_radius=10,
            expand=True,
            width=float("inf"),
            shadow=ft.BoxShadow(blur_radius=5, color="#1A000000")
        )

        ANCHO_MAPA = 1159 
        ALTO_MAPA = 376

        def toggle_access(e):
            # 1. Identificar qué barrera se está controlando
            nombre_barrera = e.control.data  # "Acceso Norte" o "Acceso Sur"
            barrera_id = "norte" if nombre_barrera == "Acceso Norte" else "sur"
            
            # 2. Leer el estado actual de la barrera
            estados_todas = DataController.obtener_estado_barreras()
            estado_actual = estados_todas.get(barrera_id, {})
            abierta_actual = estado_actual.get("barrera_abierta", False)
            
            # 3. Determinar la nueva acción (toggle: si está abierta, cerrar; si está cerrada, abrir)
            nueva_abierta = not abierta_actual
            
            # 4. Activar modo manual y guardar el estado en el backend
            DataController.guardar_manual_barrera(barrera_id, True, nueva_abierta)
            
            # 5. Actualizar los switches para reflejar el cambio
            if barrera_id == "norte":
                self.switch_manual_norte.value = True
                self.switch_abrir_norte.value = nueva_abierta
                self.switch_abrir_norte.disabled = False
            else:
                self.switch_manual_sur.value = True
                self.switch_abrir_sur.value = nueva_abierta
                self.switch_abrir_sur.disabled = False
            
            # 6. Actualizar visuales inmediatamente
            actualizar_datos()

        # --- Creación de los botones circulares ---
        self.btn_acceso_norte = ft.Container(
            content=ft.Column([
                # 1. El círculo con el icono
                ft.Container(
                    content=ft.Image(src="icon_acceso_off.png", width=30, height=30),
                    shape=ft.BoxShape.CIRCLE,
                    bgcolor="red300",
                    border=ft.border.all(3, "white"),
                    shadow=ft.BoxShadow(blur_radius=10, color="black45"),
                    width=55,
                    height=55,
                    alignment=ft.alignment.center,
                ),
                # 2. El título envuelto en un Container para poder usar border_radius
                ft.Container(
                    content=ft.Text(
                        "Acceso Norte", 
                        size=11, 
                        weight="bold", 
                        color="white"
                    ),
                    bgcolor="black",     # Fondo semitransparente
                    padding=ft.padding.symmetric(vertical=2, horizontal=8),
                    border_radius=5,       # Ahora sí funcionará aquí
                )
            ], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5
            ),
            left=790,  
            top=10,   
            on_click=toggle_access,
            data="Acceso Norte",
        )
        self.btn_acceso_norte.mouse_cursor = ft.MouseCursor.CLICK

        self.btn_acceso_sur = ft.Container(
            content=ft.Column([
                # 1. El círculo con el icono
                ft.Container(
                    content=ft.Image(src="icon_acceso_off.png", width=30, height=30),
                    shape=ft.BoxShape.CIRCLE,
                    bgcolor="red300",
                    border=ft.border.all(3, "white"),
                    shadow=ft.BoxShadow(blur_radius=10, color="black45"),
                    width=55,
                    height=55,
                    alignment=ft.alignment.center,
                ),
                # 2. El título envuelto en un Container para poder usar border_radius
                ft.Container(
                    content=ft.Text(
                        "Acceso Sur", 
                        size=11, 
                        weight="bold", 
                        color="white"
                    ),
                    bgcolor="black",     # Fondo semitransparente
                    padding=ft.padding.symmetric(vertical=2, horizontal=8),
                    border_radius=5,       # Ahora sí funcionará aquí
                )
            ], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5
            ),
            left=690,  
            top=280,   
            on_click=toggle_access,
            data="Acceso Sur",
        )
        self.btn_acceso_sur.mouse_cursor = ft.MouseCursor.CLICK

        # --- El Stack con tamaño FIJO (Evita el descuadre) ---
        mapa_stack = ft.Stack(
            controls=[
                ft.Image(
                    src="mapa_iluminacion_off.jpg",
                    width=ANCHO_MAPA,
                    height=ALTO_MAPA,
                    fit=ft.ImageFit.CONTAIN, # Mantiene la proporción sin recortar
                ),
                self.btn_acceso_norte,
                self.btn_acceso_sur,
            ],
            width=ANCHO_MAPA,
            height=ALTO_MAPA,
        )

        # --- Panel del Mapa con SCROLL (Para pantallas pequeñas) ---
        panel_mapa = ft.Container(
            # Metemos el mapa en un Row con scroll para que si la ventana es 
            # pequeña, el mapa NO se encoja (y los botones no se muevan)
            content=ft.Row([mapa_stack], scroll=ft.ScrollMode.ADAPTIVE),
            expand=True,
            border_radius=10,
            bgcolor="#ffffff",
            padding=10,
        )

    
        self.content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Text("Control de Accesos Inteligente", size=24, weight="bold"),
                        bgcolor="#ffffff", padding=20, border_radius=10, expand=True
                    ),
                ]),
                ft.Row([panel_mapa]),
                # Dos paneles lado a lado (Norte y Sur)
                ft.Row(
                    controls=[panel_norte, panel_sur],
                    expand=False,
                    spacing=20,
                    vertical_alignment=ft.CrossAxisAlignment.START
                ),
                # Registro de entradas debajo ocupando todo el ancho
                ft.Row([panel_historial], expand=True, width=float("inf"))
            ], scroll=ft.ScrollMode.ADAPTIVE, spacing=20),
            padding=20
        )

    def matar_hilos(self):
        self.activo = False