pip install streamlit pandas scipy matplotlib openpyxl
import streamlit as st
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt

st.title("🧪 Pruebas de Normalidad")
st.write("Sube un archivo Excel o CSV con hasta 100 datos numéricos para analizar si siguen una distribución normal.")

# Subir archivo
archivo = st.file_uploader("Carga tu archivo (.xlsx o .csv)", type=["xlsx", "csv"])

if archivo:
    # Verificar si tiene encabezado
    tiene_encabezado = st.checkbox("¿Tu archivo tiene encabezado?", value=True)

    if archivo.name.endswith(".csv"):
        df = pd.read_csv(archivo, header=0 if tiene_encabezado else None)
    else:
        df = pd.read_excel(archivo, header=0 if tiene_encabezado else None)

    # Seleccionar columna
    columna = st.selectbox("Selecciona la columna de datos", df.columns)

    # Limitar a los primeros 100 datos válidos
    datos = df[columna].dropna().astype(float).values[:100]

    st.write(f"Se analizarán {len(datos)} datos.")

    if len(datos) >= 3:
        # Prueba Shapiro-Wilk
        shapiro_stat, shapiro_p = stats.shapiro(datos)
        # Prueba Kolmogorov-Smirnov (vs normal estándar)
        ks_stat, ks_p = stats.kstest(stats.zscore(datos), 'norm')
        # Prueba Anderson-Darling
        ad_result = stats.anderson(datos, dist='norm')

        st.subheader("📊 Resultados de las pruebas de normalidad")

        st.write("**Shapiro-Wilk**")
        st.write(f"Estadístico: {shapiro_stat:.4f}, Valor-p: {shapiro_p:.4f}")
        st.write("→ " + ("No se rechaza la normalidad ✅" if shapiro_p > 0.05 else "Se rechaza la normalidad ❌"))

        st.write("**Kolmogorov-Smirnov** (datos estandarizados)")
        st.write(f"Estadístico: {ks_stat:.4f}, Valor-p: {ks_p:.4f}")
        st.write("→ " + ("No se rechaza la normalidad ✅" if ks_p > 0.05 else "Se rechaza la normalidad ❌"))

        st.write("**Anderson-Darling**")
        st.write(f"Estadístico: {ad_result.statistic:.4f}")
        for cv, sig in zip(ad_result.critical_values, ad_result.significance_level):
            st.write(f"Nivel de significancia {sig:.1f}% → Valor crítico: {cv:.4f}")
        if ad_result.statistic < ad_result.critical_values[2]:  # 5%
            st.write("→ No se rechaza la normalidad al 5% ✅")
        else:
            st.write("→ Se rechaza la normalidad al 5% ❌")

        # Q-Q plot
        st.subheader("📈 Gráfico Q-Q")
        fig, ax = plt.subplots()
        stats.probplot(datos, dist="norm", plot=ax)
        st.pyplot(fig)
    else:
        st.warning("Se requieren al menos 3 datos numéricos para realizar las pruebas.")
