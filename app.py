import streamlit as st
import pandas as pd
import requests
import json

# --- CONFIGURACIÓN DE DATOS ---
URL_CONTENIDO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=0&single=true&output=csv"
URL_USUARIOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=83033184&single=true&output=csv"

# URL de tu Google Apps Script (Verificada)
URL_SCRIPT_RESPUESTAS = "https://script.google.com/macros/s/AKfycbyzYGMKECbmRDinL-FkjlRbs7H88CCFGujNSb96WMI3IaKNEt2Nqg2t87M06ejhuabSTg/exec"

# URL del Logo
URL_LOGO = "https://raw.githubusercontent.com/YennyPa/AlanFinanzas/main/Logo.png"

st.set_page_config(page_title="Alan Finanzas - Reto", page_icon="💰", layout="centered")

# --- DISEÑO (CSS) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #FDFEFE; }}
    .dia-banner {{
        background-color: #457B9D;
        color: white;
        text-align: center;
        padding: 10px;
        border-radius: 10px;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
    }}
    .titulo-finanzas {{ font-size: 32px !important; font-weight: bold; color: #8B5A2B; }}
    .texto-finanzas {{ font-size: 21px !important; line-height: 1.7; color: #2E4053; }}
    .stButton>button {{ border-radius: 12px; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=10)
def cargar_datos(url):
    df = pd.read_csv(url)
    df.columns = [str(c).strip().lower().replace(" ", "").replace("_", "") for c in df.columns]
    return df

def enviar_a_excel(email, dia, paso, respuesta):
    payload = {
        "email": str(email), 
        "dia": int(dia), 
        "paso": int(paso), 
        "respuesta": str(respuesta)
    }
    try:
        # Enviamos como JSON para que Google Apps Script lo reciba sin problemas
        requests.post(URL_SCRIPT_RESPUESTAS, json=payload, timeout=10)
    except Exception as e:
        pass # Silenciamos el error para no interrumpir al usuario

# --- FLUJO ---
if 'autenticado' not in st.session_state:
    st.image(URL_LOGO, width=220)
    st.title("Acceso al Reto")
    email_input = st.text_input("Ingresa tu correo:").lower().strip()
    if st.button("Entrar al Reto"):
        df_users = cargar_datos(URL_USUARIOS)
        user_row = df_users[df_users['email'].str.lower().str.strip() == email_input]
        if not user_row.empty:
            st.session_state.autenticado = True
            st.session_state.usuario_nombre = user_row.iloc[0]['nombrecompleto']
            st.session_state.usuario_email = email_input
            st.rerun()
        else:
            st.error("Correo no registrado.")

else:
    df_content = cargar_datos(URL_CONTENIDO)
    pasos = df_content[df_content['dia'] == 2].sort_values('paso')
    if 'indice' not in st.session_state: st.session_state.indice = 0
    
    if st.session_state.indice < len(pasos):
        fila = pasos.iloc[st.session_state.indice]

        # Cabecera
        c1, c2 = st.columns([1, 1])
        with c1: st.image(URL_LOGO, width=140)
        with c2: 
            st.write(f"Hola, **{st.session_state['usuario_nombre']}** 👋")
            if st.button("Cerrar Sesión"):
                del st.session_state['autenticado']
                st.rerun()

        st.divider() 
        st.markdown('<div class="dia-banner">☀️ Día 2</div>', unsafe_allow_html=True)

        # Contenido
        st.markdown(f"<div class='titulo-finanzas'>{fila.get('titulo', '')}</div>", unsafe_allow_html=True)
        texto_final = str(fila.get('teoriatarea', '')).replace('\n', '<br>')
        st.markdown(f"<div class='texto-finanzas'>{texto_final}</div>", unsafe_allow_html=True)
        
        resp_usuario = ""
        es_obligatorio = str(fila.get('tipoinput', '')).lower() == 'texto'
        
        if es_obligatorio:
            st.write("---")
            resp_usuario = st.text_area("Escribe tu reflexión aquí (obligatorio):", key=f"in_{st.session_state.indice}", height=180).strip()
        
        if pd.notna(fila.get('audiourl')) and str(fila.get('audiourl')).startswith('http'):
            st.audio(fila.get('audiourl'))

        # Navegación
        st.write(" ")
        col_prev, col_next = st.columns([1, 1])
        with col_prev:
            if st.session_state.indice > 0:
                if st.button("⬅️ Anterior"):
                    st.session_state.indice -= 1
                    st.rerun()
                    
        with col_next:
            es_ultimo = st.session_state.indice == len(pasos) - 1
            texto_btn = "✅ ¡Terminar Día 2!" if es_ultimo else "Siguiente ➡️"
            if st.button(texto_btn):
                if es_obligatorio and not resp_usuario:
                    st.error("⚠️ Por favor, completa tu reflexión antes de continuar.")
                else:
                    if resp_usuario:
                        enviar_a_excel(st.session_state.usuario_email, 2, fila['paso'], resp_usuario)
                    
                    if not es_ultimo:
                        st.session_state.indice += 1
                        st.rerun()
                    else:
                        st.balloons()
                        st.success("¡Excelente trabajo! Tus respuestas han sido guardadas.")
