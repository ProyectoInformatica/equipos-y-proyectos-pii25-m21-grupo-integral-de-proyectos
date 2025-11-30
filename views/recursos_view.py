import flet as ft
import matplotlib.pyplot as plt
import matplotlib
import io
import base64
import threading
import time

from controllers.data_controller import DataController

matplotlib.use('Agg')

def generar_grafica_agua(historial):
    if not historial: return ""
    
    valores = [x["value"] for x in historial]
    horas = [x["hora"] for x in historial]

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(horas, valores, marker="o", color="#0077be", linewidth=2)
    ax.fill_between(horas, valores, color="#0077be", alpha=0.3)
    
    ax.set_title("Consumo de Agua en Tiempo Real (L/min)")
    ax.set_ylabel("Litros / min")
    ax.grid(True, linestyle='--', alpha=0.7)
    
    plt.xticks(rotation=45)
    if len(horas) > 10:
        ax.set_xticks(range(0, len(horas), 4))
        ax.set_xticklabels([horas[i] for i in range(0, len(horas), 4)])

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    plt.close(fig)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode()

class RecursosView(ft.Container):
    def __init__(self, page):
        super().__init__(expand=True)
        self.page = page

        self.img_agua = ft.Image(src_base64="", border_radius=10, expand=True, fit=ft.ImageFit.CONTAIN)
        self.lbl_fuga = ft.Text("Estado: NORMAL", color="green", weight="bold", size=18)
        # CORRECCIÓN AQUÍ: ft.Icons
        self.indicador_fuga = ft.Icon(ft.Icons.WATER_DROP, color="green", size=40)

        # --- LÓGICA ---
        def refrescar_datos():
            datos = DataController.obtener_datos_agua()
            if datos:
                self.img_agua.src_base64 = generar_grafica_agua(datos)
                
                ultimo_caudal = datos[-1]["value"]
                if ultimo_caudal > 45: 
                    self.lbl_fuga.value = f"¡ALERTA! POSIBLE FUGA ({ultimo_caudal} L/min)"
                    self.lbl_fuga.color = "red"
                    # CORRECCIÓN AQUÍ: ft.Icons
                    self.indicador_fuga.name = ft.Icons.WARNING
                    self.indicador_fuga.color = "red"
                else:
                    self.lbl_fuga.value = f"Consumo Normal: {ultimo_caudal} L/min"
                    self.lbl_fuga.color = "green"
                    # CORRECCIÓN AQUÍ: ft.Icons
                    self.indicador_fuga.name = ft.Icons.WATER_DROP
                    self.indicador_fuga.color = "green"

            self.page.update()

        # --- HILO ---
        def loop():
            while True:
                time.sleep(5)
                try: refrescar_datos()
                except: pass
        
        threading.Thread(target=loop, daemon=True).start()
        refrescar_datos()

        # --- LAYOUT ---
        panel_grafica = ft.Container(
            content=ft.Column([
                ft.Text("Monitorización Hídrica", size=18, weight="bold"),
                self.img_agua
            ]),
            bgcolor="white", padding=20, border_radius=10, expand=2
        )

        panel_info = ft.Container(
            content=ft.Column([
                ft.Text("Diagnóstico", size=18, weight="bold"),
                ft.Container(height=20),
                ft.Row([self.indicador_fuga, self.lbl_fuga], alignment="center"),
                ft.Divider(),
                ft.Text("Consejo de ahorro:", weight="bold"),
                ft.Text("Revise los grifos de zonas comunes si el consumo base supera los 5 L/min.")
            ], horizontal_alignment="center"),
            bgcolor="white", padding=20, border_radius=10, expand=1
        )

        self.content = ft.Container(
            content=ft.Column([
                ft.Container(content=ft.Text("Gestión de Recursos y Mantenimiento", size=24, weight="bold"),
                             bgcolor="#ffffff", padding=20, border_radius=10, expand=False),
                ft.Row([panel_grafica, panel_info], expand=True)
            ], spacing=20),
            padding=20
        )