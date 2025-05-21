# normalidad_app.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
import io
from docx import Document
from docx.shared import Inches
from fpdf import FPDF

# Configurar la página
st.set_page_config(page_title="Prueba de Normalidad", layout="wide")
st.title("📈 Análisis de Normalidad para Datos Cuantitativos")

# -----------------------
# Carga del archivo
# -----------------------
st.sidebar.header("📂 Cargar archivo")
archivo = st.sidebar.file_uploader("Carga un archivo Excel o CSV", type=["xlsx", "csv"])

if archivo:
    # -----------------------
    # Verificar si tiene encabezado
    # -----------------------
    tiene_encabezado = st.sidebar.checkbox("¿El archivo tiene encabezado?", value=True)

    # Leer el archivo
    if archivo.name.endswith("csv"):
        df = pd.read_csv(archivo, header=0 if tiene_encabezado else None)
    else:
        df = pd.read_excel(archivo, header=0 if tiene_encabezado else None)

    st.subheader("Vista previa de los datos cargados")
    st.dataframe(df.head())

    # -----------------------
    # Selección de columna
    # -----------------------
    columnas_numericas = df.select_dtypes(include=np.number).columns.tolist()
    columna = st.selectbox("Selecciona la columna de datos numéricos a analizar", columnas_numericas)

    if columna:
        datos = df[columna].dropna()

        if len(datos) < 3:
            st.error("⚠️ Se requieren al menos 3 datos válidos para realizar las pruebas.")
            st.stop()

        # -----------------------
        # Selección del nivel de significancia
        # -----------------------
        st.subheader("⚙️ Configuración del análisis")
        nivel_lista = st.selectbox("Selecciona el nivel de significancia", [0.10, 0.05, 0.01], index=1)
        nivel_manual = st.number_input("... o ingresa otro nivel de significancia (entre 0.001 y 0.20)", 
                                       min_value=0.001, max_value=0.20, value=nivel_lista, step=0.001, format="%.3f")
        alpha = nivel_manual

        # -----------------------
        # Pruebas de normalidad
        # -----------------------
        st.subheader("📊 Resultados de las pruebas de normalidad")

        shapiro_stat, shapiro_p = stats.shapiro(datos)
        anderson = stats.anderson(datos, dist='norm')
        ks_stat, ks_p = stats.kstest(datos, 'norm', args=(datos.mean(), datos.std()))

        # Interpretaciones
        interpretacion_sw = "No se rechaza la normalidad ✅" if shapiro_p > alpha else "Se rechaza la normalidad ❌"
        interpretacion_ks = "No se rechaza la normalidad ✅" if ks_p > alpha else "Se rechaza la normalidad ❌"

        st.write("**Shapiro-Wilk:**")
        st.write(f"Estadístico: {shapiro_stat:.4f}, Valor-p: {shapiro_p:.4f} → {interpretacion_sw}")

        st.write("**Anderson-Darling:**")
        st.write(f"Estadístico: {anderson.statistic:.4f}")
        for i in range(len(anderson.critical_values)):
            st.write(f"  Nivel {anderson.significance_level[i]:.1f}%: {anderson.critical_values[i]:.4f}")
        interpretacion_ad = "❌ Se rechaza la normalidad" if anderson.statistic > anderson.critical_values[2] else "✅ No se rechaza la normalidad"
        st.write(f"→ {interpretacion_ad}")

        st.write("**Kolmogorov-Smirnov:**")
        st.write(f"Estadístico: {ks_stat:.4f}, Valor-p: {ks_p:.4f} → {interpretacion_ks}")

        # -----------------------
        # Gráficos
        # -----------------------
        st.subheader("📈 Gráficos")
        fig, axs = plt.subplots(1, 3, figsize=(18, 5))

        sns.histplot(datos, kde=True, ax=axs[0], color='skyblue')
        axs[0].set_title("Histograma con KDE")

        sns.boxplot(x=datos, ax=axs[1], color='lightgreen')
        axs[1].set_title("Boxplot")

        stats.probplot(datos, dist="norm", plot=axs[2])
        axs[2].set_title("Q-Q Plot")

        st.pyplot(fig)

        # -----------------------
        # Exportar informe Word
        # -----------------------
        doc = Document()
        doc.add_heading('Informe de Prueba de Normalidad', 0)

        doc.add_paragraph(f"Nivel de significancia utilizado: {alpha:.3f}")
        doc.add_paragraph(f"Se analizaron {len(datos)} datos de la columna '{columna}'.")

        doc.add_heading('Resultados:', level=1)
        doc.add_paragraph(f"Shapiro-Wilk: Estadístico = {shapiro_stat:.4f}, p-valor = {shapiro_p:.4f} → {interpretacion_sw}")
        doc.add_paragraph(f"Anderson-Darling: Estadístico = {anderson.statistic:.4f} → {interpretacion_ad}")
        doc.add_paragraph("Valores críticos: " + ", ".join(f"{val:.4f}" for val in anderson.critical_values))
        doc.add_paragraph(f"Kolmogorov-Smirnov: Estadístico = {ks_stat:.4f}, p-valor = {ks_p:.4f} → {interpretacion_ks}")

        # Guardar el gráfico como imagen temporal para el informe
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        doc.add_picture(img_buffer, width=Inches(6))

        # Descargar Word
        word_buffer = io.BytesIO()
        doc.save(word_buffer)
        word_buffer.seek(0)
        st.download_button("📄 Descargar informe Word", word_buffer, file_name="informe_normalidad.docx")

        # -----------------------
        # Exportar informe PDF
        # -----------------------
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Informe de Prueba de Normalidad", ln=True, align='C')
        pdf.ln(10)

        pdf.multi_cell(0, 10, txt=(
            f"Nivel de significancia utilizado: {alpha:.3f}\n"
            f"Se analizaron {len(datos)} datos de la columna '{columna}'.\n\n"
            f"Shapiro-Wilk: Estadístico = {shapiro_stat:.4f}, p-valor = {shapiro_p:.4f} → {interpretacion_sw}\n"
            f"Anderson-Darling: Estadístico = {anderson.statistic:.4f} → {interpretacion_ad}\n"
            f"Kolmogorov-Smirnov: Estadístico = {ks_stat:.4f}, p-valor = {ks_p:.4f} → {interpretacion_ks}"
        ))

        # Descargar PDF
        pdf_buffer = io.BytesIO()
        pdf.output(pdf_buffer)
        pdf_buffer.seek(0)
        st.download_button("📄 Descargar informe PDF", pdf_buffer, file_name="informe_normalidad.pdf")
