import flet as ft
import threading
import time
from datetime import datetime
from controllers.data_controller import DataController

class DashboardView(ft.Container):
    def __init__(self, page):
        super().__init__(expand=True, padding=20)
        self.page = page
        self.activo = True

        # Variables para almacenar datos históricos
        self.historial_temp = []
        self.historial_humedad = []
        self.historial_agua = []
        
        # Elementos de la UI mejorados
        self.card_iluminacion = self._build_enhanced_card("Iluminación", ft.Icons.LIGHTBULB, "Cargando...", "blueGrey700", "blueGrey700")
        self.card_ambiental = self._build_enhanced_card("Temperatura", ft.Icons.THERMOSTAT, "-- °C", "blueGrey700", "blueGrey700")
        self.card_humedad = self._build_enhanced_card("Humedad", ft.Icons.WATER_DROP, "-- %", "blueGrey700", "blueGrey700")
        self.card_aire = self._build_enhanced_card("Calidad Aire", ft.Icons.AIR, "--", "blueGrey700", "blueGrey700")
        self.card_recursos = self._build_enhanced_card("Agua", ft.Icons.WATER_DROP, "-- L/min", "blueGrey700", "blueGrey700")
        self.card_emergencia = self._build_enhanced_card("Alertas", ft.Icons.WARNING, "Sistema OK", "blueGrey700", "blueGrey700")
        
        # Tarjetas de estadísticas
        self.stats_card = self._build_stats_card()
        
        # Contenedor principal
        self.lbl_last_update = ft.Text(
            f"Última actualización: {datetime.now().strftime('%H:%M:%S')}",
            size=12,
            color="grey600"
        )
        self.content = ft.Column([
            # Header mejorado
            ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text("Panel de Control General", size=28, weight="bold"),
                        self.lbl_last_update
                    ], spacing=4, tight=True),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Icon(ft.Icons.DASHBOARD, size=32, color="blueGrey700"),
                        bgcolor="blueGrey50",
                        padding=12,
                        border_radius=10
                    )
                ], alignment="center"),
                bgcolor="#ffffff",
                padding=20,
                border_radius=10,
                width=float("inf")
            ),
            ft.Container(height=15),
            
            # Primera fila: Métricas principales
            ft.ResponsiveRow([
                ft.Column([self.card_iluminacion], col={"sm": 12, "md": 6, "lg": 4}),
                ft.Column([self.card_ambiental], col={"sm": 12, "md": 6, "lg": 4}),
                ft.Column([self.card_humedad], col={"sm": 12, "md": 6, "lg": 4}),
            ], spacing=15),
            
            ft.Container(height=15),
            
            # Segunda fila: Más métricas
            ft.ResponsiveRow([
                ft.Column([self.card_aire], col={"sm": 12, "md": 6, "lg": 4}),
                ft.Column([self.card_recursos], col={"sm": 12, "md": 6, "lg": 4}),
                ft.Column([self.card_emergencia], col={"sm": 12, "md": 6, "lg": 4}),
            ], spacing=15),
            
            ft.Container(height=15),
            
            # Tercera fila: Estadísticas y resumen
            ft.ResponsiveRow([
                ft.Column([self.stats_card], col={"sm": 12, "md": 12, "lg": 12}),
            ], spacing=15)
        ], scroll=ft.ScrollMode.AUTO, spacing=0)

        # Iniciar hilo de actualización
        threading.Thread(target=self._update_loop, daemon=True).start()

    def _build_enhanced_card(self, title, icon, value, color, accent_color):
        """Constructor mejorado de tarjetas informativas con más detalles."""
        lbl_value = ft.Text(value, size=24, weight="bold", color=color)
        lbl_subtitle = ft.Text("", size=12, color="grey600")
        icon_control = ft.Icon(icon, size=36, color=accent_color)
        
        # Indicador de progreso (opcional)
        progress_bar = ft.ProgressBar(width=float("inf"), height=6, color=accent_color, bgcolor="grey200")
        progress_bar.value = None
        
        card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=icon_control,
                        bgcolor="grey100",
                        padding=12,
                        border_radius=10
                    ),
                    ft.Column([
                        ft.Text(title, size=14, weight="bold"),
                        lbl_subtitle
                    ], spacing=2, tight=True, expand=True),
                ], spacing=12),
                ft.Container(height=15),
                lbl_value,
                ft.Container(height=8),
                progress_bar
            ], spacing=0),
            bgcolor="#ffffff",
            padding=20,
            border_radius=10,
            border=ft.border.all(1, "grey200")
        )
        
        card.lbl_value = lbl_value
        card.lbl_subtitle = lbl_subtitle
        card.icon_control = icon_control
        card.progress_bar = progress_bar
        return card

    def _build_stats_card(self):
        """Tarjeta de estadísticas generales."""
        self.stats_light_status = ft.Text("--", size=14, weight="bold")
        self.stats_temp_avg = ft.Text("--", size=14, weight="bold")
        self.stats_humidity_avg = ft.Text("--", size=14, weight="bold")
        self.stats_alertas_count = ft.Text("0", size=14, weight="bold", color="green")
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.ANALYTICS, size=24, color="blueGrey700"),
                    ft.Text("Estadísticas del Sistema", size=18, weight="bold")
                ], spacing=10),
                ft.Divider(height=15, thickness=1),
                ft.ResponsiveRow([
                    ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.LIGHTBULB, size=20, color="blueGrey700"),
                            ft.Column([
                                ft.Text("Estado Iluminación", size=12, color="grey600"),
                                self.stats_light_status
                            ], spacing=2, tight=True, expand=True)
                        ], spacing=10)
                    ], col={"sm": 12, "md": 6, "lg": 3}),
                    ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.THERMOSTAT, size=20, color="blueGrey700"),
                            ft.Column([
                                ft.Text("Temp. Promedio", size=12, color="grey600"),
                                self.stats_temp_avg
                            ], spacing=2, tight=True, expand=True)
                        ], spacing=10)
                    ], col={"sm": 12, "md": 6, "lg": 3}),
                    ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.WATER_DROP, size=20, color="blueGrey700"),
                            ft.Column([
                                ft.Text("Humedad Promedio", size=12, color="grey600"),
                                self.stats_humidity_avg
                            ], spacing=2, tight=True, expand=True)
                        ], spacing=10)
                    ], col={"sm": 12, "md": 6, "lg": 3}),
                    ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.WARNING, size=20, color="blueGrey700"),
                            ft.Column([
                                ft.Text("Alertas Activas", size=12, color="grey600"),
                                self.stats_alertas_count
                            ], spacing=2, tight=True, expand=True)
                        ], spacing=10)
                    ], col={"sm": 12, "md": 6, "lg": 3}),
                ], spacing=15)
            ], spacing=10),
            bgcolor="#ffffff",
            padding=20,
            border_radius=10,
            border=ft.border.all(1, "grey200")
        )

    def _calculate_average(self, data_list, key="value"):
        """Calcula el promedio de una lista de datos."""
        if not data_list or len(data_list) == 0:
            return 0
        try:
            values = [item.get(key, 0) for item in data_list if isinstance(item, dict)]
            return sum(values) / len(values) if values else 0
        except:
            return 0

    def _update_ui(self):
        try:
            # Actualizar hora en header
            if self.lbl_last_update:
                self.lbl_last_update.value = f"Última actualización: {datetime.now().strftime('%H:%M:%S')}"

            # 1. ILUMINACIÓN
            luz_estado = DataController.obtener_estado_luz()
            lux = DataController.obtener_luminosidad()
            if luz_estado == "on":
                self.card_iluminacion.lbl_value.value = f"ENCENDIDO"
                self.card_iluminacion.lbl_subtitle.value = f"Luminosidad: {int(lux)}%"
                self.card_iluminacion.lbl_value.color = "blueGrey700"
                self.card_iluminacion.icon_control.color = "blueGrey700"
                self.card_iluminacion.progress_bar.value = int(lux) / 100
                self.card_iluminacion.progress_bar.color = "blueGrey400"
            else:
                self.card_iluminacion.lbl_value.value = f"APAGADO"
                self.card_iluminacion.lbl_subtitle.value = f"Luminosidad: {int(lux)}%"
                self.card_iluminacion.lbl_value.color = "grey600"
                self.card_iluminacion.icon_control.color = "grey600"
                self.card_iluminacion.progress_bar.value = int(lux) / 100
                self.card_iluminacion.progress_bar.color = "grey400"

            # 2. AMBIENTAL - TEMPERATURA
            datos_env = DataController.obtener_datos_ambientales()
            if datos_env["temp"] and len(datos_env["temp"]) > 0:
                temp_val = datos_env["temp"][-1]["value"]
                self.card_ambiental.lbl_value.value = f"{temp_val} °C"
                
                # Calcular promedio
                self.historial_temp = datos_env["temp"][-10:]  # Últimos 10 valores
                temp_avg = self._calculate_average(self.historial_temp)
                self.card_ambiental.lbl_subtitle.value = f"Promedio: {temp_avg:.1f} °C"
                
                # Barra de progreso (0-40°C)
                progress = min(max(temp_val / 40, 0), 1)
                self.card_ambiental.progress_bar.value = progress
                self.card_ambiental.progress_bar.color = "blueGrey400"
                self.card_ambiental.lbl_value.color = "blueGrey700"
                self.card_ambiental.icon_control.color = "blueGrey700"
            else:
                self.card_ambiental.lbl_value.value = "-- °C"
                self.card_ambiental.lbl_subtitle.value = "Sin datos"
                self.card_ambiental.progress_bar.value = None

            # 3. HUMEDAD
            if datos_env["hum"] and len(datos_env["hum"]) > 0:
                hum_val = datos_env["hum"][-1]["value"]
                self.card_humedad.lbl_value.value = f"{hum_val} %"
                
                # Calcular promedio
                self.historial_humedad = datos_env["hum"][-10:]
                hum_avg = self._calculate_average(self.historial_humedad)
                self.card_humedad.lbl_subtitle.value = f"Promedio: {hum_avg:.1f} %"
                
                # Barra de progreso (0-100%)
                self.card_humedad.progress_bar.value = hum_val / 100
                self.card_humedad.progress_bar.color = "blueGrey400"
                self.card_humedad.lbl_value.color = "blueGrey700"
                self.card_humedad.icon_control.color = "blueGrey700"
            else:
                self.card_humedad.lbl_value.value = "-- %"
                self.card_humedad.lbl_subtitle.value = "Sin datos"
                self.card_humedad.progress_bar.value = None

            # 4. CALIDAD DEL AIRE
            if datos_env["iaq"] and len(datos_env["iaq"]) > 0:
                iaq_val = datos_env["iaq"][-1]["value"]
                if iaq_val < 50:
                    calidad = "Excelente"
                    color = "blueGrey700"
                elif iaq_val < 100:
                    calidad = "Buena"
                    color = "blueGrey700"
                elif iaq_val < 150:
                    calidad = "Moderada"
                    color = "blueGrey600"
                else:
                    calidad = "Mala"
                    color = "red600"
                
                self.card_aire.lbl_value.value = calidad
                self.card_aire.lbl_subtitle.value = f"Índice: {iaq_val}"
                self.card_aire.lbl_value.color = color
                self.card_aire.icon_control.color = color
                self.card_aire.progress_bar.value = min(iaq_val / 200, 1)
                self.card_aire.progress_bar.color = "blueGrey400" if color != "red600" else "red400"
            else:
                self.card_aire.lbl_value.value = "--"
                self.card_aire.lbl_subtitle.value = "Sin datos"
                self.card_aire.progress_bar.value = None
            
            # 6. RECURSOS - AGUA
            datos_agua = DataController.obtener_datos_agua()
            if datos_agua and len(datos_agua) > 0:
                flujo = datos_agua[-1]["value"]
                self.card_recursos.lbl_value.value = f"{flujo:.1f} L/min"
                
                # Calcular promedio
                self.historial_agua = datos_agua[-10:]
                agua_avg = self._calculate_average(self.historial_agua)
                self.card_recursos.lbl_subtitle.value = f"Promedio: {agua_avg:.1f} L/min"
                
                if flujo > 5.0: 
                    self.card_recursos.lbl_value.color = "red600"
                    self.card_recursos.icon_control.color = "red600"
                    self.card_recursos.progress_bar.color = "red400"
                    self.card_recursos.progress_bar.value = min(flujo / 10, 1)
                else:
                    self.card_recursos.lbl_value.color = "blueGrey700"
                    self.card_recursos.icon_control.color = "blueGrey700"
                    self.card_recursos.progress_bar.color = "blueGrey400"
                    self.card_recursos.progress_bar.value = flujo / 10
            else:
                self.card_recursos.lbl_value.value = "-- L/min"
                self.card_recursos.lbl_subtitle.value = "Sin datos"
                self.card_recursos.progress_bar.value = None

            # 7. EMERGENCIAS
            datos_emergencia = DataController.obtener_datos_emergencia()
            config = DataController.obtener_config_alertas()
            limite_humo = config.get("humo_max", 25)
            limite_viento = config.get("viento_max", 50)
            
            alerta = False
            msg = "Sistema Normal"
            alertas_count = 0
            
            if datos_emergencia["humo"] and datos_emergencia["humo"][-1]["value"] > limite_humo:
                alerta = True
                alertas_count += 1
                val = datos_emergencia["humo"][-1]["value"]
                msg = f"¡ALERTA DE HUMO! ({val})"
            elif datos_emergencia["viento"] and datos_emergencia["viento"][-1]["value"] > limite_viento:
                alerta = True
                alertas_count += 1
                val = datos_emergencia["viento"][-1]["value"]
                msg = f"¡VIENTO FUERTE! ({val} km/h)"

            if alerta:
                self.card_emergencia.lbl_value.value = msg
                self.card_emergencia.lbl_subtitle.value = "Acción requerida"
                self.card_emergencia.lbl_value.color = "red600"
                self.card_emergencia.icon_control.color = "red600"
                self.card_emergencia.icon_control.name = ft.Icons.WARNING
                self.card_emergencia.progress_bar.value = 1.0
                self.card_emergencia.progress_bar.color = "red400"
            else:
                self.card_emergencia.lbl_value.value = "Sin incidencias"
                self.card_emergencia.lbl_subtitle.value = "Todo funcionando correctamente"
                self.card_emergencia.lbl_value.color = "blueGrey700"
                self.card_emergencia.icon_control.color = "blueGrey700"
                self.card_emergencia.icon_control.name = ft.Icons.CHECK_CIRCLE
                self.card_emergencia.progress_bar.value = 0.0
                self.card_emergencia.progress_bar.color = "blueGrey400"

            # Actualizar estadísticas
            self._update_stats(luz_estado, datos_env, datos_agua, alertas_count)

            self.page.update()
        except Exception as e:
            print(f"Error Dashboard: {e}")

    def _update_stats(self, luz_estado, datos_env, datos_agua, alertas_count):
        """Actualiza la tarjeta de estadísticas."""
        # Estado iluminación
        self.stats_light_status.value = "ACTIVA" if luz_estado == "on" else "INACTIVA"
        self.stats_light_status.color = "blueGrey700" if luz_estado == "on" else "grey600"
        
        # Temperatura promedio
        if datos_env["temp"] and len(datos_env["temp"]) > 0:
            temp_avg = self._calculate_average(datos_env["temp"][-20:])
            self.stats_temp_avg.value = f"{temp_avg:.1f} °C"
        else:
            self.stats_temp_avg.value = "--"
        
        # Humedad promedio
        if datos_env["hum"] and len(datos_env["hum"]) > 0:
            hum_avg = self._calculate_average(datos_env["hum"][-20:])
            self.stats_humidity_avg.value = f"{hum_avg:.1f} %"
        else:
            self.stats_humidity_avg.value = "--"
        
        # Alertas
        self.stats_alertas_count.value = str(alertas_count)
        self.stats_alertas_count.color = "red600" if alertas_count > 0 else "blueGrey700"

    def _update_loop(self):
        while True:
            if not getattr(self, 'activo', True): break
            if self.page:
                self._update_ui()
            time.sleep(2)

    def matar_hilos(self):
        self.activo = False
