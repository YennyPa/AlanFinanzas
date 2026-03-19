import streamlit as st
import pandas as pd
import requests

# --- TUS ENLACES ---
URL_CONTENIDO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=0&single=true&output=csv"
URL_USUARIOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=83033184&single=true&output=csv"

st.set_page_config(page_title="Reto Financiero", page_icon="💰", layout="centered")

# Función para cargar y LIMPIAR datos
@st.cache_data(ttl=60)
def cargar_datos(url):
    df = pd.read_csv(url)
    # Limpieza extrema de nombres de columnas
    df.columns = [str(c).strip().replace(" ", "_") for c in df.columns]
    return df

# --- ACCESO ---
if 'autenticado' not in st.session_state:
    st.title("🛡️ Acceso al Reto")
    email_input = st.text_input("Ingresa tu correo:").lower().strip()
    
    if st.button("Entrar"):
        try:
            df_users = cargar_datos(URL_USUARIOS)
            user_row = df_users[df_users['Email'].str.lower().str.strip() == email_input]
            
            if not user_row.empty:
                # Buscamos 'Estado_Calculado' sin importar mayúsculas
                estado = str(user_row.iloc[0].get('Estado_Calculado', 'INACTIVO')).upper().strip()
                if "ACTIVO" in estado:
                    st.session_state['autenticado'] = True
                    st.session_state['usuario_nombre'] = user_row.iloc[0]['Nombre_Completo']
                    st.session_state['usuario_email'] = email_input
                    st.rerun()
                else:
                    st.error(f"Tu acceso está {estado}. Contacta a tu Coach.")
            else:
                st.warning("Correo no encontrado.")
        except Exception as e:
            st.error(f"Revisa los encabezados de la hoja Usuarios: {e}")

# --- CONTENIDO ---
else:
    st.sidebar.write(f"Hola, {st.session_state['usuario_nombre']} 👋")
    if st.sidebar.button("Cerrar Sesión"):
        del st.session_state['autenticado']
        st.rerun()

    try:
        df_content = cargar_datos(URL_CONTENIDO)
        # Filtramos Día 2
        pasos = df_content[df_content['Dia'] == 2].sort_values('Paso')
        total_pasos = len(pasos)

        if 'indice' not in st.session_state:
            st.session_state.indice = 0

        fila = pasos.iloc[st.session_state.indice]
        
        # Barra de progreso
        st.progress((st.session_state.indice + 1) / total_pasos)
        
        # Mostrar Contenido
        st.header(fila.get('Titulo', 'Sin Título'))
        st.subheader(fila.get('Subtitulo', ''))
        
        with st.container(border=True):
            # Usamos .get por si acaso el nombre falla
            texto = fila.get('Teoria_Tarea', 'No hay texto en esta lámina')
            st.write(texto)
            
            # Mostrar Audio si existe
            audio = fila.get('Audio_URL')
            if pd.notna(audio) and str(audio).startswith('http'):
                st.audio(audio)

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
                    st.session_state.indice += 1
                    st.rerun()
            else:
                st.success("¡Día 2 Completado! 🎉")

    except Exception as e:
        st.error(f"Error al mostrar contenido: {e}")
