import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import os
import base64

# ==============================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILO INDUSTRIAL COMPACTO (MÓVIL)
# ==============================================================================
icono_pestana = "logoBlumare.ico" if os.path.exists("logoBlumare.ico") else "logoBlumare.jpeg"
st.set_page_config(page_title="Blumare - Repartos", page_icon=icono_pestana, layout="centered")

st.markdown("""
    <style>
    [data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    .stAppDeployButton { display: none !important; }
    footer { display: none !important; }
    
    .stApp { background-color: #0f172a; }
    .stTextInput > div > div > input, .stSelectbox > div > div > div {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        color: #f8fafc !important;
    }
    
    div.stButton > button {
        border-radius: 8px !important;
        font-weight: 800 !important;
        border: none !important;
        transition: transform 0.1s ease !important;
    }
    div.stButton > button:active { transform: scale(0.96) !important; }
    div.stButton > button[kind="primary"] { background-color: #10b981 !important; color: white !important; }
    div.stButton > button[kind="secondary"] { background-color: #ef4444 !important; color: white !important; }
    
    /* Tarjetas de Pedidos */
    .pedido-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

URL_API = "https://script.google.com/macros/s/AKfycbys2ymG2Ad5av2jtR3LFttFiJPkQS2LfiOGwuw7-RynhbuPvEE9R5G90xeS_bofoi-CCg/exec"
CLOUDINARY_URL = "https://api.cloudinary.com/v1_1/ddouzzzs1i/image/upload"
CLOUDINARY_PRESET = "bluemare_preset"

# Estado de autenticación
if 'placa_autenticada' not in st.session_state: st.session_state.placa_autenticada = None

# ==============================================================================
# 2. CARGA DE CONEXIONES LOGÍSTICAS
# ==============================================================================
@st.cache_data(ttl=60)
def obtener_vehiculos_maestros():
    try:
        res = requests.get(f"{URL_API}?tipo_operacion=ObtenerVehiculos", timeout=10)
        return res.json() if isinstance(res.json(), list) else []
    except: return []

@st.cache_data(ttl=15)
def obtener_pedidos_totales():
    try:
        res = requests.get(f"{URL_API}?tipo_operacion=ObtenerDespachos", timeout=12)
        return res.json() if isinstance(res.json(), list) else []
    except: return []

# ==============================================================================
# BRANDING DE ENCABEZADO
# ==============================================================================
nombre_logo = "logoBlumare.jpeg"
if os.path.exists(nombre_logo):
    with open(nombre_logo, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode()
    logo_html = f'<img src="data:image/jpeg;base64,{encoded_string}" width="45" style="border-radius: 6px;">'
else:
    logo_html = "🚚"

st.markdown(
    f"""
    <div style="display: flex; align-items: center; justify-content: center; gap: 12px; margin-top: 15px; margin-bottom: 5px;">
        {logo_html}
        <h2 style='color: #f8fafc; margin: 0; font-weight: 800; font-size: 24px;'>BLUMARE - REPARTOS</h2>
    </div>
    <hr style="border-color: #334155; margin-top: 5px; margin-bottom: 20px;">
    """, unsafe_allow_html=True
)

# ==============================================================================
# 3. INTERFAZ DE LOGEO MANDATORIO POR PLACA
# ==============================================================================
if st.session_state.placa_autenticada is None:
    st.markdown("<h4 style='color: #94a3b8; text-align: center;'>Control de Acceso de Conductores</h4>", unsafe_allow_html=True)
    
    placas_validas = obtener_vehiculos_maestros()
    
    if not placas_validas:
        st.error("No se pudo conectar con la base de datos de vehículos. Intente de nuevo.")
    else:
        placa_seleccionada = st.selectbox("Seleccione la Placa del Camión:", ["Seleccione su vehículo"] + placas_validas)
        
        if st.button("🔓 INICIAR SESIÓN", type="primary", use_container_width=True):
            if placa_seleccionada != "Seleccione su vehículo":
                st.session_state.placa_autenticada = placa_seleccionada
                st.success(f"Vehículo {placa_seleccionada} autenticado correctamente.")
                st.rerun()
            else:
                st.warning("Debe seleccionar una placa válida para ingresar.")
else:
    # Header de sesión activa
    c_user, c_out = st.columns([7, 3])
    c_user.markdown(f"🟢 Vehículo activo: **{st.session_state.placa_autenticada}**")
    if c_out.button("🚪 Cerrar Sesión", type="secondary", use_container_width=True):
        st.session_state.placa_autenticada = None
        st.rerun()
        
    st.markdown("### Pedidos Asignados para Entrega")
    
    # Descarga e interpretación del JSON puro de la nube
    raw_pedidos = obtener_pedidos_totales()
    
    # Filtrado estricto por placa (índice 12) y estado pendiente (índice 10)
    pedidos_filtrados = []
    for p in raw_pedidos:
        if len(p) > 12:
            placa_pedido = str(p[12]).strip().toUpperCase() if hasattr(str(p[12]), 'toUpperCase') else str(p[12]).strip().upper()
            placa_login = st.session_state.placa_autenticada.strip().upper()
            estado_pedido = str(p[10]).strip()
            
            if placa_pedido == placa_login and estado_pedido == "Pendiente":
                pedidos_filtrados.append({
                    "id": p[0], "fecha": p[1], "sede": p[2], "cliente": p[3],
                    "producto": p[4], "lote": p[5], "cantidad": p[6]
                })

    if not pedidos_filtrados:
        st.info("No tienes rutas de entrega pendientes asignadas para el día de hoy.")
    else:
        for item in pedidos_filtrados:
            with st.container():
                st.markdown(f"""
                <div class="pedido-card">
                    <span style="color:#3b82f6; font-weight:bold;">📦 RECIBO: {item['id']}</span><br>
                    <span style="color:#f8fafc; font-size:16px;"><b>Cliente:</b> {item['cliente']}</span><br>
                    <span style="color:#94a3b8; font-size:14px;"><b>Carga:</b> {item['producto']} ({item['cantidad']} KGS)</span><br>
                    <span style="color:#94a3b8; font-size:14px;"><b>Origen:</b> Sede {item['sede']} | Lote: {item['lote']}</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Desplegable individual para procesar la entrega del pedido sin afectar los demás
                with st.expander(f"⚙️ Reportar Entrega de {item['id']}"):
                    foto_captura = st.camera_input(f"Tomar Foto al Documento Firmado:", key=f"cam_{item['id']}")
                    
                    if st.button(f"🚀 Confirmar Entrega de {item['id']}", key=f"btn_{item['id']}", type="primary", use_container_width=True):
                        if not foto_captura:
                            st.error("Es obligatorio tomar la foto del recibo firmado antes de finalizar.")
                        else:
                            with st.spinner("Subiendo evidencia digital a la nube y actualizando Google Sheets..."):
                                try:
                                    # 1. Envío binario multipart directo a la API REST de Cloudinary
                                    archivos = {"file": foto_captura.getvalue()}
                                    parametros = {"upload_preset": CLOUDINARY_PRESET}
                                    
                                    response_cloud = requests.post(CLOUDINARY_URL, files=archivos, data=parametros, timeout=15)
                                    
                                    if response_cloud.status_code == 200:
                                        url_segura_evidencia = response_cloud.json().get("secure_url", "")
                                        
                                        # 2. Despacho de variables de estado a Apps Script
                                        hora_actual_texto = datetime.now().strftime("%H:%M:%S")
                                        endpoint_update = (
                                            f"{URL_API}?tipo_operacion=ActualizarEstado"
                                            f"&id_venta={item['id']}"
                                            f"&nuevo_estado=Entregado"
                                            f"&hora_entrega={hora_actual_texto}"
                                            f"&soporte_entrega={url_segura_evidencia}"
                                        )
                                        
                                        res_sheets = requests.get(endpoint_update, timeout=10)
                                        if res_sheets.status_code == 200 and "SUCCESS" in res_sheets.text:
                                            st.success("¡Documentación enviada con éxito! Registro completado.")
                                            st.cache_data.clear()
                                            st.rerun()
                                        else:
                                            st.error("Error al asentar el estado en la base de datos.")
                                    else:
                                        st.error("Error crítico de almacenamiento de imágenes (Cloudinary).")
                                except Exception as ex:
                                    st.error(f"Fallo de conectividad: {str(ex)}")
