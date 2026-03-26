import streamlit as st
import pandas as pd
import requests

# --- CONFIGURACIÓN ---
URL_CONTENIDO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=0&single=true&output=csv"
URL_USUARIOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=83033184&single=true&output=csv"
URL_RESPUESTAS_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=716546769&single=true&output=csv" 
URL_SCRIPT_RESPUESTAS = "https://script.google.com/macros/s/AKfycbzC0gS3sMZpY0H63ad60ufa0hF1vZ9FjKsRyamXGTNYJrBfReU-Hi9VS8uwFnakDKiL9g/exec"
URL_LOGO = "https://raw.githubusercontent.com/YennyPa/AlanFinanzas/main/Logo.png"

st.set_page_config(page_title="Alan Finanzas - Reto", page_icon="💰", layout="centered")

@st.cache_data(ttl=5)
def cargar_datos(url):
    try:
        df = pd.read_csv(url)
        df.columns = [str(c).strip().lower().replace(" ", "").replace("_", "") for c in df.columns]
        return df
    except:
        return pd.DataFrame()

def enviar_a_excel(email, dia, paso, respuesta):
    payload = {"email": str(email), "dia": int(dia), "paso": int(paso), "respuesta": str(respuesta)}
    try:
        requests.post(URL_SCRIPT_RESPUESTAS, json=payload, timeout=5)
        return True
    except:
        return False

# --- DETECCIÓN DE PROGRESO ---
def obtener_dia_actual(email):
    df_resp = cargar_datos(URL_RESPUESTAS_CSV)
    if df_resp.empty or 'email' not in df_resp.columns:
        return 1 # Si no hay respuestas, empezamos en el Día 1
    
    # Buscamos el último día registrado para este usuario
    user_resp = df_resp[df_resp['email'].str.lower().str.strip() == email.lower().strip()]
    if user_resp.empty:
        return 1
    
    ultimo_dia = user_resp['dia'].max()
    # Si ya tiene registros del día X, revisamos si terminó todos los pasos (opcionalmente podrías saltar al X+1)
    return int(ultimo_dia)

# --- FLUJO PRINCIPAL ---
if 'autenticado' not in st.session_state:
    st.image(URL_LOGO, width=180)
    st.title("Acceso al Reto")
    email_input = st.text_input("Ingresa tu correo:").lower().strip()
    if st.button("Entrar al Reto"):
        df_users = cargar_datos(URL_USUARIOS)
        if not df_users.empty and email_input in df_users['email'].values:
            st.session_state.autenticado = True
            st.session_state.usuario_email = email_input
            # Detectamos en qué día se quedó
            st.session_state.dia_actual = obtener_dia_actual(email_input)
            st.rerun()
        else:
            st.error("Correo no registrado.")

else:
    df_content = cargar_datos(URL_CONTENIDO)
    # Filtramos por el día que le corresponde al usuario
    pasos = df_content[df_content['dia'] == st.session_state.dia_actual].sort_values('paso')
    
    if 'indice' not in st.session_state: st.session_state.indice = 0
    
    if st.session_state.indice < len(pasos):
        fila = pasos.iloc[st.session_state.indice]
        
        # Interfaz de usuario... (Mantenemos tu diseño de banners y logos)
        st.markdown(f'<div class="dia-banner">☀️ Día {st.session_state.dia_actual}</div>', unsafe_allow_html=True)
        st.markdown(f"### {fila.get('titulo', '')}")
        st.write(fila.get('teoriatarea', '').replace('\n', '\n\n'))
        
        resp_usuario = ""
        if str(fila.get('tipoinput', '')).lower() == 'texto':
            resp_usuario = st.text_area("Tu respuesta:", key=f"res_{st.session_state.indice}")

        if st.button("Siguiente ➡️"):
            if resp_usuario:
                with st.spinner('Guardando...'):
                    enviar_a_excel(st.session_state.usuario_email, st.session_state.dia_actual, fila['paso'], resp_usuario)
            
            if st.session_state.indice < len(pasos) - 1:
                st.session_state.indice += 1
            else:
                # ¡Terminó el día! Pasamos al siguiente
                st.session_state.dia_actual += 1
                st.session_state.indice = 0
                st.balloons()
                st.success(f"¡Día {st.session_state.dia_actual - 1} completado!")
            st.rerun()
