import streamlit as st
import pandas as pd

# 1. TUS LINKS (Cámbialos por los links CSV de cada hoja)
URL_CONTENIDO = "TU_LINK_CSV_HOJA_CONTENIDO"
URL_USUARIOS = "TU_LINK_CSV_HOJA_USUARIOS"

st.set_page_config(page_title="Reto Financiero", page_icon="💰")

# Función para leer el Excel publicado
def cargar_datos(url):
    return pd.read_csv(url)

# --- PANTALLA DE ACCESO ---
if 'autenticado' not in st.session_state:
    st.title("Bienvenido al Reto")
    email_input = st.text_input("Ingresa tu correo para comenzar:").lower().strip()
    
    if st.button("Ingresar"):
        try:
            df_users = cargar_datos(URL_USUARIOS)
            # Buscamos al usuario por email
            user_data = df_users[df_users['Email'].str.lower() == email_input]
            
            if not user_data.empty:
                estado = user_data.iloc[0]['Estado_Calculado'] # Aquí lee tu fórmula de Excel
                if estado == "ACTIVO":
                    st.session_state['autenticado'] = True
                    st.session_state['usuario'] = user_data.iloc[0]['Nombre_Completo']
                    st.rerun()
                else:
                    st.error("Tu acceso ha expirado. Contacta a tu Coach.")
            else:
                st.warning("Correo no encontrado. Verifica con tu Coach.")
        except:
            st.error("Error conectando con la base de datos.")
else:
    # --- PANTALLA DEL REEL (Día 2) ---
    st.sidebar.write(f"Hola, {st.session_state['usuario']} 👋")
    if st.sidebar.button("Cerrar Sesión"):
        del st.session_state['autenticado']
        st.rerun()

    # Cargar contenido del Día 2
    df_content = cargar_datos(URL_CONTENIDO)
    pasos_dia_2 = df_content[df_content['Dia'] == 2].sort_values('Paso')
    
    # Navegación del Reel
    if 'paso_actual' not in st.session_state:
        st.session_state.paso_actual = 0

    total_pasos = len(pasos_dia_2)
    fila = pasos_dia_2.iloc[st.session_state.paso_actual]

    # Diseño de la Lámina
    st.progress((st.session_state.paso_actual + 1) / total_pasos)
    st.subheader(f"{fila['Titulo']}")
    st.info(f"**{fila['Subtitulo']}**")
    st.write(fila['Teoria_Tarea'])

    # Navegación entre láminas
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.paso_actual > 0:
            if st.button("⬅️ Anterior"):
                st.session_state.paso_actual -= 1
                st.rerun()
    with col2:
        if st.session_state.paso_actual < total_pasos - 1:
            if st.button("Siguiente ➡️"):
                st.session_state.paso_actual += 1
                st.rerun()
        else:
            st.success("¡Has llegado al final de la lección!")
            st.button("✅ Enviar reporte al Coach (WhatsApp)")
