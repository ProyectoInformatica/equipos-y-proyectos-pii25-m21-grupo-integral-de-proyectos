import flet as ft
import threading
import time
from controllers.data_controller import DataController


class BiordinarioView(ft.Container):
    def __init__(self, page):
        super().__init__(expand=True)
        self.page  = page
        self.activo = True

        # ── Tabla de registros ────────────────────────────────
        self.tabla_filas  = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Fecha",  weight="bold")),
                ft.DataColumn(ft.Text("Valor",  weight="bold"), numeric=True),
                ft.DataColumn(ft.Text("Texto",  weight="bold")),
            ],
            rows=[],
            border=ft.border.all(1, "grey300"),
            border_radius=8,
            horizontal_lines=ft.BorderSide(1, "grey200"),
            heading_row_color="blueGrey50",
            heading_row_height=48,
            data_row_min_height=44,
            expand=True,
            width=float("inf"),
        )

        self.lbl_total  = ft.Text("", size=12, color="grey600", italic=True)
        self.lbl_ultimo = ft.Text("Último registro: —", size=13, color="grey700")

        # ── Tarjeta resumen del último dato ───────────────────
        self.lbl_ultimo_valor = ft.Text("—",    size=32, weight="bold", color="blueGrey800")
        self.lbl_ultimo_texto = ft.Text("—",    size=20, color="blueGrey600")
        self.lbl_ultimo_hora  = ft.Text("—",    size=12, color="grey500", italic=True)

        tarjeta_ultimo = ft.Container(
            content=ft.Column([
                ft.Text("Último dato recibido", size=14, weight="bold", color="blueGrey700"),
                ft.Divider(height=8),
                ft.Row([
                    ft.Column([
                        ft.Text("Valor numérico", size=12, color="grey600"),
                        self.lbl_ultimo_valor,
                    ], horizontal_alignment="center", spacing=4),
                    ft.VerticalDivider(width=30),
                    ft.Column([
                        ft.Text("Valor texto", size=12, color="grey600"),
                        self.lbl_ultimo_texto,
                    ], horizontal_alignment="center", spacing=4),
                ], alignment="center", spacing=20),
                ft.Divider(height=8),
                self.lbl_ultimo_hora,
            ], horizontal_alignment="center", spacing=6),
            bgcolor="white",
            padding=25,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=6, color="#1A000000"),
            expand=1,
        )

        # ── Lógica de refresco ────────────────────────────────
        def actualizar():
            try:
                registros = DataController.obtener_datos_biordinario(50)

                # Actualizar tarjeta resumen con el más reciente
                if registros:
                    ultimo = registros[0]
                    self.lbl_ultimo_valor.value = str(ultimo["valor"])
                    self.lbl_ultimo_texto.value = ultimo["texto"] if ultimo["texto"] else "—"
                    hora = ultimo["hora"]
                    try:
                        if " " in hora:
                            hora = hora.split(" ")[1]
                    except Exception:
                        pass
                    self.lbl_ultimo_hora.value = f"Recibido a las {hora}"

                # Actualizar tabla
                self.tabla_filas.rows.clear()
                self.lbl_total.value = f"Total: {len(registros)} registros"

                for r in registros:
                    hora_display = r["hora"]
                    try:
                        if " " in hora_display:
                            fecha, hora_display = hora_display.split(" ", 1)
                        else:
                            fecha = ""
                    except Exception:
                        fecha = ""

                    self.tabla_filas.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(r["hora"],          size=13)),
                                ft.DataCell(ft.Text(str(r["valor"]),    size=13, weight="bold")),
                                ft.DataCell(ft.Text(r["texto"] or "—",  size=13)),
                            ]
                        )
                    )

                if not registros:
                    self.tabla_filas.rows.append(
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text("Sin datos", color="grey500", italic=True)),
                            ft.DataCell(ft.Text("—")),
                            ft.DataCell(ft.Text("—")),
                        ])
                    )

                self.page.update()
            except Exception as e:
                print(f"[BiordinarioView] Error: {e}")

        def ciclo_refresco():
            while True:
                time.sleep(2)
                if not getattr(self, "activo", True):
                    break
                if self.page:
                    actualizar()

        actualizar()
        threading.Thread(target=ciclo_refresco, daemon=True).start()

        # ── Panel tabla ───────────────────────────────────────
        panel_tabla = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.TABLE_ROWS, color="blueGrey700"),
                    ft.Text("Historial de lecturas", size=18, weight="bold"),
                    ft.Container(expand=True),
                    self.lbl_total,
                ], spacing=8),
                ft.Divider(height=1),
                ft.Container(
                    content=ft.Row(
                        [self.tabla_filas],
                        scroll=ft.ScrollMode.ADAPTIVE,
                    ),
                    expand=True,
                    padding=ft.padding.only(top=8),
                ),
            ], spacing=10, expand=True),
            bgcolor="white",
            padding=25,
            border_radius=12,
            expand=True,
            shadow=ft.BoxShadow(blur_radius=6, color="#1A000000"),
        )

        # ── Layout final ──────────────────────────────────────
        self.content = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text("Sensor Biordinario", size=24, weight="bold"),
                    bgcolor="white", padding=20, border_radius=10, expand=True,
                ),
                ft.Row([tarjeta_ultimo], expand=False),
                ft.Row([panel_tabla], expand=True),
            ], scroll=ft.ScrollMode.ADAPTIVE, spacing=20),
            padding=20,
        )

    def matar_hilos(self):
        self.activo = False
