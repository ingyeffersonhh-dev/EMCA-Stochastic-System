import os
from datetime import datetime
from fpdf import FPDF
from core.models.resultados import ResultadoSimulacion
from core.models.parametros import ParametrosEntrada

class ReporteEjecutivoPDF(FPDF):
    def header(self):
        # Fondo oscuro en cabecera estilo EMCA
        self.set_fill_color(11, 11, 15)
        self.rect(0, 0, 210, 30, 'F')
        
        self.set_font("helvetica", "B", 20)
        self.set_text_color(0, 230, 138)  # EMCA Accent Green
        self.cell(0, 10, "EMCA - Reporte Ejecutivo Estocástico", border=False, align="C", new_x="LMARGIN", new_y="NEXT")
        
        self.set_font("helvetica", "I", 10)
        self.set_text_color(226, 232, 240)
        self.cell(0, 10, f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}", border=False, align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Página {self.page_no()}/{{nb}} - EMCA Pilotes", align="C")

def generar_pdf_ejecutivo(resultado: ResultadoSimulacion, params: ParametrosEntrada) -> bytearray:
    """Genera un reporte PDF con análisis financiero y de rendimiento y retorna los bytes."""
    pdf = ReporteEjecutivoPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "", 12)
    
    k = resultado.kpis
    if not k:
        return bytearray()
        
    # --- 1. Contexto del Proyecto ---
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(30, 30, 50)
    pdf.cell(0, 10, "1. Contexto del Proyecto", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 11)
    pdf.set_text_color(50, 50, 50)
    
    vol_total = 3.14159 * (params.diametro_m / 2)**2 * params.longitud_m * params.cantidad_pilotes
    contexto = (
        f"Escenario: {params.nombre_escenario}\n"
        f"Pilotes a ejecutar: {params.cantidad_pilotes} (Volumen total est: {vol_total:.1f} m3)\n"
        f"Logística: {params.num_mixers} mixers, distancia a planta: {params.distancia_proveedor_km} km\n"
        f"Terreno: {params.tipo_suelo.label}"
    )
    pdf.multi_cell(0, 8, contexto)
    pdf.ln(5)

    # --- 2. Resultados Financieros y de Tiempo ---
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(30, 30, 50)
    pdf.cell(0, 10, "2. Proyección Financiera y Plazos (Monte Carlo)", new_x="LMARGIN", new_y="NEXT")
    
    horas_dia = getattr(params, "horas_por_dia", 8.0)
    
    data = [
        ("Duración Mediana (P50)", f"{k.tiempo_proyecto_p50_h:.1f} horas ({k.tiempo_proyecto_p50_h/horas_dia:.1f} días)"),
        ("Duración Pesimista (P90)", f"{k.tiempo_proyecto_p90_h:.1f} horas ({k.tiempo_proyecto_p90_h/horas_dia:.1f} días)"),
        ("Presupuesto Estimado (P50)", f"${getattr(k, 'costo_proyecto_p50_usd', 0):,.2f}"),
        ("Riesgo Presupuestal (P90)", f"${getattr(k, 'costo_proyecto_p90_usd', 0):,.2f}"),
        ("Costo de Inactividad Logística", f"${getattr(k, 'costo_inactividad_mixers_usd', 0):,.2f}"),
        ("Cuello de Botella Limitante", k.cuello_botella.capitalize())
    ]
    
    pdf.set_fill_color(240, 245, 250)
    for row in data:
        pdf.set_font("helvetica", "B", 11)
        pdf.cell(85, 10, row[0], border=1, fill=True)
        pdf.set_font("helvetica", "", 11)
        pdf.cell(105, 10, row[1], border=1, new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(8)
    
    # --- 3. Análisis Estratégico e IA ---
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "3. Recomendaciones Operativas", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 11)
    
    alerta_prefix = "ALERTA CRÍTICA: " if k.alerta_logistica else "ESTADO NORMAL: "
    analisis = f"{alerta_prefix}El tiempo promedio de espera del mixer es de {k.tiempo_espera_mixer_promedio_h:.2f} horas. La utilización promedio de la flota de mixers está al {k.utilizacion_mixer_pct:.1f}%.\n"
    
    if k.alerta_logistica:
         analisis += "\nRecomendación de Optimización: Existe un cuello de botella grave en la logística. Se recomienda urgentemente evaluar el aumento de la flota de mixers o reubicar el punto de suministro (proveedor más cercano) para mitigar los costos de inactividad de la perforadora y acelerar el cronograma del proyecto."
    elif k.alerta_capacidad_mixer:
         analisis += "\nRecomendación de Optimización: Los mixers están saturados (>85% uso). Cualquier interrupción vial causará paros en la perforación. Considere un mixer de contingencia."
    else:
         analisis += "\nRecomendación de Optimización: El sistema está balanceado operativamente. Mantenga el control de la dispersión en los tiempos de perforación para asegurar el cumplimiento del escenario P50."
         
    pdf.multi_cell(0, 8, analisis)
    
    return bytearray(pdf.output())
