import streamlit as st
import requests
import pandas as pd

# 1. CONFIGURACIÓN DE LA PÁGINA MÓVIL
st.set_page_config(
    page_title="Blumare - Despachos",
    page_icon="🚚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilos CSS personalizados para lograr un look Premium Dark y tarjetas estilo App Móvil
st.markdown("""
    <style>
    /* Fondo general oscuro */
    .stApp {
        background-color: #0d1117;
    }
    /* Tarjetas de entregas (Glassmorphism) */
    .delivery-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
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
    .badge-entregado {
        background-color: rgba(46, 204, 113, 0.15);
        color: #2ecc71;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        border: 1px solid rgba(46, 204, 113, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# URL exacta de tu API de Google Apps Script
URL_API = "https://script.google.com/macros/s/AKfycbys2ymG2Ad5av2jtR3LFttFiJPkQS2LfiOGwuw7-RynhbuPvEE9R5G90xeS_bofoi-CCg/exec"

# 2. ENCABEZADO DE LA APP
st.markdown("<h1 style='text-align: center; color: white; margin-bottom: 0;'>BLUMARE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #00f0ff; font-weight: bold; letter-spacing: 2px; margin-top: 0;'>LOGÍSTICA Y DESPACHOS</p>", unsafe_allow_html=True)
st.markdown("---")

# 3. CONEXIÓN Y DESCARGA DE DATOS FORZANDO "Historico_Ventas"
@st.cache_data(ttl=5)  # Sincronización rápida de 5 segundos
def descargar_datos_despacho():
    try:
        # Enviamos explícitamente los parámetros para asegurar que intente leer las ventas
        url_con_parametros = f"{URL_API}?tipo_operacion=ObtenerDespachos&pestana=Historico_Ventas"
        respuesta = requests.get(url_con_parametros, timeout=10)
        resultado = respuesta.json()
        
        if isinstance(resultado, list):
            return resultado
        elif isinstance(resultado, dict) and "data" in resultado:
            return resultado.get("data", [])
        return []
    except Exception as e:
        st.error(f"Error de conexión con la central: {e}")
        return []
        
datos_crudos = descargar_datos_despacho()

if not datos_crudos:
    st.warning("No se recibieron datos de la central o la lista está vacía.")
else:
    # Convertimos la matriz JSON a DataFrame de Pandas
    df_base = pd.DataFrame(datos_crudos)

    # DETECCIÓN DE ESTRUCTURA: ¿Nos mandó el Inventario (25 filas) o las Ventas Reales?
    # Si la fila tiene menos de 6 columnas o la columna 0 contiene "PLAQUETA", es que sigue leyendo el Inventario por error del .gs
    ejemplo_celda = str(df_base.iloc[0, 0]).upper() if not df_base.empty else ""
    
    if "PLAQUETA" in ejemplo_celda or len(df_base.columns) == 5:
        # Alerta informativa para ti mientras ajustas el Apps Script si es necesario
        st.sidebar.error("⚠️ La API está retornando el Inventario de Lotes en lugar de Ventas.")
        
        # Mapeo de emergencia para que la app no rompa usando los datos que enviaste
        df = df_base.copy()
        df['id_venta'] = df[4] if 4 in df.columns else "N/A"
        df['cliente'] = "Inventario Central"
        df['producto'] = df[0]
        df['cantidad_kgs'] = df[1] if 1 in df.columns else 0
        df['direccion'] = df[2] if 2 in df.columns else "Cali"
        df['estado'] = "Disponible"
        df['repartidor'] = "Bodega"
        df['fecha'] = "Hoy"
    else:
        # ¡ESTRUCTURA DE VENTAS EXCELENTE! Mapeo según la foto de tu Excel (Columnas A=0, B=1, C=2, D=3, E=4, G=6, K=10)
        # Limpiamos filas donde la columna A (ID_Venta) esté vacía
        df_base = df_base[df_base[0].astype(str).str.strip() != ''].copy()
        df_base = df_base[df_base[0].astype(str).str.upper() != 'ID_VENTA'].copy() # Ignora el encabezado físico si viene
        
        df = pd.DataFrame()
        df['id_venta'] = df_base[0] if 0 in df_base.columns else "N/A"
        df['fecha'] = df_base[1] if 1 in df_base.columns else "N/A"
        df['direccion'] = df_base[2] if 2 in df_base.columns else "N/A"
        df['cliente'] = df_base[3] if 3 in df_base.columns else "N/A"
        df['producto'] = df_base[4] if 4 in df_base.columns else "N/A"
        df['cantidad_kgs'] = df_base[6] if 6 in df_base.columns else 0
        df['estado'] = df_base[10] if 10 in df_base.columns else "Pendiente"
        df['repartidor'] = df_base[2] # Copia la sede de despacho temporalmente

    # Limpieza final y formateo numérico
    df['cantidad_kgs'] = pd.to_numeric(df['cantidad_kgs'], errors='coerce').fillna(0.0)
    
    # Filtrar filas vacías accidentales de control de base de datos
    df = df[df['id_venta'].astype(str).str.strip() != ''].copy()

    if df.empty:
        st.info("No hay registros activos para mostrar.")
    else:
        # 4. MÉTRICAS CLAVE EN LA PARTE SUPERIOR (KPIs)
        # Cuenta los envíos que no dicen exactamente 'entregado'
        pendientes = len(df[df['estado'].astype(str).str.lower().str.strip() != 'entregado'])
        total_kgs = df['cantidad_kgs'].sum()

        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Envíos Pendientes", value=pendientes)
        with col2:
            st.metric(label="Total Kilos Ruta", value=f"{total_kgs:,.1f} KG")

        st.markdown("##")

        # 5. BUSCADOR INTERACTIVO EN TIEMPO REAL
        busqueda = st.text_input("🔍 Buscar por Cliente o Producto:", placeholder="Escribe para filtrar la ruta...")

        if busqueda:
            df = df[
                df['cliente'].astype(str).str.contains(busqueda, case=False) | 
                df['producto'].astype(str).str.contains(busqueda, case=False)
            ]

        # 6. RENDERIZADO DE LAS TARJETAS DIGITALES DE ENTREGA
        st.markdown("<h3 style='color: gray; font-size: 14px; letter-spacing: 1px;'>HOJA DE RUTA EN TIEMPO REAL</h3>", unsafe_allow_html=True)
        
        for _, fila in df.iterrows():
            est_str = str(fila['estado']).strip()
            clase_badge = "badge-entregado" if est_str.lower() == "entregado" else "badge-pendiente"
            
            card_html = f"""
            <div class="delivery-card">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <span style="font-family: monospace; color: #8b949e; font-size: 11px;">ID REGISTRO #{fila['id_venta']}</span>
                        <h4 style="color: white; margin: 4px 0 0 0; font-size: 18px; font-weight: bold;">{fila['cliente']}</h4>
                    </div>
                    <span class="{clase_badge}">{est_str.upper()}</span>
                </div>
                <div style="margin-top: 15px; border-top: 1px solid #30363d; pt-10px; font-size: 14px;">
                    <p style="margin: 10px 0 5px 0; color: #c9d1d9;">📦 <b>Producto:</b> {fila['producto']} — <span style="color: #00f0ff; font-weight: bold;">{fila['cantidad_kgs']} KGS</span></p>
                    <p style="margin: 5px 0 5px 0; color: #8b949e;">📍 <b>Ubicación:</b> {fila['direccion']}</p>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 15px; font-size: 11px; color: #58a6ff;">
                    <span>🏢 Origen/Zona: {fila['repartidor']}</span>
                    <span>📅 Registro: {fila['fecha']}</span>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

# 7. BOTÓN MANUAL DE REFRESCAR EN EL FOOTER
if st.button("🔄 Sincronizar Datos Ahora"):
    st.cache_data.clear()
    st.rerun()
