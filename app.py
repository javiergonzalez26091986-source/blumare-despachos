import streamlit as st
import requests
import pandas as pd
import datetime
import os

# =============================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA MÓVIL Y ANTI-INACTIVIDAD
# =============================================================================
icono_pestana = "logoBlumare.ico"
if not os.path.exists(icono_pestana):
    icono_pestana = "logoBlumare.jpeg"

st.set_page_config(
    page_title="Blumare Logistics",
    page_icon=icono_pestana if os.path.exists(icono_pestana) else "🚚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Inyección de estilos CSS - ESTILO ENTERPRISE/MINIMALISTA Y BLOQUEO DE FOTO DE PERFIL
st.markdown("""
    <style>
    /* ===================================================================== */
    /* 1. OCULTAR ABSOLUTAMENTE TODO LO DE STREAMLIT CLOUD (FOTO Y MENÚS)    */
    /* ===================================================================== */
    [data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    .stAppDeployButton { display: none !important; }
    #MainMenu { display: none !important; }
    footer { display: none !important; }
    
    /* LA MAGIA PARA DESAPARECER LA FOTO DE PERFIL (CREATOR BADGE) */
    div[class*="viewerBadge"] { display: none !important; }
    div[class^="viewerBadge"] { display: none !important; }
    [data-testid="stAppCreatorBadge"] { display: none !important; }
    [data-testid="stCreatorProfile"] { display: none !important; }
    a[href*="streamlit.io/cloud"] { display: none !important; }
    #creatorBadge { display: none !important; }

    /* ===================================================================== */
    /* 2. ESTILOS VISUALES DEL DASHBOARD (Slate 900 - Premium)               */
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

URL_API = "https://script.google.com/macros/s/AKfycbys2ymG2Ad5av2jtR3LFttFiJPkQS2LfiOGwuw7-RynhbuPvEE9R5G90xeS_bofoi-CCg/exec"

# =============================================================================
# 2. ENCABEZADO MINIMALISTA (LOGO + TÍTULO)
# =============================================================================
nombre_logo = "logoBlumare.jpeg"

if os.path.exists(nombre_logo):
    import base64
    with open(nombre_logo, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    
    st.markdown(
        f"""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin-top: 10px; margin-bottom: 25px;">
            <img src="data:image/jpeg;base64,{encoded_string}" width="60" style="border-radius: 12px; margin-bottom: 15px;">
            <h1 style="color: #f8fafc; font-size: 20px; font-weight: 700; margin: 0; letter-spacing: 1px;">BLUMARE LOGISTICS</h1>
            <p style="color: #64748b; font-size: 12px; font-weight: 500; margin: 0; text-transform: uppercase; letter-spacing: 0.5px;">Control de Despachos</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# =============================================================================
# 3. LÓGICA DE DATOS
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
        return []

def registrar_entrega_en_sheets(id_venta):
    try:
        ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        url_actualizar = f"{URL_API}?tipo_operacion=ActualizarEstado&id_venta={id_venta}&nuevo_estado=Entregado&hora_entrega={ahora}"
        respuesta = requests.get(url_actualizar, timeout=10)
        
        if respuesta.status_code == 200:
            st.toast(f"Entrega confirmada: {id_venta}", icon="✅")
            st.cache_data.clear() 
            st.rerun()
        else:
            st.error("Error al actualizar en servidor.")
    except Exception as e:
        st.error("Error de red.")

datos_crudos = descargar_datos_despacho()

if not datos_crudos:
    st.info("Sincronizando con la central...")
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
        st.success("No hay datos históricos activos.")
    else:
        # =============================================================================
        # 4. DASHBOARD DE MÉTRICAS (HTML/CSS Personalizado)
        # =============================================================================
        pendientes = len(df[df['estado'].str.lower() != 'entregado'])
        total_kgs = df['cantidad_kgs'].sum()

        html_dashboard = f"""
        <div style="display: flex; gap: 12px; margin-bottom: 25px;">
            <div style="flex: 1; background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 16px;">
                <div style="color: #94a3b8; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px;">Envíos Pendientes</div>
                <div style="color: #f8fafc; font-size: 26px; font-weight: 700;">{pendientes}</div>
            </div>
            <div style="flex: 1; background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 16px;">
                <div style="color: #94a3b8; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px;">Total Kilos (Ruta)</div>
                <div style="color: #f8fafc; font-size: 26px; font-weight: 700;">{total_kgs:,.1f} <span style="font-size: 14px; color: #64748b;">KG</span></div>
            </div>
        </div>
        """
        st.markdown(html_dashboard, unsafe_allow_html=True)

        # =============================================================================
        # 5. BUSCADOR INTERACTIVO
        # =============================================================================
        busqueda = st.text_input("Buscar", placeholder="🔍 Buscar por cliente o producto...", label_visibility="collapsed")

        if busqueda:
            df = df[
                df['cliente'].str.contains(busqueda, case=False) | 
                df['producto'].str.contains(busqueda, case=False)
            ]

        # =============================================================================
        # 6. TARJETAS DE RUTA ESTILO TICKET CORPORATIVO
        # =============================================================================
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        
        df_pendientes = df[df['estado'].str.lower() != 'entregado']

        if df_pendientes.empty:
            st.markdown(
                """
                <div style="background-color: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 12px; padding: 20px; text-align: center; margin-top: 20px;">
                    <h3 style="color: #10b981; font-size: 18px; margin: 0 0 5px 0;">¡Ruta Completada! 🎉</h3>
                    <p style="color: #94a3b8; font-size: 13px; margin: 0;">Todas las entregas del día han sido procesadas.</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            for index, fila in df_pendientes.iterrows():
                id_v = fila['id_venta']
                
                # Diseño de Ticket Profesional
                ticket_html = f"""
                <div style="background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 20px; margin-bottom: 8px;">
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <span style="color: #64748b; font-size: 12px; font-weight: 600; font-family: monospace;">{id_v}</span>
                        <span style="background-color: rgba(245, 158, 11, 0.1); color: #f59e0b; padding: 4px 10px; border-radius: 6px; font-size: 10px; font-weight: 700; text-transform: uppercase;">Pendiente</span>
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <div style="color: #94a3b8; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px;">Cliente / Destino</div>
                        <div style="color: #f8fafc; font-size: 18px; font-weight: 600; line-height: 1.3;">{fila['cliente']}</div>
                        <div style="color: #cbd5e1; font-size: 13px; margin-top: 4px;">📍 {fila['direccion']}</div>
                    </div>
                    
                    <div style="background-color: #0f172a; border-radius: 8px; padding: 12px; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="color: #64748b; font-size: 11px; margin-bottom: 2px;">PRODUCTO</div>
                            <div style="color: #e2e8f0; font-size: 14px; font-weight: 500;">📦 {fila['producto']}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="color: #64748b; font-size: 11px; margin-bottom: 2px;">CANTIDAD</div>
                            <div style="color: #3b82f6; font-size: 16px; font-weight: 700;">{fila['cantidad_kgs']} KG</div>
                        </div>
                    </div>
                    
                </div>
                """
                st.markdown(ticket_html, unsafe_allow_html=True)
                
                # Botón Integrado
                if st.button("Confirmar Entrega", key=f"btn_{id_v}_{index}", type="primary"):
                    registrar_entrega_en_sheets(id_v)
                
                st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

# =============================================================================
# 7. BOTÓN MANUAL DE REFRESCAR
# =============================================================================
st.markdown("<div style='margin-top: 30px; margin-bottom: 10px; border-top: 1px solid #334155; padding-top: 20px;'></div>", unsafe_allow_html=True)
if st.button("Actualizar Sistema", key="btn_global_refresh", type="secondary"):
    st.cache_data.clear()
    st.rerun()
