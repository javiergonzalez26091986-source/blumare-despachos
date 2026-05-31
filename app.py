import streamlit as st
import requests
import pandas as pd
import datetime
import os
import base64

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

# Inyección de estilos CSS y código JavaScript Keep-Alive
st.markdown("""
    <style>
    /* 1. OCULTAR ELEMENTOS DE STREAMLIT CLOUD */
    [data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    .stAppDeployButton { display: none !important; }
    #MainMenu { display: none !important; }
    footer { display: none !important; }
    
    /* Configuración UI global */
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    
    /* Tarjetas de entregas (Glassmorphism) */
    .delivery-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 5px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }
    
    /* Badges de estado */
    .badge-pendiente {
        background-color: rgba(241, 196, 15, 0.15);
        color: #f1c40f;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        border: 1px solid rgba(241, 196, 15, 0.3);
    }
    
    /* Ajuste para los botones principales */
    div.stButton > button {
        width: 100%;
        background-color: #238636 !important;
        color: white !important;
        border: 1px solid #30853e !important;
        border-radius: 8px !important;
        padding: 6px 0px !important;
        font-weight: bold !important;
    }
    div.stButton > button:hover {
        background-color: #2ea043 !important;
        border-color: #3fb950 !important;
    }
    
    /* Botones secundarios */
    div.stButton > button[kind="secondary"] {
        background-color: #21262d !important;
        border-color: #30363d !important;
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

# Constantes API
URL_API = "https://script.google.com/macros/s/AKfycbys2ymG2Ad5av2jtR3LFttFiJPkQS2LfiOGwuw7-RynhbuPvEE9R5G90xeS_bofoi-CCg/exec"
CLOUDINARY_URL = "https://api.cloudinary.com/v1_1/ddouzzs1i/image/upload"
CLOUDINARY_PRESET = "bluemare_preset"

# Estado de autenticación local
if 'placa_autenticada' not in st.session_state:
    st.session_state.placa_autenticada = None

# =============================================================================
# LOGO DE LA APP
# =============================================================================
nombre_logo = "logoBlumare.jpeg"
if os.path.exists(nombre_logo):
    with open(nombre_logo, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; margin-bottom: 10px;">
            <img src="data:image/jpeg;base64,{encoded_string}" width="130" style="border-radius: 10px;">
        </div>
        """, unsafe_allow_html=True
    )
else:
    st.error(f"Archivo del logo no detectado. Asegúrate de que '{nombre_logo}' esté guardado en el repositorio.")

st.markdown("<h1 style='text-align: center; color: #898989; margin-bottom: 0;'>BLUMARE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #898989; font-weight: bold; letter-spacing: 2px; margin-top: 0;'>LOGÍSTICA Y DESPACHOS</p>", unsafe_allow_html=True)
st.markdown("---")

# =============================================================================
# FUNCIONES DE CONEXIÓN A GOOGLE SHEETS Y CLOUDINARY
# =============================================================================
@st.cache_data(ttl=60)
def descargar_vehiculos():
    try:
        res = requests.get(f"{URL_API}?tipo_operacion=ObtenerVehiculos", timeout=10)
        return res.json() if isinstance(res.json(), list) else []
    except: return []

@st.cache_data(ttl=2)
def descargar_datos_despacho():
    try:
        respuesta = requests.get(f"{URL_API}?tipo_operacion=ObtenerDespachos", timeout=10)
        resultado = respuesta.json()
        return resultado if isinstance(resultado, list) else []
    except Exception as e:
        st.error(f"Error de conexión con la central: {e}")
        return []

def registrar_entrega_en_sheets(id_venta, foto_bytes):
    archivos = {"file": foto_bytes}
    parametros = {"upload_preset": CLOUDINARY_PRESET}
    
    try:
        res_cloud = requests.post(CLOUDINARY_URL, files=archivos, data=parametros, timeout=15)
        
        if res_cloud.status_code == 200:
            link_foto = res_cloud.json().get("secure_url", "")
            
            ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            url_actualizar = (
                f"{URL_API}?tipo_operacion=ActualizarEstado"
                f"&id_venta={id_venta}"
                f"&nuevo_estado=Entregado"
                f"&hora_entrega={ahora}"
                f"&soporte_entrega={link_foto}"
            )
            respuesta = requests.get(url_actualizar, timeout=10)
            if respuesta.status_code == 200:
                st.toast(f"Pedido #{id_venta} marcado como Entregado", icon="✅")
                st.cache_data.clear() 
                st.rerun()
            else:
                st.error("La central recibió la imagen, pero no pudo actualizar el archivo maestro.")
        else:
            try:
                mensaje_servidor = res_cloud.json().get("error", {}).get("message", res_cloud.text)
            except:
                mensaje_servidor = res_cloud.text
            st.error(f"Error de Cloudinary: {mensaje_servidor}")
            
    except Exception as ex:
        st.error(f"Fallo de conexión de red al intentar subir el soporte: {str(ex)}")

