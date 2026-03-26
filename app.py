import streamlit as st
import pandas as pd
import requests
import re

# --- CONFIGURACIÓN ---
URL_CONTENIDO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=0&single=true&output=csv"
URL_USUARIOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=83033184&single=true&output=csv"
URL_RESPUESTAS_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=1626466961&single=true&output=csv"
URL_SCRIPT_RESPUESTAS = "https://script.google.com/macros/s/AKfycbzC0gS3sMZpY0H63ad60ufa0hF1vZ9FjKsRyamXGTNYJrBfReU-Hi9VS8uwFnakDKiL9g/exec"
# URL DE POSTIMAGES (Enlace Directo)
URL_LOGO = "https://i.postimg.cc/0NTk41C9/logo.png"

st.set_page_config(page_title="Alan Finanzas", page_icon="💰", layout="centered")

# --- FUNCIONES ---
def obtener_embed_video(url):
    if 'drive.google.com' in str(url):
        match = re.search(r'/d/([-\w]+)', url) or re.search(r'id=([-\w]+)', url)
        if match:
            file_id = match.group(1) or match.group(2)
            return f'<iframe src="https://drive.google.com/file/d/{file_id}/preview" width="100%" height="360" frameborder="0" allow="autoplay"></iframe>'
    return None

@st.cache_data(ttl=2)
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

# --- ESTILO BOUTIQUE ---
st.markdown("""
    <style>
    .stApp { background-color: #FDFEFE; }
    .dia-banner { background-color: #457B9D; color: white; text-align: center; padding: 15px; border-radius: 12px; font-size: 24px; font-weight: bold; margin-bottom: 20px; }
    .titulo-finanzas { font-size: 28px !important; font-weight: bold; color: #8B5A2B; }
    .texto-finanzas { font-size: 18px !important; line-height: 1.7; color: #2E4053; }
    .stButton>button { border-radius: 20px; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- FLUJO ---
if not st.session_state.autenticado:
    st.image(URL_LOGO, width=150)
    st.title("Alan Finanzas")
    email_i = st.text_input("Ingresa tu correo registrado:").lower().strip()
    
    if st.button("Entrar al Reto"):
        df_u = cargar_datos(URL_USUARIOS)
        if not df_u.empty and email_i in df_u['email'].values:
            st.session_state.autenticado = True
            st.session_state.usuario_email = email_i
            st.session_state.usuario_nombre = df_u[df_u['email'] == email_i]['nombrecompleto'].iloc[0]
            
            # DETERMINAR DÍA ACTUAL (Lógica de ocultar completados)
            df_r = cargar_datos(URL_RESPUESTAS_CSV)
            if not df_r.empty and 'email' in df_r.columns:
                mis_resp = df_r[df_r['email'] == email_i]
                st.session_state.dia_actual = int(mis_resp['dia'].max() + 1) if not mis_resp.empty else 1
            else:
                st.session_state.dia_actual = 1
            st.rerun()
        else: st.error("Usuario no encontrado.")

else:
    df_c = cargar_datos(URL_CONTENIDO)
    pasos = df_c[df_c['dia'] == st.session_state.dia_actual].sort_values('paso')
    
    # Header Limpio
    c1, c2 = st.columns([1, 4])
    with c1: st.image(URL_LOGO, width=80)
    with c2: st.subheader(f"Hola, {st.session_state.usuario_nombre}")

    if pasos.empty:
        st.balloons()
        st.markdown(f'<div class="dia-banner">✨ ¡Día {st.session_state.dia_actual - 1} Completado!</div>', unsafe_allow_html=True)
        st.write("Tu registro de hoy ha sido guardado con éxito. El contenido del siguiente día se habilitará automáticamente cuando procesemos tu avance.")
        if st.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()
    else:
        fila = pasos.iloc[st.session_state.indice]
        st.markdown(f'<div class="dia-banner">☀️ Día {st.session_state.dia_actual}</div>', unsafe_allow_html=True)
        
        st.markdown(f"<div class='titulo-finanzas'>{fila.get('titulo', '')}</div>", unsafe_allow_html=True)
        st.markdown(f"**{fila.get('subtitulo', '')}**")
        
        c_html = str(fila.get('teoriatarea','')).replace('\n', '<br>')
        st.markdown(f"<div class='texto-finanzas'>{c_html}</div>", unsafe_allow_html=True)
        
        # Multimedia
        v_url = fila.get('videourl')
        if pd.notna(v_url):
            embed = obtener_embed_video(v_url)
            if embed: st.components.v1.html(embed, height=380)
        
        if pd.notna(fila.get('audiourl')): st.audio(fila.get('audiourl'))

        # Input Reflexivo
        resp_val = ""
        if str(fila.get('tipoinput','')).lower() == 'texto':
            resp_val = st.text_area("Tu reflexión:", key=f"in_{st.session_state.dia_actual}_{st.session_state.indice}")

        # Navegación
        col_izq, col_der = st.columns(2)
        with col_der:
            es_fin = st.session_state.indice == len(pasos) - 1
            if st.button("Siguiente ➡️" if not es_fin else "Enviar y Finalizar"):
                st.session_state.resp_temporales.append({
                    "email": str(st.session_state.usuario_email),
                    "dia": int(st.session_state.dia_actual),
                    "paso": int(fila['paso']),
                    "respuesta": str(resp_val)
                })
                
                if not es_fin:
                    st.session_state.indice += 1
                    st.rerun()
                else:
                    with st.spinner('Guardando en tu bitácora...'):
                        for r in st.session_state.resp_temporales:
                            requests.post(URL_SCRIPT_RESPUESTAS, json=r, timeout=10)
                    st.session_state.dia_actual += 1
                    st.session_state.indice = 0
                    st.session_state.resp_temporales = []
                    st.rerun()
        with col_izq:
            if st.session_state.indice > 0:
                if st.button("⬅️ Anterior"):
                    st.session_state.indice -= 1
                    st.session_state.resp_temporales.pop()
                    st.rerun()
