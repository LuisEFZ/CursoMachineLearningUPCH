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

    # Verificación: ¿es columna numérica?
    if not pd.api.types.is_numeric_dtype(df[columna]):
        st.error("⚠️ La columna seleccionada no contiene datos numéricos.")
        st.stop()

    datos = df[columna].dropna().astype(float).values[:100]
    st.write(f"Se analizarán **{len(datos)} datos**.")

    if len(datos) < 3:
        st.warning("Se requieren al menos 3 datos numéricos para realizar las pruebas.")
        st.stop()
