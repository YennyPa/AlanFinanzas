import streamlit as st
import pandas as pd
import requests
import re

# --- CONFIGURACIÓN ---
URL_CONTENIDO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=0&single=true&output=csv"
URL_USUARIOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=83033184&single=true&output=csv"
URL_RESPUESTAS_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=1626466961&single=true&output=csv"
URL_SCRIPT_RESPUESTAS = "https://script.google.com/macros/s/AKfycbzC0gS3sMZpY0H63ad60ufa0hF1vZ9FjKsRyamXGTNYJrBfReU-Hi9VS8uwFnakDKiL9g/exec"
URL_LOGO = "https://raw.githubusercontent.com/YennyPa/AlanFinanzas/main/Logo.png"

st.set_page_config(page_title="Alan Finanzas", page_icon="💰", layout="centered")

# --- FUNCIONES DE APOYO ---
def corregir_url_drive(url):
    """Convierte links de Google Drive en links reproducibles para Streamlit"""
    if 'drive.google.com' in str(url):
        match = re.search(r'id=([-\w]+)|/d/([-\w]+)', url)
        if match:
            file_id = match.group(1) or match.group(2)
            return f"https://www.google.com/get_video_info?docid={file_id}" 
            # Si el anterior falla, el estándar es este:
            # return f"https://drive.google.com/uc?export=download&id={file_id}"
    return url

@st.cache_data(ttl=5)
def cargar_datos(url):
    try:
        df = pd.read_csv(url)
        df.columns = [str(c).strip().lower().replace(" ", "").replace("_", "") for c in df.columns]
        return df
    except: return pd.DataFrame()

# --- INICIALIZACIÓN ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'resp_temporales' not in st.session_state: st.session_state.resp_temporales = []
if 'indice' not in st.session_state: st.session_state.indice = 0

# --- DISEÑO ---
st.markdown("""
    <style>
    .stApp { background-color: #FDFEFE; }
    .dia-banner { background-color: #457B9D; color: white; text-align: center; padding: 12px; border-radius: 10px; font-size: 22px; font-weight: bold; }
    .titulo-finanzas { font-size: 26px !important; font-weight: bold; color: #8B5A2B; margin-top: 15px; }
    .texto-finanzas { font-size: 18px !important; line-height: 1.6; color: #2E4053; }
    </style>
    """, unsafe_allow_html=True)

# --- FLUJO ---
if not st.session_state.autenticado:
    st.image(URL_LOGO, width=200)
    st.title("Acceso al Reto")
    email_input = st.text_input("Correo:").lower().strip()
    if st.button("Entrar"):
        df_users = cargar_datos(URL_USUARIOS)
        if not df_users.empty and email_input in df_users['email'].values:
            st.session_state.autenticado = True
            st.session_state.usuario_email = email_input
            st.session_state.usuario_nombre = df_users[df_users['email'] == email_input]['nombrecompleto'].iloc[0]
            
            # Revisar en qué día quedó (Basado en respuestas guardadas)
            df_resp = cargar_datos(URL_RESPUESTAS_CSV)
            if not df_resp.empty and 'email' in df_resp.columns:
                user_resps = df_resp[df_resp['email'] == email_input]
                st.session_state.dia_actual = int(user_resps['dia'].max() + 1) if not user_resps.empty else 2
            else:
                st.session_state.dia_actual = 2
            st.rerun()
        else: st.error("No registrado.")

else:
    df_content = cargar_datos(URL_CONTENIDO)
    pasos = df_content[df_content['dia'] == st.session_state.dia_actual].sort_values('paso')
    
    if pasos.empty:
        st.success("¡Día completado! No hay más contenido.")
        if st.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()
    else:
        fila = pasos.iloc[st.session_state.indice]
        
        # Header
        col1, col2 = st.columns([1, 1])
        with col1: st.image(URL_LOGO, width=120)
        with col2: st.write(f"Hola, **{st.session_state.usuario_nombre}**")

        st.markdown(f'<div class="dia-banner">☀️ Día {st.session_state.dia_actual}</div>', unsafe_allow_html=True)
        st.markdown(f"<div class='titulo-finanzas'>{fila.get('titulo', '')}</div>", unsafe_allow_html=True)
        st.markdown(f"**{fila.get('subtitulo', '')}**")
        
        t_final = str(fila.get('teoriatarea','')).replace('\n', '<br>')
        st.markdown(f"<div class='texto-finanzas'>{t_final}</div>", unsafe_allow_html=True)
        
        # MOSTRAR VIDEO (Con corrección de link de Drive)
        if pd.notna(fila.get('videourl')):
            video_link = corregir_url_drive(fila.get('videourl'))
            st.video(video_link)

        if pd.notna(fila.get('audiourl')):
            st.audio(fila.get('audiourl'))

        resp_u = ""
        if str(fila.get('tipoinput','')).lower() == 'texto':
            resp_u = st.text_area("Tu respuesta:", key=f"p_{st.session_state.dia_actual}_{st.session_state.indice}")

        # NAVEGACIÓN
        es_ultimo = st.session_state.indice == len(pasos) - 1
        if st.button("Siguiente ➡️" if not es_ultimo else "Finalizar Día"):
            st.session_state.resp_temporales.append({
                "email": str(st.session_state.usuario_email),
                "dia": int(st.session_state.dia_actual),
                "paso": int(fila['paso']),
                "respuesta": str(resp_u)
            })
            
            if not es_ultimo:
                st.session_state.indice += 1
                st.rerun()
            else:
                with st.spinner('Guardando...'):
                    for r in st.session_state.resp_temporales:
                        requests.post(URL_SCRIPT_RESPUESTAS, json=r, timeout=10)
                st.balloons()
                st.session_state.dia_actual += 1
                st.session_state.indice = 0
                st.session_state.resp_temporales = []
                st.rerun()
