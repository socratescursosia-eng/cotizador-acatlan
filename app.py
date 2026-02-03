import streamlit as st
import fitz  # PyMuPDF
import numpy as np
import pandas as pd

# --- IDENTIDAD INSTITUCIONAL ---
st.set_page_config(page_title="FES Acatlán - Cotizador IA", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #F4F7F9; }
    .stButton>button { background-color: #002060; color: #CFAC46; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ FAC - Sistema de Precisión Web")
st.subheader("Despliegue de Agentes de IA para el D")

# --- TABLA DE PRECIOS (TU CEREBRO DE DATOS) ---
tabla_precios = {
    "Plóter 60x90": {"Color": [30, 45, 50, 60, 70, 80, 90, 100, 120, 150, 200], "B&N": [18, 22.5, 25, 35, 45, 60, 76.5, 85, 102, 127.5, 170]},
    "Plóter 60x45": {"Color": [25, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120], "B&N": [15, 17.5, 22.5, 37.5, 45, 52.5, 60, 67.5, 75, 82.5, 102]},
    "Doble Carta": {"Color": [8, 8, 10, 10, 10, 12, 12, 14, 14.5, 15, 16], "B&N": [2, 2, 2, 5.5, 7.5, 9, 9, 10.5, 11, 11.5, 12]},
    "Carta/Oficio": {"Color": [5, 5, 6, 6, 6, 7, 7, 8, 9, 10, 11], "B&N": [1, 1, 1, 3, 4, 5, 5, 5.5, 6, 7, 8]}
}

# --- INTERFAZ DE USUARIO ---
with st.sidebar:
    st.header("Configuración")
    formato = st.selectbox("Selecciona Formato:", list(tabla_precios.keys()))
    modo = st.radio("Modo de Impresión:", ["Color", "B&N"])

archivo = st.file_uploader("Subir archivo PDF para análisis", type=["pdf"])

if archivo:
    st.info("🤖 **Agente Receptor:** Archivo recibido. Iniciando análisis...")
    
    doc = fitz.open(stream=archivo.read(), filetype="pdf")
    total_final = 0
    resultados = []

    for i in range(len(doc)):
        # --- AGENTE DE VISIÓN ---
        page = doc[i]
        pix = page.get_pixmap(colorspace=fitz.csCMYK)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, 4)
        tac = (np.mean(img[:,:,0]) + np.mean(img[:,:,1]) + np.mean(img[:,:,2]) + np.mean(img[:,:,3])) / 2.55
        pico_k = np.percentile(img[:,:,3], 95) / 2.55

        # --- AGENTE FINANCIERO (REGLA DE ORO) ---
        if tac > 136.01 or pico_k > 85:
            idx = 10
            cat = "Crítica (Saturada)"
        else:
            idx = min(int((tac / 136.01) * 11), 10)
            cat = "Baja" if idx < 3 else ("Media" if idx < 7 else "Alta")
        
        costo = tabla_precios[formato][modo][idx]
        total_final += costo
        resultados.append([i+1, f"{tac:.1f}%", cat, f"${costo:.2f}"])

    # --- AGENTE AUDITOR ---
    st.success(f"✅ **Agente Auditor:** Análisis completado para {len(doc)} páginas.")
    df = pd.DataFrame(resultados, columns=["Página", "Densidad TAC", "Categoría", "Precio"])
    st.table(df)
    
    st.metric("TOTAL A COBRAR", f"${total_final:.2f}")

st.markdown("---")
st.caption("Realización  | Supervisión  | Revisó ")
