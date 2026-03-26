import streamlit as st
import pandas as pd
import requests

# --- CONFIGURACIÓN ---
URL_CONTENIDO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=0&single=true&output=csv"
URL_USUARIOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=83033184&single=true&output=csv"
URL_RESPUESTAS_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=1626466961&single=true&output=csv"
URL_SCRIPT_RESPUESTAS = "https://script.google.com/macros/s/AKfycbzC0gS3sMZpY0H63ad60ufa0hF1vZ9FjKsRyamXGTNYJrBfReU-Hi9VS8uwFnakDKiL9g/exec"
URL_LOGO = "https://raw.githubusercontent.com/YennyPa/AlanFinanzas/main/Logo.png"

st.set_page_config(page_title="Alan Finanzas", page_icon="💰", layout="centered")

# --- DISEÑO BOUTIQUE ---
st.markdown("""
    <style>
    .stApp { background-color: #FDFEFE; }
    .dia-banner { background-color: #457B9D; color: white; text-align: center; padding: 15px; border-radius: 12px; font-size: 24px; font-weight: bold; margin-bottom: 20px; }
    .titulo-finanzas { font-size: 28px !important; font-weight: bold; color: #8B5A2B; }
    .texto-finanzas { font-size: 18px !important; line-height: 1.6; color: #2E4053; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=2) # Bajamos el cache para que lea los cambios casi al instante
def cargar_datos(url):
    try:
        df = pd.read_csv(url)
        df.columns = [str(c).strip().lower().replace(" ", "").replace("_", "") for c in df.columns]
        return df
    except: return pd.DataFrame()

# --- ACCESO ---
if 'autenticado' not in st.session_state:
    try: st.image(URL_LOGO, width=200)
    except: st.title("Alan Finanzas")
    
    email_input = st.text_input("Ingresa tu correo:").lower().strip()
    if st.button("Entrar"):
        df_users = cargar_datos(URL_USUARIOS)
        if not df_users.empty and email_input in df_users['email'].values:
            st.session_state.autenticado = True
            st.session_state.usuario_email = email_input
            st.session_state.usuario_nombre = df_users[df_users['email'] == email_input]['nombrecompleto'].iloc[0]
            
            # DETECCIÓN DE PROGRESO MEJORADA
            df_resp = cargar_datos(URL_RESPUESTAS_CSV)
            if not df_resp.empty and 'email' in df_resp.columns:
                user_resps = df_resp[df_resp['email'] == email_input]
                # Si no tiene registros, empezamos en Día 2 (o el que tú definas como inicial)
                st.session_state.dia_actual = int(user_resps['dia'].max() + 1) if not user_resps.empty else 2
            else:
                st.session_state.dia_actual = 2
            
            st.session_state.indice = 0
            st.session_state.resp_temporales = []
            st.rerun()
        else:
            st.error("Correo no registrado.")

else:
    df_content = cargar_datos(URL_CONTENIDO)
    # Filtramos el contenido del día que toca
    pasos = df_content[df_content['dia'] == st.session_state.dia_actual].sort_values('paso')
    
    # Si el día actual no tiene contenido, avisamos
    if pasos.empty:
        st.success("✨ ¡Día completado! No hay más pasos por ahora.")
        if st.button("Cerrar Sesión"):
            del st.session_state['autenticado']
            st.rerun()
    else:
        fila = pasos.iloc[st.session_state.indice]
        
        # Cabecera
        c1, c2 = st.columns([1, 1])
        with c1: st.write(f"☀️ **Día {st.session_state.dia_actual}**")
        with c2: st.write(f"👤 {st.session_state.usuario_nombre}")

        st.markdown(f'<div class="dia-banner">Paso {fila["paso"]}</div>', unsafe_allow_html=True)
        st.markdown(f"<div class='titulo-finanzas'>{fila.get('titulo', '')}</div>", unsafe_allow_html=True)
        
        # Corregimos el salto de línea en el texto
        t_final = str(fila.get('teoriatarea','')).replace('\n', '<br>')
        st.markdown(f"<div class='texto-finanzas'>{t_final}</div>", unsafe_allow_html=True)
        
        if pd.notna(fila.get('audiourl')): st.audio(fila.get('audiourl'))

        resp_u = ""
        if str(fila.get('tipoinput','')).lower() == 'texto':
            resp_u = st.text_area("Tu reflexión:", key=f"p_{st.session_state.indice}", height=150)

        # Navegación
        if st.button("Siguiente ➡️" if st.session_state.indice < len(pasos)-1 else "Terminar Día"):
            st.session_state.resp_temporales.append({
                "email": st.session_state.usuario_email,
                "dia": st.session_state.dia_actual,
                "paso": fila['paso'],
                "respuesta": resp_u
            })
            
            if st.session_state.indice < len(pasos) - 1:
                st.session_state.indice += 1
                st.rerun()
            else:
                with st.spinner('Guardando en tu bitácora...'):
                    for r in st.session_state.resp_temporales:
                        requests.post(URL_SCRIPT_RESPUESTAS, json=r, timeout=10)
                st.balloons()
                st.session_state.dia_actual += 1
                st.session_state.indice = 0
                st.session_state.resp_temporales = []
                st.rerun()
