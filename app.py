import streamlit as st
import pandas as pd

# --- ENLACES DE TU GOOGLE SHEETS ---
URL_CONTENIDO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=0&single=true&output=csv"
URL_USUARIOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=83033184&single=true&output=csv"

st.set_page_config(page_title="Reto Financiero", page_icon="💰")

# Función optimizada para leer Google Sheets
@st.cache_data(ttl=60)
def cargar_datos(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip() # Limpia espacios en los nombres de columnas
    return df

# --- PANTALLA DE ACCESO ---
if 'autenticado' not in st.session_state:
    st.title("🛡️ Acceso al Reto")
    email_input = st.text_input("Ingresa tu correo registrado:").lower().strip()
    
    if st.button("Entrar"):
        try:
            df_users = cargar_datos(URL_USUARIOS)
            # Buscamos el correo ignorando mayúsculas y espacios
            user_row = df_users[df_users['Email'].str.lower().str.strip() == email_input]
            
            if not user_row.empty:
                estado = str(user_row.iloc[0]['Estado_Calculado']).strip().upper()
                if estado == "ACTIVO":
                    st.session_state['autenticado'] = True
                    st.session_state['usuario_nombre'] = user_row.iloc[0]['Nombre_Completo']
                    st.session_state['usuario_email'] = email_input
                    st.rerun()
                else:
                    st.error(f"⏳ Acceso: {estado}. Contacta a tu Coach.")
            else:
                st.warning("🚫 Correo no encontrado en la lista de Usuarios.")
        except Exception as e:
            st.error(f"Error de conexión: {e}")

# --- APP PRINCIPAL ---
else:
    st.sidebar.title(f"Hola, {st.session_state['usuario_nombre']} 👋")
    if st.sidebar.button("Cerrar Sesión"):
        del st.session_state['autenticado']
        st.rerun()

    try:
        df_content = cargar_datos(URL_CONTENIDO)
        pasos = df_content[df_content['Dia'] == 2].sort_values('Paso')
        total_pasos = len(pasos)

        if 'indice' not in st.session_state:
            st.session_state.indice = 0

        fila = pasos.iloc[st.session_state.indice]
        
        # Interfaz de Usuario
        st.progress((st.session_state.indice + 1) / total_pasos)
        st.header(f"{fila['Titulo']}")
        st.subheader(fila['Subtitulo'])
        
        with st.container(border=True):
            st.markdown(fila['Teoria_Tarea'])
            
            # Si el paso requiere escribir (Tipo_Input == 'Texto')
            if str(fila.get('Tipo_Input')) == 'Texto':
                # Guardamos la respuesta en memoria antes de mandarla al Excel
                respuesta_key = f"resp_{st.session_state.indice}"
                st.text_area("Escribe tu respuesta aquí:", key=respuesta_key)

        # Navegación
        col1, col2 = st.columns(2)
        with col1:
            if st.session_state.indice > 0:
                if st.button("⬅️ Anterior"):
                    st.session_state.indice -= 1
                    st.rerun()
        with col2:
            if st.session_state.indice < total_pasos - 1:
                if st.button("Siguiente ➡️"):
                    # AQUÍ ES DONDE GUARDAREMOS LA RESPUESTA
                    st.session_state.indice += 1
                    st.rerun()
            else:
                st.success("¡Día 2 Completado!")
                if st.button("🚀 Enviar Todo al Coach"):
                    st.balloons()
                    # Aquí irá el enlace final de WhatsApp con el resumen
    except Exception as e:
        st.error(f"Error al mostrar contenido: {e}")
