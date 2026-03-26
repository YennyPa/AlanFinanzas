import streamlit as st
import pandas as pd
import requests

# --- CONFIGURACIÓN DE RUTAS ---
URL_CONTENIDO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=0&single=true&output=csv"
URL_USUARIOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=83033184&single=true&output=csv"
URL_RESPUESTAS_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=1626466961&single=true&output=csv"
URL_SCRIPT_RESPUESTAS = "https://script.google.com/macros/s/AKfycbzC0gS3sMZpY0H63ad60ufa0hF1vZ9FjKsRyamXGTNYJrBfReU-Hi9VS8uwFnakDKiL9g/exec"
URL_LOGO = "https://raw.githubusercontent.com/YennyPa/AlanFinanzas/main/Logo.png"

st.set_page_config(page_title="Alan Finanzas - Reto", page_icon="💰", layout="centered")

# --- 1. INICIALIZACIÓN DE VARIABLES (Anti-AttributeError) ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'resp_temporales' not in st.session_state:
    st.session_state.resp_temporales = []
if 'indice' not in st.session_state:
    st.session_state.indice = 0
if 'dia_actual' not in st.session_state:
    st.session_state.dia_actual = 2

# --- 2. DISEÑO VISUAL (Estética Boutique) ---
st.markdown("""
    <style>
    .stApp { background-color: #FDFEFE; }
    .dia-banner { 
        background-color: #457B9D; 
        color: white; 
        text-align: center; 
        padding: 15px; 
        border-radius: 12px; 
        font-size: 24px; 
        font-weight: bold; 
        margin-bottom: 20px; 
    }
    .titulo-finanzas { font-size: 28px !important; font-weight: bold; color: #8B5A2B; margin-bottom: 10px; }
    .texto-finanzas { font-size: 18px !important; line-height: 1.6; color: #2E4053; }
    .stButton>button { border-radius: 20px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=5)
def cargar_datos(url):
    try:
        df = pd.read_csv(url)
        df.columns = [str(c).strip().lower().replace(" ", "").replace("_", "") for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# --- 3. FLUJO DE PANTALLAS ---

if not st.session_state.autenticado:
    # Pantalla de Login
    try:
        st.image(URL_LOGO, width=220)
    except:
        st.title("💰 Alan Finanzas")
    
    st.subheader("Acceso al Reto de 30 Días")
    email_input = st.text_input("Ingresa tu correo registrado:").lower().strip()
    
    if st.button("Comenzar el viaje"):
        df_users = cargar_datos(URL_USUARIOS)
        if not df_users.empty and email_input in df_users['email'].values:
            st.session_state.autenticado = True
            st.session_state.usuario_email = email_input
            st.session_state.usuario_nombre = df_users[df_users['email'] == email_input]['nombrecompleto'].iloc[0]
            
            # Detectar progreso desde el Excel de Respuestas
            df_resp = cargar_datos(URL_RESPUESTAS_CSV)
            if not df_resp.empty and 'email' in df_resp.columns:
                user_resps = df_resp[df_resp['email'] == email_input]
                st.session_state.dia_actual = int(user_resps['dia'].max() + 1) if not user_resps.empty else 2
            else:
                st.session_state.dia_actual = 2 # Por defecto empezamos en Día 2 si está vacío
            
            st.rerun()
        else:
            st.error("Lo siento, ese correo no está en nuestra lista de alumnos.")

else:
    # Pantalla de Contenido
    df_content = cargar_datos(URL_CONTENIDO)
    pasos = df_content[df_content['dia'] == st.session_state.dia_actual].sort_values('paso')
    
    if pasos.empty:
        st.success("✨ ¡Has completado todo el contenido disponible por ahora!")
        if st.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()
    else:
        fila = pasos.iloc[st.session_state.indice]
        
        # Header de usuario
        col1, col2 = st.columns([1, 1])
        with col1: 
            try: st.image(URL_LOGO, width=120)
            except: st.write("💰 **Alan Finanzas**")
        with col2: st.write(f"Hola, **{st.session_state.usuario_nombre}** 👋")

        st.divider()
        st.markdown(f'<div class="dia-banner">☀️ Día {st.session_state.dia_actual} - Paso {fila["paso"]}</div>', unsafe_allow_html=True)

        # Título y Texto (Data Viz Style)
        st.markdown(f"<div class='titulo-finanzas'>{fila.get('titulo', '')}</div>", unsafe_allow_html=True)
        t_limpio = str(fila.get('teoriatarea','')).replace('\n', '<br>')
        st.markdown(f"<div class='texto-finanzas'>{t_limpio}</div>", unsafe_allow_html=True)
        
        if pd.notna(fila.get('audiourl')):
            st.audio(fila.get('audiourl'))

        # Input de reflexión
        resp_u = ""
        if str(fila.get('tipoinput','')).lower() == 'texto':
            st.write("---")
            resp_u = st.text_area("Comparte tu reflexión aquí:", key=f"input_{st.session_state.dia_actual}_{st.session_state.indice}", height=150)

        # --- NAVEGACIÓN Y ENVÍO (Anti-TypeError) ---
        es_ultimo = st.session_state.indice == len(pasos) - 1
        
        if st.button("Siguiente ➡️" if not es_ultimo else "✅ Finalizar el Día"):
            # 1. Empaquetar datos con tipos nativos de Python (Crucial para evitar errores)
            nuevo_registro = {
                "email": str(st.session_state.usuario_email),
                "dia": int(st.session_state.dia_actual),
                "paso": int(fila['paso']),
                "respuesta": str(resp_u)
            }
            
            # 2. Guardar en memoria temporal
            st.session_state.resp_temporales.append(nuevo_registro)
            
            if not es_ultimo:
                st.session_state.indice += 1
                st.rerun()
            else:
                # 3. Envío masivo a Google Sheets al terminar el día
                with st.spinner('Guardando tu progreso en la bitácora...'):
                    for r in st.session_state.resp_temporales:
                        try:
                            requests.post(URL_SCRIPT_RESPUESTAS, json=r, timeout=10)
                        except:
                            pass # Silenciamos errores individuales para no romper la experiencia
                
                st.balloons()
                st.success(f"¡Felicidades! Has completado el Día {st.session_state.dia_actual}")
                
                # Preparar para el siguiente día
                st.session_state.dia_actual += 1
                st.session_state.indice = 0
                st.session_state.resp_temporales = []
                st.rerun()
