import streamlit as st
import requests
import pandas as pd
import datetime
import os

# =============================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA MÓVIL (ÍCONO CORPORATIVO Y ANTI-INACTIVIDAD)
# =============================================================================
icono_pestana = "logoBlumare.ico"

if not os.path.exists(icono_pestana):
    icono_pestana = "logoBlumare.jpeg"

st.set_page_config(
    page_title="Blumare - Despachos",
    page_icon=icono_pestana if os.path.exists(icono_pestana) else "🚚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Inyección de estilos CSS PREMIUM y código JavaScript Keep-Alive
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    div[data-testid="stToolbar"] { visibility: hidden !important; }
    
    /* Fondo general oscuro de la App */
    .stApp {
        background-color: #090c10;
        background-image: radial-gradient(circle at 50% 0%, #161b22 0%, #090c10 70%);
    }

    /* Animación de entrada suave para las tarjetas */
    @keyframes slideUpFade {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Tarjetas de entregas (Verdadero Glassmorphism Premium) */
    .delivery-card {
        background: linear-gradient(145deg, rgba(22, 27, 34, 0.7), rgba(13, 17, 23, 0.8));
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 22px;
        margin-bottom: 5px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        animation: slideUpFade 0.6s ease-out both;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .delivery-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0, 240, 255, 0.08);
        border: 1px solid rgba(0, 240, 255, 0.2);
    }

    /* Badges de estado refinados */
    .badge-pendiente {
        background: linear-gradient(135deg, rgba(241, 196, 15, 0.15), rgba(243, 156, 18, 0.2));
        color: #f1c40f;
        padding: 6px 14px;
        border-radius: 30px;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.5px;
        border: 1px solid rgba(241, 196, 15, 0.4);
        box-shadow: 0 0 10px rgba(241, 196, 15, 0.1);
    }

    /* Ajuste para TODOS los botones (Gradiente Esmeralda Premium) */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 0px !important;
        font-weight: 800 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        font-size: 13px !important;
        box-shadow: 0 6px 15px rgba(56, 239, 125, 0.25) !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(56, 239, 125, 0.4) !important;
    }
    div.stButton > button:active {
        transform: translateY(1px) !important;
    }

    /* Estilización de las métricas superiores */
    [data-testid="stMetricValue"] {
        color: #00f0ff !important;
        font-weight: 900 !important;
        text-shadow: 0 0 15px rgba(0, 240, 255, 0.3);
    }
    [data-testid="stMetricLabel"] {
        color: #8b949e !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 12px !important;
    }
    
    /* Inputs y buscadores */
    .stTextInput > div > div > input {
        background-color: rgba(22, 27, 34, 0.6) !important;
        border: 1px solid #30363d !important;
        border-radius: 10px !important;
        color: white !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #00f0ff !important;
        box-shadow: 0 0 10px rgba(0, 240, 255, 0.2) !important;
    }
    </style>
    
    <iframe src="about:blank" style="display:none;" id="anti-idle-iframe"></iframe>
    <script>
        setInterval(function() {
            var iframe = document.getElementById('anti-idle-iframe');
            if (iframe) {
                iframe.src = 'about:blank?keepalive=' + Date.now();
                console.log("Blumare Keep-Alive: Conexión refrescada.");
            }
        }, 300000); 
    </script>
    """, unsafe_allow_html=True)

URL_API = "https://script.google.com/macros/s/AKfycbys2ymG2Ad5av2jtR3LFttFiJPkQS2LfiOGwuw7-RynhbuPvEE9R5G90xeS_bofoi-CCg/exec"

# =============================================================================
# LOGO DE LA APP Y ENCABEZADO
# =============================================================================
nombre_logo = "logoBlumare.jpeg"

if os.path.exists(nombre_logo):
    import base64
    with open(nombre_logo, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; margin-top: 15px; margin-bottom: 10px;">
            <img src="data:image/jpeg;base64,{encoded_string}" width="110" style="border-radius: 18px; box-shadow: 0 8px 20px rgba(0,0,0,0.4);">
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.error(f"⚠️ Archivo del logo no detectado.")

# Títulos con Gradiente Metálico Premium
st.markdown("<h1 style='text-align: center; font-weight: 900; margin-bottom: 0; font-size: 32px; background: -webkit-linear-gradient(45deg, #ffffff, #00f0ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>BLUMARE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8b949e; font-weight: 800; letter-spacing: 4px; margin-top: 0; font-size: 11px;'>LOGÍSTICA Y DESPACHOS</p>", unsafe_allow_html=True)

# Línea separadora difuminada
st.markdown("<div style='height: 1px; background: linear-gradient(90deg, transparent, #30363d, transparent); margin: 25px 0;'></div>", unsafe_allow_html=True)

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

def registrar_entrega_en_sheets(id_venta):
    try:
        ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        url_actualizar = f"{URL_API}?tipo_operacion=ActualizarEstado&id_venta={id_venta}&nuevo_estado=Entregado&hora_entrega={ahora}"
        respuesta = requests.get(url_actualizar, timeout=10)
        
        if respuesta.status_code == 200:
            st.toast(f"¡Pedido #{id_venta} marcado como Entregado! 🎉", icon="✅")
            st.cache_data.clear() 
            st.rerun()
        else:
            st.error("La central recibió la orden pero no pudo actualizar la fila.")
    except Exception as e:
        st.error(f"Error al comunicar la entrega: {e}")

datos_crudos = descargar_datos_despacho()

if not datos_crudos:
    st.warning("No se recibieron datos de la central o la lista de despachos está vacía.")
else:
    df_base = pd.DataFrame(datos_crudos)
    
    df = pd.DataFrame()
    df['id_venta'] = df_base[0].astype(str).str.strip()
    df['fecha'] = df_base[1].astype(str)
    df['direccion'] = df_base[2].astype(str)
    df['cliente'] = df_base[3].astype(str)
    df['producto'] = df_base[4].astype(str)
    df['cantidad_kgs'] = pd.to_numeric(df_base[6], errors='coerce').fillna(0.0)
    df['estado'] = df_base[10].astype(str).str.strip()
    df['repartidor'] = df_base[2].astype(str)

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

        st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

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
        # 6. HOJA DE RUTA EN TIEMPO REAL
        # =============================================================================
        st.markdown("<h3 style='color: #8b949e; font-size: 12px; font-weight: bold; letter-spacing: 2px; margin-top: 20px; margin-bottom: 15px;'>📍 HOJA DE RUTA EN TIEMPO REAL</h3>", unsafe_allow_html=True)
        
        df_pendientes = df[df['estado'].str.lower() != 'entregado']

        if df_pendientes.empty:
            st.success("¡Felicidades! 🎉 Todas las entregas del día han sido completadas.")
        else:
            # Añadimos un pequeño retraso en la animación (delay) según el índice para efecto cascada
            for index, fila in df_pendientes.iterrows():
                id_v = fila['id_venta']
                estado = fila['estado']
                clase_badge = "badge-pendiente"
                delay = (index % 10) * 0.1 # Efecto cascada
                
                # HTML mejorado para la tarjeta
                card_html = f"""
                <div class="delivery-card" style="animation-delay: {delay}s;">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <span style="font-family: 'Courier New', Courier, monospace; color: #58a6ff; font-size: 11px; font-weight: bold; background: rgba(88, 166, 255, 0.1); padding: 3px 8px; border-radius: 6px;">#{id_v}</span>
                            <h4 style="color: white; margin: 8px 0 0 0; font-size: 19px; font-weight: 800; letter-spacing: -0.5px;">{fila['cliente']}</h4>
                        </div>
                        <span class="{clase_badge}">{estado.upper()}</span>
                    </div>
                    <div style="margin-top: 18px; border-top: 1px dashed rgba(255,255,255,0.1); padding-top: 15px; font-size: 14px;">
                        <p style="margin: 0 0 8px 0; color: #c9d1d9;">📦 <span style="color: #8b949e; font-size: 12px; text-transform: uppercase;">Producto:</span> <br><b>{fila['producto']}</b> — <span style="color: #00f0ff; font-weight: 900; font-size: 16px; text-shadow: 0 0 8px rgba(0,240,255,0.4);">{fila['cantidad_kgs']} KGS</span></p>
                        <p style="margin: 0; color: #c9d1d9;">📍 <span style="color: #8b949e; font-size: 12px; text-transform: uppercase;">Destino:</span> <br><b>{fila['direccion']}</b></p>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 20px; font-size: 11px; color: #8b949e; font-weight: 600; margin-bottom: 10px;">
                        <span>🏢 Repartidor: <span style="color: #c9d1d9;">{fila['repartidor']}</span></span>
                        <span>📅 <span style="color: #c9d1d9;">{fila['fecha']}</span></span>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
                
                if st.button(f"CONFIRMAR ENTREGA", key=f"btn_{id_v}_{index}"):
                    registrar_entrega_en_sheets(id_v)
                
                st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

# =============================================================================
# 7. BOTÓN MANUAL DE REFRESCAR
# =============================================================================
st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
if st.button("🔄 SINCRONIZAR DATOS AHORA", key="btn_global_refresh"):
    st.cache_data.clear()
    st.rerun()
