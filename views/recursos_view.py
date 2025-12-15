import flet as ft
import matplotlib.pyplot as plt
import matplotlib
import io
import base64
import threading
import time
import datetime

from controllers.data_controller import DataController

# Configurar backend no interactivo para evitar errores de hilos
matplotlib.use('Agg')

def generar_grafica(historial, titulo, ylabel, color_linea):
    # Si no hay historial, generamos una lista vacía para mostrar al menos la rejilla
    valores = [x["value"] for x in historial] if historial else []
    horas = []
    
    if historial:
        for x in historial:
            try:
                dt = datetime.datetime.strptime(x["hora"], "%Y-%m-%d %H:%M:%S")
                horas.append(dt.strftime("%H:%M:%S"))
            except:
                horas.append(x["hora"])

    # Crear figura
    fig, ax = plt.subplots(figsize=(5, 3))
    
    if valores:
        ax.plot(horas, valores, marker=".", color=color_linea, linewidth=2)
        ax.fill_between(horas, valores, color=color_linea, alpha=0.2)
    else:
        # Texto placeholder si está vacío
        ax.text(0.5, 0.5, "Sin datos recientes", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, color='gray', alpha=0.5)

    ax.set_title(titulo, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.tick_params(axis='x', labelsize=8, rotation=45)
    ax.tick_params(axis='y', labelsize=8)
    
    # Reducir etiquetas eje X para que no se amontonen
    if len(horas) > 6:
        ax.set_xticks(range(0, len(horas), 5))
        ax.set_xticklabels([horas[i] for i in range(0, len(horas), 5)])

    # Guardar en buffer
    buffer = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buffer, format="png")
    plt.close(fig)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode()

class RecursosView(ft.Container):
    def __init__(self, page):
        super().__init__(expand=True)
        self.page = page

        # IMÁGENES DE GRÁFICAS
        # Iniciamos con una imagen transparente o placeholder
        self.img_agua = ft.Image(
            src_base64=self._generar_placeholder(),
            border_radius=10, 
            expand=True, 
            fit=ft.ImageFit.CONTAIN
        )
        self.img_luz = ft.Image(
            src_base64=self._generar_placeholder(),
            border_radius=10, 
            expand=True, 
            fit=ft.ImageFit.CONTAIN
        )

        # INDICADORES DE ESTADO
        self.lbl_agua = ft.Text("Cargando...", color="grey", weight="bold")
        self.icon_agua = ft.Icon(ft.Icons.WATER_DROP, color="grey")
        
        self.lbl_luz = ft.Text("Cargando...", color="grey", weight="bold")
        self.icon_luz = ft.Icon(ft.Icons.ELECTRIC_BOLT, color="grey")

        # LÓGICA DE ACTUALIZACIÓN
        def refrescar_datos():
            try:
                # 1. AGUA
                datos_agua = DataController.obtener_datos_agua()
                # Siempre generamos gráfica, aunque esté vacía, para mantener el layout
                self.img_agua.src_base64 = generar_grafica(datos_agua, "Consumo Agua", "L/min", "#0077be")
                
                if datos_agua and len(datos_agua) > 0:
                    val_agua = datos_agua[-1]["value"]
                    if val_agua > 45:
                        self.lbl_agua.value = f"¡POSIBLE FUGA! ({val_agua} L/min)"
                        self.lbl_agua.color = "red"
                        self.icon_agua.color = "red"
                    else:
                        self.lbl_agua.value = f"Normal: {val_agua} L/min"
                        self.lbl_agua.color = "green"
                        self.icon_agua.color = "green"
                else:
                    self.lbl_agua.value = "Sin datos de agua"

                # 2. ELECTRICIDAD
                datos_luz = DataController.obtener_datos_electricidad()
                self.img_luz.src_base64 = generar_grafica(datos_luz, "Consumo Eléctrico", "Watts", "#f4b400")
                
                if datos_luz and len(datos_luz) > 0:
                    val_luz = datos_luz[-1]["value"]
                    if val_luz > 8500:
                        self.lbl_luz.value = f"¡SOBRECARGA! ({val_luz} W)"
                        self.lbl_luz.color = "red"
                        self.icon_luz.color = "red"
                    else:
                        self.lbl_luz.value = f"Estable: {val_luz} W"
                        self.lbl_luz.color = "orange"
                        self.icon_luz.color = "orange"
                else:
                    self.lbl_luz.value = "Sin datos eléctricos"

                if self.page: 
                    self.page.update()
            except Exception as e:
                print(f"Error actualizando recursos: {e}")

        def loop():
            while True:
                time.sleep(2) # Actualización más rápida
                if self.page:
                    refrescar_datos()
        
        threading.Thread(target=loop, daemon=True).start()

        # LAYOUT 
        # Panel Izquierdo: Agua
        panel_agua = ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(ft.Icons.WATER_DROP, color="blue"), ft.Text("Red Hídrica", size=16, weight="bold")]),
                ft.Container(content=self.img_agua, expand=True), # Contenedor extra para asegurar expansión
                ft.Divider(),
                ft.Row([self.icon_agua, self.lbl_agua], alignment="center")
            ]),
            bgcolor="white", padding=15, border_radius=10, expand=1
        )

        # Panel Derecho: Electricidad
        panel_luz = ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(ft.Icons.ELECTRIC_BOLT, color="orange"), ft.Text("Red Eléctrica", size=16, weight="bold")]),
                ft.Container(content=self.img_luz, expand=True),
                ft.Divider(),
                ft.Row([self.icon_luz, self.lbl_luz], alignment="center")
            ]),
            bgcolor="white", padding=15, border_radius=10, expand=1
        )

        # Estructura principal
        self.content = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text("Gestión de Recursos y Suministros", size=24, weight="bold"),
                    bgcolor="white", 
                    padding=20, 
                    border_radius=10,
                    width=float("inf"), 
                    shadow=ft.BoxShadow(blur_radius=5, color="#1A000000")
                ),
                ft.Container(height=10),
                ft.Row([panel_agua, panel_luz], expand=True, spacing=20)
            ], expand=True),
            padding=20
        )

    def _generar_placeholder(self):
        """Genera una imagen blanca pequeña en base64 para evitar errores de carga inicial"""
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1sAAAAASUVORK5CYII="