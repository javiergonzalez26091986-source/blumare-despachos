import streamlit as st
import requests
import pandas as pd
import datetime
import os

# =============================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA MÓVIL (ÍCONO CORPORATIVO Y ANTI-INACTIVIDAD)
# =============================================================================
# Nombre del archivo para el ícono de la pestaña (Favicon)
icono_pestana = "logoBlumare.ico"

# Si por alguna razón no encuentra el .ico, usamos el .jpeg como respaldo
if not os.path.exists(icono_pestana):
    icono_pestana = "logoBlumare.jpeg"

st.set_page_config(
    page_title="Blumare - Despachos",
    page_icon=icono_pestana if os.path.exists(icono_pestana) else "🚚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Inyección de estilos CSS - ESTILO ENTERPRISE/MINIMALISTA Y OCULTAMIENTO TOTAL
st.markdown("""
    <style>
    /* ===================================================================== */
    /* 1. OCULTAR ELEMENTOS NATIVOS DE STREAMLIT Y BARRA SUPERIOR            */
    /* ===================================================================== */
    [data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    .stAppDeployButton { display: none !important; }
    #MainMenu { display: none !important; }
    footer { display: none !important; }

    /* ===================================================================== */
    /* 🔥 2. LA MAGIA PARA OCULTAR TU FOTO DE PERFIL (CREATOR BADGE) 🔥      */
    /* ===================================================================== */
    .viewerBadge_container { display: none !important; }
    .viewerBadge_link { display: none !important; }
    #viewerBadge { display: none !important; }
    #creatorBadge { display: none !important; }
    [data-testid="stAppCreatorBadge"] { display: none !important; }
    [data-testid="stCreatorProfile"] { display: none !important; }
    [data-testid="viewerBadge"] { display: none !important; }

    /* ===================================================================== */
    /* 3. ESTILOS VISUALES DEL DASHBOARD (Slate 900)                         */
    /* ===================================================================== */
    .stApp {
        background-color: #0f172a;
    }

    /* Redefinir la caja de búsqueda */
    .stTextInput > div > div > input {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        color: #f8fafc !important;
        font-size: 14px !important;
        padding: 12px 15px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 1px #3b82f6 !important;
    }

    /* Estilo Flat Moderno para los Botones */
    div.stButton > button {
        width: 100%;
        border-radius: 8px !important;
        padding: 12px 0px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        font-size: 15px !important;
        border: none !important;
        transition: background-color 0.2s ease, transform 0.1s ease !important;
    }

    /* Botón Principal (Confirmar Entrega - Verde Esmeralda Mate) */
    div.stButton > button[kind="primary"] {
        background-color: #10b981 !important;
        color: #ffffff !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #059669 !important;
    }
    div.stButton > button[kind="primary"]:active {
        transform: scale(0.98) !important;
    }

    /* Botón Secundario (Sincronizar - Gris Pizarra) */
    div.stButton > button[kind="secondary"] {
        background-color: #1e293b !important;
        color: #94a3b8 !important;
        border: 1px solid #334155 !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        background-color: #334155 !important;
        color: #f8fafc !important;
    }
    
    /* Toast (Mensajes de éxito nativos) */
    div[data-testid="stToast"] {
        background-color: #1e293b !important;
        border-left: 4px solid #10b981 !important;
    }
    </style>
    
    <iframe src="about:blank" style="display:none;" id="anti-idle-iframe"></iframe>
    <script>
        setInterval(function() {
            var iframe = document.getElementById('anti-idle-iframe');
            if (iframe) {
                iframe.src = 'about:blank?keepalive=' + Date.now();
            }
        }, 300000); 
    </script>
    """, unsafe_allow_html=True)

# URL exacta de tu API de Google Apps Script
URL_API = "https://script.google.com/macros/s/AKfycbys2ymG2Ad5av2jtR3LFttFiJPkQS2LfiOGwuw7-RynhbuPvEE9R5G90xeS_bofoi-CCg/exec"

# =============================================================================
# LOGO DE LA APP (CENTRADO ABSOLUTO Y TAMAÑO AJUSTADO)
# =============================================================================
nombre_logo = "logoBlumare.jpeg"

if os.path.exists(nombre_logo):
    import base64
    with open(nombre_logo, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; margin-bottom: 10px;">
            <img src="data:image/jpeg;base64,{encoded_string}" width="130" style="border-radius: 10px;">
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.error(f"⚠️ Archivo del logo no detectado. Asegúrate de que '{nombre_logo}' esté guardado exactamente en: {os.path.abspath('.')}")

# =============================================================================
# 2. ENCABEZADO DE LA APP
# =============================================================================
st.markdown("<h1 style='text-align: center; color: #898989; margin-bottom: 0;'>BLUMARE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #898989; font-weight: bold; letter-spacing: 2px; margin-top: 0;'>LOGÍSTICA Y DESPACHOS</p>", unsafe_allow_html=True)
st.markdown("---")

# =============================================================================
# 3. CONEXIÓN Y DESCARGA DE DATOS (LECTURA REAL)
# =============================================================================
@st.cache_data(ttl=2)
def descargar_datos_despacho():
    try:
        url_con_parametros = f"{URL_API}?tipo_operacion=ObtenerDespachos"
        respuesta = requests.get(url_con_parametros, timeout=10)
        resultado = respuesta.json()
        
        if isinstance(resultado, list):
            return resultado
        return []
    except Exception as e:
        st.error(f"Error de conexión con la central: {e}")
        return []

# FUNCIÓN PARA REPORTAR LA ENTREGA A GOOGLE SHEETS (ESCRITURA CON HORA)
def registrar_entrega_en_sheets(id_venta):
    try:
        ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        url_actualizar = f"{URL_API}?tipo_operacion=ActualizarEstado&id_venta={id_venta}&nuevo_estado=Entregado&hora_entrega={ahora}"
        respuesta = requests.get(url_actualizar, timeout=10)
        
        if respuesta.status_code == 200:
            st.toast(f"¡Pedido #{id_venta} marcado como Entregado! 🎉", icon="✅")
            st.cache_data.clear() # Limpia el caché inmediatamente para forzar la recarga
            st.rerun()
        else:
            st.error("La central recibió la orden pero no pudo actualizar la fila.")
    except Exception as e:
        st.error(f"Error al comunicar la entrega: {e}")

datos_crudos = descargar_datos_despacho()

if not datos_crudos:
    st.warning("No se recibieron datos de la central o la lista de despachos está vacía.")
else:
    # Procesamiento y Mapeo directo desde la matriz real de Google Sheets
    df_base = pd.DataFrame(datos_crudos)
    
    df = pd.DataFrame()
    df['id_venta'] = df_base[0].astype(str).str.strip()
    df['fecha'] = df_base[1].astype(str)
    df['direccion'] = df_base[2].astype(str)
    df['cliente'] = df_base[3].astype(str)
    df['producto'] = df_base[4].astype(str)
    df['cantidad_kgs'] = pd.to_numeric(df_base[6], errors='coerce').fillna(0.0)
    df['estado'] = df_base[10].astype(str).str.strip()
    df['repartidor'] = df_base[2].astype(str) # Se usa la sede de despacho como Zona de manera predeterminada

    # Filtro de seguridad para remover registros o encabezados vacíos
    df = df[df['id_venta'] != ''].copy()

    if df.empty:
        st.info("No hay registros activos de despacho en este momento.")
    else:
        # =============================================================================
        # 4. METRICAS CLAVE EN TIEMPO REAL
        # =============================================================================
        pendientes = len(df[df['estado'].str.lower() != 'entregado'])
        total_kgs = df['cantidad_kgs'].sum()

        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Envíos Pendientes", value=pendientes)
        with col2:
            st.metric(label="Total Kilos Ruta", value=f"{total_kgs:,.1f} KG")

        st.markdown("##")

        # =============================================================================
        # 5. BUSCADOR INTERACTIVO
        # =============================================================================
        busqueda = st.text_input("🔍 Buscar por Cliente o Producto:", placeholder="Escribe para filtrar la ruta...")

        if busqueda:
            df = df[
                df['cliente'].str.contains(busqueda, case=False) | 
                df['producto'].str.contains(busqueda, case=False)
            ]

        # =============================================================================
        # 6. HOJA DE RUTA EN TIEMPO REAL (FILTRADA: SOLO MUESTRA PENDIENTES)
        # =============================================================================
        st.markdown("<h3 style='color: gray; font-size: 14px; letter-spacing: 1px;'>HOJA DE RUTA EN TIEMPO REAL</h3>", unsafe_allow_html=True)
        
        # Filtramos el DataFrame para que SOLO muestre las ventas que NO estén entregadas
        df_pendientes = df[df['estado'].str.lower() != 'entregado']

        if df_pendientes.empty:
            st.success("¡Felicidades! 🎉 Todas las entregas del día han sido completadas.")
        else:
            for index, fila in df_pendientes.iterrows():
                id_v = fila['id_venta']
                estado = fila['estado']
                clase_badge = "badge-pendiente"
                
                # Renderizado visual de la tarjeta
                card_html = f"""
                <div class="delivery-card">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <span style="font-family: monospace; color: #8b949e; font-size: 11px;">ID VENTA #{id_v}</span>
                            <h4 style="color: white; margin: 4px 0 0 0; font-size: 18px; font-weight: bold;">{fila['cliente']}</h4>
                        </div>
                        <span class="{clase_badge}">{estado.upper()}</span>
                    </div>
                    <div style="margin-top: 15px; border-top: 1px solid #30363d; pt-10px; font-size: 14px;">
                        <p style="margin: 10px 0 5px 0; color: #c9d1d9;">📦 <b>Producto:</b> {fila['producto']} — <span style="color: #00f0ff; font-weight: bold;">{fila['cantidad_kgs']} KGS</span></p>
                        <p style="margin: 5px 0 5px 0; color: #8b949e;">📍 <b>Sede Despacho:</b> {fila['direccion']}</p>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 15px; font-size: 11px; color: #58a6ff; margin-bottom: 5px;">
                        <span>🏢 Zona/Repartidor: {fila['repartidor']}</span>
                        <span>📅 Registro: {fila['fecha']}</span>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
                
                # Habilitamos el botón físico debajo de la tarjeta para confirmar
                if st.button(f"Confirmar Entrega ✅", key=f"btn_{id_v}_{index}"):
                    registrar_entrega_en_sheets(id_v)
                
                st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

# =============================================================================
# 7. BOTÓN MANUAL DE REFRESCAR
# =============================================================================
if st.button("🔄 Sincronizar Datos Ahora", key="btn_global_refresh"):
    st.cache_data.clear()
    st.rerun()
