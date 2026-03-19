import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN DE LINKS ---
URL_CONTENIDO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=0&single=true&output=csv"
URL_USUARIOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=83033184&single=true&output=csv"

st.set_page_config(page_title="Reto Financiero", page_icon="💰")

# Función para cargar datos
@st.cache_data(ttl=300) # Se actualiza cada 5 min
def cargar_datos(url):
    return pd.read_csv(url)

# --- LÓGICA DE ACCESO ---
if 'autenticado' not in st.session_state:
    st.title("🛡️ Acceso al Reto")
    email_input = st.text_input("Ingresa tu correo registrado:").lower().strip()
    
    if st.button("Entrar"):
        try:
            df_users = cargar_datos(URL_USUARIOS)
            # Buscamos el correo en la columna 'Email'
            user_row = df_users[df_users['Email'].str.lower() == email_input]
            
            if not user_row.empty:
                # Revisamos la columna 'Estado_Calculado' (la de tu fórmula)
                estado = user_row.iloc[0]['Estado_Calculado']
                if estado == "ACTIVO":
                    st.session_state['autenticado'] = True
                    st.session_state['usuario_nombre'] = user_row.iloc[0]['Nombre_Completo']
                    st.session_state['usuario_email'] = email_input
                    st.rerun()
                else:
                    st.error("⏳ Tu acceso ha expirado. Contacta a tu Coach.")
            else:
                st.warning("🚫 Correo no encontrado. Verifica con tu Coach.")
        except Exception as e:
            st.error("Hubo un problema al conectar con la base de datos.")

# --- APP PRINCIPAL (CONTENIDO) ---
else:
    st.sidebar.title(f"Hola, {st.session_state['usuario_nombre']} 👋")
    if st.sidebar.button("Cerrar Sesión"):
        del st.session_state['autenticado']
        st.rerun()

    try:
        df_content = cargar_datos(URL_CONTENIDO)
        # Filtramos solo el Día 2 para esta prueba
        pasos = df_content[df_content['Dia'] == 2].sort_values('Paso')
        total_pasos = len(pasos)

        if 'indice' not in st.session_state:
            st.session_state.indice = 0

        # Mostrar progreso
        progreso = (st.session_state.indice + 1) / total_pasos
        st.progress(progreso)
        
        # Datos del paso actual
        fila = pasos.iloc[st.session_state.indice]
        
        st.header(f"{fila['Titulo']}")
        st.subheader(fila['Subtitulo'])
        
        # Contenedor de la Teoría/Tarea
        with st.container(border=True):
            st.markdown(fila['Teoria_Tarea'])
            
            # Si hay audio, lo mostramos
            if pd.notna(fila['Audio_URL']) and str(fila['Audio_URL']).startswith('http'):
                st.audio(fila['Audio_URL'])

        # Navegación
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.session_state.indice > 0:
                if st.button("⬅️ Anterior"):
                    st.session_state.indice -= 1
                    st.rerun()
        
        with col2:
            if st.session_state.indice < total_pasos - 1:
                if st.button("Siguiente ➡️"):
                    st.session_state.indice += 1
                    st.rerun()
            else:
                st.success("¡Completaste el Día 2! 🎉")
                # Aquí podrías poner el botón de WhatsApp final

    except:
        st.error("No se pudo cargar el contenido. Revisa tu hoja de 'Contenido'.")
