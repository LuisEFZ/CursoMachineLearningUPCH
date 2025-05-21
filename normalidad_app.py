# normalidad_app.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
from io import BytesIO
from docx import Document
from docx.shared import Inches
from fpdf import FPDF
import os
import seaborn as sns

# Configuración general
st.set_page_config(page_title="Prueba de Normalidad", layout="centered")
st.title("🧪 Análisis de Normalidad para una Variable Cuantitativa Continua")

# Sección: Cargar archivo
st.header("1. Cargar archivo Excel")
archivo = st.file_uploader("Carga tu archivo .xlsx (máximo 106 datos)", type=["xlsx"])

if archivo is not None:
    # Leer datos y verificar si tiene encabezado
    encabezado = st.checkbox("¿El archivo tiene encabezado?", value=True)
    try:
        df = pd.read_excel(archivo, header=0 if encabezado else None)
        col_numericas = df.select_dtypes(include=[np.number]).columns.tolist()

        if not col_numericas:
            st.error("⚠️ El archivo no contiene columnas numéricas válidas.")
        else:
            columna = st.selectbox("Selecciona la columna numérica a analizar:", col_numericas)
            datos = df[columna].dropna().values

            if len(datos) > 106:
                st.warning("⚠️ Solo se analizarán los primeros 106 datos.")
                datos = datos[:106]

            # Sección: Nivel de significancia
            st.header("2. Selección del nivel de significancia")
            alfa_opcion = st.radio("¿Deseas usar el nivel de significancia por defecto (0.05)?", ("Sí", "No"))
            if alfa_opcion == "No":
                alfa = st.number_input("Ingresa el nivel de significancia (por ejemplo, 0.01, 0.05, 0.10):", min_value=0.001, max_value=0.2, value=0.05, step=0.001)
            else:
                alfa = 0.05

            # Sección: Pruebas de normalidad
            st.header("3. Resultados de las pruebas de normalidad")
            shapiro_stat, shapiro_p = stats.shapiro(datos)
            anderson_result = stats.anderson(datos, dist='norm')
            ks_stat, ks_p = stats.kstest((datos - np.mean(datos)) / np.std(datos), 'norm')

            st.subheader("Prueba de Shapiro-Wilk")
            st.write(f"Estadístico: {shapiro_stat:.4f}, Valor-p: {shapiro_p:.4f}")
            interpretacion_sw = "No se rechaza la normalidad ✅" if shapiro_p > alfa else "Se rechaza la normalidad ❌"
            st.write(interpretacion_sw)

            st.subheader("Prueba de Anderson-Darling")
            st.write(f"Estadístico: {anderson_result.statistic:.4f}")
            for i, (cv, sig) in enumerate(zip(anderson_result.critical_values, anderson_result.significance_level)):
                st.write(f"  - Nivel {sig:.1f}%: Crítico = {cv:.4f} {'✅' if anderson_result.statistic < cv else '❌'}")

            st.subheader("Prueba de Kolmogorov-Smirnov")
            st.write(f"Estadístico: {ks_stat:.4f}, Valor-p: {ks_p:.4f}")
            interpretacion_ks = "No se rechaza la normalidad ✅" if ks_p > alfa else "Se rechaza la normalidad ❌"
            st.write(interpretacion_ks)

            # Sección: Gráficos
            st.header("4. Visualización de los datos")
            fig, axs = plt.subplots(1, 3, figsize=(15, 4))
            sns.histplot(datos, kde=True, ax=axs[0], color="skyblue").set(title="Histograma")
            sns.boxplot(x=datos, ax=axs[1], color="lightgreen").set(title="Boxplot")
            stats.probplot(datos, dist="norm", plot=axs[2])
            axs[2].set_title("Gráfico Q-Q")
            st.pyplot(fig)

            # Sección: Exportar a Word
            st.header("5. Exportar informe")
            if st.button("📄 Descargar informe Word"):
                doc = Document()
                doc.add_heading("Informe de Prueba de Normalidad", level=1)

                doc.add_paragraph(f"Se evaluó la normalidad de la variable '{columna}' con {len(datos)} datos.")
                doc.add_paragraph(f"Nivel de significancia seleccionado: {alfa:.3f}")

                doc.add_heading("Resultados de las pruebas", level=2)
                doc.add_paragraph(f"Shapiro-Wilk: Estadístico = {shapiro_stat:.4f}, Valor-p = {shapiro_p:.4f}. {interpretacion_sw}")
                doc.add_paragraph(f"Anderson-Darling: Estadístico = {anderson_result.statistic:.4f}")
                for sig, cv in zip(anderson_result.significance_level, anderson_result.critical_values):
                    doc.add_paragraph(f"  - Nivel {sig:.1f}%: Crítico = {cv:.4f} {'✅' if anderson_result.statistic < cv else '❌'}")
                doc.add_paragraph(f"Kolmogorov-Smirnov: Estadístico = {ks_stat:.4f}, Valor-p = {ks_p:.4f}. {interpretacion_ks}")

                # Guardar y descargar
                word_buffer = BytesIO()
                doc.save(word_buffer)
                st.download_button(
                    label="📥 Descargar Word",
                    data=word_buffer.getvalue(),
                    file_name="informe_normalidad.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