# =============================================================================
# LÓGICA DE INTERFAZ: PANTALLA DE INICIO DE SESIÓN VS. PANEL DE REPARTOS
# =============================================================================
if st.session_state.placa_autenticada is None:
    # --- PANTALLA DE ACCESO ---
    st.markdown("<h3 style='text-align: center; color: white;'>AUTENTICACIÓN DE VEHÍCULO</h3>", unsafe_allow_html=True)
    placas_validas = descargar_vehiculos()
    
    if not placas_validas:
        st.warning("Cargando base de datos de vehículos...")
    else:
        placa_seleccionada = st.selectbox("Seleccione su Placa Asignada:", ["Seleccione su vehículo"] + placas_validas)
        # Uso del icon nativo de Material Design para Streamlit
        if st.button("Ingresar a la Ruta", icon=":material/login:"):
            if placa_seleccionada != "Seleccione su vehículo":
                st.session_state.placa_autenticada = placa_seleccionada
                st.rerun()
            else:
                st.error("Debe seleccionar una placa de la lista.")
else:
    # --- PANEL DE REPARTOS Y RUTAS ---
    col_info, col_logout = st.columns([7, 3])
    with col_info:
        st.markdown(f"<span style='color:#3fb950;'>●</span> Vehículo Activo: **{st.session_state.placa_autenticada}**", unsafe_allow_html=True)
    with col_logout:
        # Icono corporativo de salida
        if st.button("Cerrar Sesión", type="secondary", icon=":material/logout:"):
            st.session_state.placa_autenticada = None
            st.rerun()
            
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
        
        def extraer_placa(fila):
            try: return str(fila[12]).strip().upper()
            except: return ""
            
        df['placa'] = df_base.apply(extraer_placa, axis=1)

        # Limpiamos filas vacías
        df = df[df['id_venta'] != ''].copy()

        if df.empty:
            st.info("No hay registros activos de despacho en este momento.")
        else:
            # 1. FILTRADO ESTRICTO
            placa_actual = st.session_state.placa_autenticada.strip().upper()
            df_pendientes = df[(df['estado'].str.lower() != 'entregado') & (df['placa'] == placa_actual)]

            # 2. MÉTRICAS
            pendientes = len(df_pendientes)
            total_kgs = df_pendientes['cantidad_kgs'].sum()

            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Envíos Pendientes", value=pendientes)
            with col2:
                st.metric(label="Kilos en Camión", value=f"{total_kgs:,.1f} KG")
            st.markdown("##")

            # 3. RENDERIZADO DE LA RUTA
            st.markdown("<h3 style='color: gray; font-size: 14px; letter-spacing: 1px;'>HOJA DE RUTA EN TIEMPO REAL</h3>", unsafe_allow_html=True)
            
            if df_pendientes.empty:
                st.success("Todas tus entregas asignadas han sido completadas satisfactoriamente.")
            else:
                for index, fila in df_pendientes.iterrows():
                    id_v = fila['id_venta']
                    
                    estado_camara = f"mostrar_camara_{id_v}_{index}"
                    if estado_camara not in st.session_state:
                        st.session_state[estado_camara] = False
                    
                    # HTML
                    card_html = f"""
                    <div class="delivery-card">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <span style="font-family: monospace; color: #8b949e; font-size: 11px;">ID VENTA #{id_v}</span>
                                <h4 style="color: white; margin: 4px 0 0 0; font-size: 18px; font-weight: bold;">{fila['cliente']}</h4>
                            </div>
                            <span class="badge-pendiente">PENDIENTE</span>
                        </div>
                        <div style="margin-top: 15px; border-top: 1px solid #30363d; padding-top: 10px; font-size: 14px;">
                            <p style="margin: 10px 0 5px 0; color: #c9d1d9;"><b>Producto:</b> {fila['producto']} — <span style="color: #00f0ff; font-weight: bold;">{fila['cantidad_kgs']} KGS</span></p>
                            <p style="margin: 5px 0 5px 0; color: #8b949e;"><b>Sede Despacho:</b> {fila['direccion']}</p>
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
                    
                    # Flujo de botones
                    if not st.session_state[estado_camara]:
                        if st.button("Confirmar Entrega", key=f"abrir_cam_{id_v}_{index}", icon=":material/task_alt:"):
                            st.session_state[estado_camara] = True
                            st.rerun()
                    else:
                        st.caption("Protocolo de seguridad: Evidencia fotográfica obligatoria.")
                        foto_evidencia = st.camera_input(f"Soporte {id_v}", key=f"cam_{id_v}_{index}", label_visibility="collapsed")
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("Cancelar", key=f"cancelar_{id_v}_{index}", type="secondary", icon=":material/close:"):
                                st.session_state[estado_camara] = False
                                st.rerun()
                                
                        with col_btn2:
                            if st.button("Enviar Soporte", key=f"btn_{id_v}_{index}", icon=":material/upload:"):
                                if foto_evidencia is None:
                                    st.error("La foto es obligatoria para cerrar la entrega.")
                                else:
                                    with st.spinner("Subiendo evidencia al sistema logístico..."):
                                        registrar_entrega_en_sheets(id_v, foto_evidencia.getvalue())
                                        st.session_state[estado_camara] = False
                    
                    st.markdown("<hr style='border-color: #30363d; margin: 25px 0px;'>", unsafe_allow_html=True)

    if st.button("Sincronizar Datos Ahora", key="btn_global_refresh", type="secondary", icon=":material/sync:"):
        st.cache_data.clear()
        st.rerun()
