import streamlit as st
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import io
from docx import Document

st.set_page_config(page_title="Pruebas de Normalidad", layout="centered")

st.title("🧪 Pruebas de Normalidad")
st.write("Sube un archivo Excel o CSV con hasta 100 datos numéricos para analizar si siguen una distribución normal.")

# Subir archivo
archivo = st.file_uploader("Carga tu archivo (.xlsx o .csv)", type=["xlsx", "csv"])

if archivo:
    # Verificar si tiene encabezado
    tiene_encabezado = st.checkbox("¿Tu archivo tiene encabezado?", value=True)

    try:
        if archivo.name.endswith(".csv"):
            df = pd.read_csv(archivo, header=0 if tiene_encabezado else None)
        else:
            df = pd.read_excel(archivo, header=0 if tiene_encabezado else None)
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        st.stop()

    # Seleccionar columna
    columna = st.selectbox("Selecciona la columna de datos", df.columns)

    # Conversión segura a numérico
    datos_raw = pd.to_numeric(df[columna], errors='coerce')  # Convierte errores a NaN
    datos = datos_raw.dropna().astype(float).values[:100]

    st.write(f"Se analizarán **{len(datos)} datos**.")
    
    if len(datos) < 3:
        st.error("⚠️ Se requieren al menos 3 datos válidos para realizar las pruebas.")
        st.stop()

    # Ejecutar pruebas de normalidad
    try:
        shapiro_stat, shapiro_p = stats.shapiro(datos)
        ks_stat, ks_p = stats.kstest(stats.zscore(datos), 'norm')
        ad_result = stats.anderson(datos, dist='norm')
    except Exception as e:
        st.error(f"Error al ejecutar las pruebas estadísticas: {e}")
        st.stop()

    st.subheader("📊 Resultados de las pruebas de normalidad")
    texto_resultado = []

    st.write("**Shapiro-Wilk**")
    st.write(f"Estadístico: {shapiro_stat:.4f}, Valor-p: {shapiro_p:.4f}")
    interpretacion_sw = "No se rechaza la normalidad ✅" if shapiro_p > 0.05 else "Se rechaza la normalidad ❌"
    st.write("→ " + interpretacion_sw)
    texto_resultado.append(f"Shapiro-Wilk: estadístico = {shapiro_stat:.4f}, p = {shapiro_p:.4f} → {interpretacion_sw}")

    st.write("**Kolmogorov-Smirnov** (datos estandarizados)")
    st.write(f"Estadístico: {ks_stat:.4f}, Valor-p: {ks_p:.4f}")
    interpretacion_ks = "No se rechaza la normalidad ✅" if ks_p > 0.05 else "Se rechaza la normalidad ❌"
    st.write("→ " + interpretacion_ks)
    texto_resultado.append(f"Kolmogorov-Smirnov: estadístico = {ks_stat:.4f}, p = {ks_p:.4f} → {interpretacion_ks}")

    st.write("**Anderson-Darling**")
    st.write(f"Estadístico: {ad_result.statistic:.4f}")
    for cv, sig in zip(ad_result.critical_values, ad_result.significance_level):
        st.write(f"Nivel de significancia {sig:.1f}% → Valor crítico: {cv:.4f}")
    if ad_result.statistic < ad_result.critical_values[2]:
        interpretacion_ad = "No se rechaza la normalidad al 5% ✅"
    else:
        interpretacion_ad = "Se rechaza la normalidad al 5% ❌"
    st.write("→ " + interpretacion_ad)
    texto_resultado.append(f"Anderson-Darling: estadístico = {ad_result.statistic:.4f} → {interpretacion_ad}")

    # Q-Q Plot
    st.subheader("📈 Gráfico Q-Q")
    fig, ax = plt.subplots()
    stats.probplot(datos, dist="norm", plot=ax)
    st.pyplot(fig)

    # Exportar a Word
    st.subheader("📤 Exportar informe")
    if st.button("📄 Exportar resultados a Word"):
        doc = Document()
        doc.add_heading("Informe de Pruebas de Normalidad", 0)
        doc.add_paragraph(f"Archivo analizado: {archivo.name}")
        doc.add_paragraph(f"Número de datos analizados: {len(datos)}\n")
        for linea in texto_resultado:
            doc.add_paragraph(linea)

        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        st.download_button(
            label="⬇️ Descargar informe Word",
            data=buffer,
            file_name="resultado_normalidad.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
