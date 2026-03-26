import streamlit as st
import pandas as pd
import requests

# --- CONFIGURACIÓN DE DATOS ---
URL_CONTENIDO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=0&single=true&output=csv"
URL_USUARIOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=83033184&single=true&output=csv"
# Si aún no tienes este CSV de respuestas, la app usará el Día 1 por defecto
URL_RESPUESTAS_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=716546769&single=true&output=csv"
URL_SCRIPT_RESPUESTAS = "https://script.google.com/macros/s/AKfycbzC0gS3sMZpY0H63ad60ufa0hF1vZ9FjKsRyamXGTNYJrBfReU-Hi9VS8uwFnakDKiL9g/exec"
URL_LOGO = "https://raw.githubusercontent.com/YennyPa/AlanFinanzas/main/Logo.png"

st.set_page_config(page_title="Alan Finanzas - Reto", page_icon="💰", layout="centered")

# --- DISEÑO MINIMALISTA Y BOUTIQUE ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #FDFEFE; }}
    .dia-banner {{
        background-color: #457B9D;
        color: white;
        text-align: center;
        padding: 15px;
        border-radius: 12px;
        font-size: 26px;
        font-weight: bold;
        margin-bottom: 25px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
    }}
    .titulo-finanzas {{ font-size: 32px !important; font-weight: bold; color: #8B5A2B; margin-bottom: 10px; }}
    .texto-finanzas {{ font-size: 19px !important; line-height: 1.8; color: #2E4053; }}
    .stButton>button {{ 
        border-radius: 20px; 
        font-weight: bold; 
        background-color: #457B9D; 
        color: white;
        padding: 10px 25px;
    }}
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=10)
def cargar_datos(url):
    try:
        df = pd.read_csv(url)
        df.columns = [str(c).strip().lower().replace(" ", "").replace("_", "") for c in df.columns]
        return df
    except:
        return pd.DataFrame()

def enviar_a_google(payload):
    try:
        requests.post(URL_SCRIPT_RESPUESTAS, json=payload, timeout=10)
        return True
    except:
        return False

# --- LÓGICA DE NAVEGACIÓN ---
if 'autenticado' not in st.session_state:
    # Intento de cargar logo con Plan B
    try:
        st.image(URL_LOGO, width=200)
    except:
        st.title("💰 Alan Finanzas")
    
    st.title("Acceso al Reto")
    email_input = st.text_input("Ingresa tu correo:").lower().strip()
    
    if st.button("Entrar al Reto"):
        df_users = cargar_datos(URL_USUARIOS)
        if not df_users.empty and email_input in df_users['email'].values:
            st.session_state.autenticado = True
            st.session_state.usuario_email = email_input
            st.session_state.usuario_nombre = df_users[df_users['email'] == email_input]['nombrecompleto'].iloc[0]
            
            # Detectar progreso
            df_resp = cargar_datos(URL_RESPUESTAS_CSV)
            if not df_resp.empty and 'email' in df_resp.columns:
                user_data = df_resp[df_resp['email'] == email_input]
                st.session_state.dia_actual = int(user_data['dia'].max() + 1) if not user_data.empty else 1
            else:
                st.session_state.dia_actual = 1
            
            st.session_state.indice = 0
            st.session_state.respuestas_del_dia = []
            st.rerun()
        else:
            st.error("Correo no registrado o error de conexión.")

else:
    df_content = cargar_datos(URL_CONTENIDO)
    pasos = df_content[df_content['dia'] == st.session_state.dia_actual].sort_values('paso')
    
    if pasos.empty:
        st.balloons()
        st.success(f"¡Has completado todo el contenido disponible por ahora! ✨")
        if st.button("Cerrar Sesión"):
            del st.session_state['autenticado']
            st.rerun()
    else:
        fila = pasos.iloc[st.session_state.indice]

        # Cabecera con Logo
        c1, c2 = st.columns([1, 1])
        with c1:
            try: st.image(URL_LOGO, width=120)
            except: st.write("💰 **Alan Finanzas**")
        with c2: 
            st.write(f"Hola, **{st.session_state['usuario_nombre']}** 👋")

        st.divider() 
        st.markdown(f'<div class="dia-banner">☀️ Día {st.session_state.dia_actual}</div>', unsafe_allow_html=True)

        # Contenido
        st.markdown(f"<div class='titulo-finanzas'>{fila.get('titulo', '')}</div>", unsafe_allow_html=True)
        texto_limpio = str(fila.get('teoriatarea', '')).replace('\n', '<br>')
        st.markdown(f"<div class='texto-finanzas'>{texto_limpio}</div>", unsafe_allow_html=True)
        
        if pd.notna(fila.get('audiourl')) and str(fila.get('audiourl')).startswith('http'):
            st.audio(fila.get('audiourl'))

        resp_usuario = ""
        if str(fila.get('tipoinput', '')).lower() == 'texto':
            st.write("---")
            resp_usuario = st.text_area("Tu reflexión consciente:", key=f"p_{st.session_state.dia_actual}_{st.session_state.indice}", height=150)

        # Botón de Siguiente / Finalizar
        es_ultimo = st.session_state.indice == len(pasos) - 1
        
        if st.button("Siguiente ➡️" if not es_ultimo else "✅ Guardar y Finalizar Día"):
            # Guardamos la respuesta en la lista temporal
            st.session_state.respuestas_del_dia.append({
                "email": st.session_state.usuario_email,
                "dia": st.session_state.dia_actual,
                "paso": fila['paso'],
                "respuesta": resp_usuario
            })
            
            if not es_ultimo:
                st.session_state.indice += 1
                st.rerun()
            else:
                with st.spinner('Integrando tus respuestas...'):
                    # Enviamos todas una por una a Google
                    for resp in st.session_state.respuestas_del_dia:
                        enviar_a_google(resp)
                
                st.balloons()
                st.session_state.dia_actual += 1
                st.session_state.indice = 0
                st.session_state.respuestas_del_dia = []
                st.rerun()
