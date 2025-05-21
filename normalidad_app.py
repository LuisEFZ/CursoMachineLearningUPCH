import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import shapiro, anderson, kstest, norm, probplot
from io import BytesIO
from docx import Document
from docx.shared import Inches
from fpdf import FPDF

# Configuración de la aplicación
st.set_page_config(page_title="Prueba de Normalidad", layout="centered")
st.title("📈 Análisis de Normalidad")
st.write("Sube un archivo Excel con hasta 100 datos numéricos para evaluar si siguen una distribución normal.")

# Cargar archivo
uploaded_file = st.file_uploader("Cargar archivo Excel (.xlsx)", type=["xlsx"])

# Selección del nivel de significancia
alpha_default = 0.05
alpha = st.number_input(
    "Selecciona el nivel de significancia (α)", 
    min_value=0.01, max_value=0.10, 
    value=alpha_default, step=0.01
)

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
    except Exception as e:
        st.error(f"❌ Error al leer el archivo: {e}")
    else:
        st.subheader("Vista previa de los datos")
        st.dataframe(df.head())

        # Verificar si tiene encabezado
        columnas_numericas = df.select_dtypes(include=["number"]).columns.tolist()
        if not columnas_numericas:
            st.error("❌ No se encontraron columnas numéricas.")
        else:
            columna = st.selectbox("Selecciona la columna a analizar", columnas_numericas)
            datos = df[columna].dropna().values

            if len(datos) > 100:
                st.warning("⚠️ Se analizarán solo los primeros 100 datos.")
                datos = datos[:100]

            st.success(f"Se analizarán {len(datos)} datos.")

            # Prueba de Shapiro-Wilk
            shapiro_stat, shapiro_p = shapiro(datos)
            interpretacion_sw = "No se rechaza la normalidad ✅" if shapiro_p > alpha else "Se rechaza la normalidad ❌"

            # Prueba de Anderson-Darling
            ad_result = anderson(datos, dist='norm')
            ad_stat = ad_result.statistic
            ad_critical = dict(zip(ad_result.significance_level, ad_result.critical_values))
            ad_interp = "No se rechaza la normalidad ✅" if ad_stat < ad_critical.get(alpha*100, np.inf) else "Se rechaza la normalidad ❌"

            # Prueba de Kolmogorov-Smirnov
            ks_stat, ks_p = kstest(datos, 'norm', args=(np.mean(datos), np.std(datos)))
            interpretacion_ks = "No se rechaza la normalidad ✅" if ks_p > alpha else "Se rechaza la normalidad ❌"

            # Resultados
            st.subheader("📊 Resultados de las pruebas de normalidad")
            st.write(f"**Shapiro-Wilk**: Estadístico = {shapiro_stat:.4f}, p-valor = {shapiro_p:.4f} → {interpretacion_sw}")
            st.write(f"**Anderson-Darling**: Estadístico = {ad_stat:.4f}, valor crítico (α={alpha}) = {ad_critical.get(alpha*100, 'N/A'):.4f} → {ad_interp}")
            st.write(f"**Kolmogorov-Smirnov**: Estadístico = {ks_stat:.4f}, p-valor = {ks_p:.4f} → {interpretacion_ks}")

            # Gráficos
            st.subheader("📈 Gráficos")
            fig, ax = plt.subplots(1, 3, figsize=(15, 4))
            sns.histplot(datos, kde=True, ax=ax[0])
            ax[0].set_title("Histograma")
            sns.boxplot(x=datos, ax=ax[1])
            ax[1].set_title("Boxplot")
            probplot(datos, dist="norm", plot=ax[2])
            ax[2].set_title("Q-Q Plot")
            st.pyplot(fig)

            # Generar documento Word
            doc = Document()
            doc.add_heading("Informe de Pruebas de Normalidad", 0)
            doc.add_paragraph(f"Nivel de significancia seleccionado: {alpha}")
            doc.add_paragraph(f"Shapiro-Wilk: Estadístico = {shapiro_stat:.4f}, p-valor = {shapiro_p:.4f} → {interpretacion_sw}")
            doc.add_paragraph(f"Anderson-Darling: Estadístico = {ad_stat:.4f}, valor crítico (α={alpha}) = {ad_critical.get(alpha*100, 'N/A'):.4f} → {ad_interp}")
            doc.add_paragraph(f"Kolmogorov-Smirnov: Estadístico = {ks_stat:.4f}, p-valor = {ks_p:.4f} → {interpretacion_ks}")
            buffer_word = BytesIO()
            doc.save(buffer_word)
            buffer_word.seek(0)
            st.download_button("📄 Descargar informe en Word", data=buffer_word, file_name="informe_normalidad.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

            # Generar PDF
            class PDF(FPDF):
                def __init__(self):
                    super().__init__()
                    self.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf', uni=True)
                    self.set_font('DejaVu', '', 12)
                    self.set_auto_page_break(auto=True, margin=15)

            pdf = PDF()
            pdf.add_page()
            pdf.set_font("DejaVu", "", 14)
            pdf.cell(0, 10, "Informe de Pruebas de Normalidad", ln=True, align="C")
            pdf.ln(10)
            pdf.set_font("DejaVu", "", 12)
            pdf.cell(0, 10, f"Nivel de significancia seleccionado: {alpha}", ln=True)
            pdf.ln(5)
            pdf.multi_cell(0, 10, f"📊 Shapiro-Wilk:\nEstadístico = {shapiro_stat:.4f}, p-valor = {shapiro_p:.4f} → {interpretacion_sw}")
            pdf.multi_cell(0, 10, f"📊 Anderson-Darling:\nEstadístico = {ad_stat:.4f}, valor crítico (α={alpha}) = {ad_critical.get(alpha*100, 'N/A'):.4f} → {ad_interp}")
            pdf.multi_cell(0, 10, f"📊 Kolmogorov-Smirnov:\nEstadístico = {ks_stat:.4f}, p-valor = {ks_p:.4f} → {interpretacion_ks}")
            pdf.ln(5)
            pdf.multi_cell(0, 10, "Conclusión: Se realizó una evaluación rigurosa de normalidad utilizando tres pruebas estadísticas con un nivel de significancia ajustable. Los resultados sugieren la aceptación o el rechazo de la hipótesis de normalidad en función de los valores-p obtenidos y los umbrales críticos.")

            pdf_buffer = BytesIO()
            pdf.output(pdf_buffer)
            pdf_buffer.seek(0)
            st.download_button("📄 Descargar informe en PDF", data=pdf_buffer, file_name="informe_normalidad.pdf", mime="application/pdf")
