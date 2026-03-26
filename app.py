import streamlit as st
import pandas as pd
import requests

# --- CONFIGURACIÓN DE DATOS ---
URL_CONTENIDO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=0&single=true&output=csv"
URL_USUARIOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=83033184&single=true&output=csv"
# IMPORTANTE: Publica tu pestaña de 'Respuestas' como CSV y pega el link aquí:
URL_RESPUESTAS_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=1626466961&single=true&output=csv"
URL_SCRIPT_RESPUESTAS = "https://script.google.com/macros/s/AKfycbzC0gS3sMZpY0H63ad60ufa0hF1vZ9FjKsRyamXGTNYJrBfReU-Hi9VS8uwFnakDKiL9g/exec"
URL_LOGO = "https://raw.githubusercontent.com/YennyPa/AlanFinanzas/main/Logo.png"

st.set_page_config(page_title="Alan Finanzas - Reto", page_icon="💰", layout="centered")

# --- RECUPERANDO TU DISEÑO ORIGINAL ---
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

@st.cache_data(ttl=5)
def cargar_datos(url):
    try:
        df = pd.read_csv(url)
        df.columns = [str(c).strip().lower().replace(" ", "").replace("_", "") for c in df.columns]
        return df
    except: return pd.DataFrame()

def enviar_final(respuestas_lista):
    # Esta función envía todas las respuestas acumuladas una tras otra
    exito = True
    for r in respuestas_lista:
        try:
            requests.post(URL_SCRIPT_RESPUESTAS, json=r, timeout=10)
        except: exito = False
    return exito

# --- FLUJO ---
if 'autenticado' not in st.session_state:
    st.image(URL_LOGO, width=220)
    st.title("Acceso al Reto")
    email_input = st.text_input("Ingresa tu correo:").lower().strip()
    if st.button("Entrar al Reto"):
        df_users = cargar_datos(URL_USUARIOS)
        if not df_users.empty and email_input in df_users['email'].values:
            st.session_state.autenticado = True
            st.session_state.usuario_email = email_input
            st.session_state.usuario_nombre = df_users[df_users['email'] == email_input]['nombrecompleto'].iloc[0]
            
            # Detectar progreso (Día actual)
            df_resp = cargar_datos(URL_RESPUESTAS_CSV)
            if not df_resp.empty and 'email' in df_resp.columns:
                dias_hechos = df_resp[df_resp['email'] == email_input]['dia'].unique()
                st.session_state.dia_actual = int(max(dias_hechos) + 1) if len(dias_hechos) > 0 else 1
            else:
                st.session_state.dia_actual = 1
            
            st.session_state.respuestas_temp = [] # Aquí guardaremos lo del día antes de enviar
            st.rerun()
        else:
            st.error("Correo no registrado.")

else:
    df_content = cargar_datos(URL_CONTENIDO)
    pasos = df_content[df_content['dia'] == st.session_state.dia_actual].sort_values('paso')
    
    if 'indice' not in st.session_state: st.session_state.indice = 0
    
    if st.session_state.indice < len(pasos):
        fila = pasos.iloc[st.session_state.indice]

        # Cabecera
        c1, c2 = st.columns([1, 1])
        with c1: st.image(URL_LOGO, width=140)
        with c2: st.write(f"Hola, **{st.session_state['usuario_nombre']}** 👋")

        st.divider() 
        st.markdown(f'<div class="dia-banner">☀️ Día {st.session_state.dia_actual}</div>', unsafe_allow_html=True)

        # Contenido
        st.markdown(f"<div class='titulo-finanzas'>{fila.get('titulo', '')}</div>", unsafe_allow_html=True)
        texto_final = str(fila.get('teoriatarea', '')).replace('\n', '<br>')
        st.markdown(f"<div class='texto-finanzas'>{texto_final}</div>", unsafe_allow_html=True)
        
        if pd.notna(fila.get('audiourl')): st.audio(fila.get('audiourl'))

        resp_usuario = ""
        if str(fila.get('tipoinput', '')).lower() == 'texto':
            st.write("---")
            resp_usuario = st.text_area("Tu reflexión:", key=f"p_{st.session_state.indice}", height=150)

        # Navegación
        col_prev, col_next = st.columns([1, 1])
        with col_next:
            es_ultimo = st.session_state.indice == len(pasos) - 1
            if st.button("Siguiente ➡️" if not es_ultimo else "✅ Finalizar Día"):
                # Guardamos localmente (sin enviar a Google todavía)
                st.session_state.respuestas_temp.append({
                    "email": st.session_state.usuario_email,
                    "dia": int(st.session_state.dia_actual),
                    "paso": int(fila['paso']),
                    "respuesta": resp_usuario
                })
                
                if not es_ultimo:
                    st.session_state.indice += 1
                    st.rerun()
                else:
                    with st.spinner('Guardando todo el día...'):
                        enviar_final(st.session_state.respuestas_temp)
                    st.balloons()
                    st.success(f"¡Día {st.session_state.dia_actual} completado!")
                    st.session_state.dia_actual += 1
                    st.session_state.indice = 0
                    st.session_state.respuestas_temp = []
                    st.rerun()
