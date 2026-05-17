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

# 3. CONEXIÓN Y DESCARGA DE DATOS CORREGIDA
@st.cache_data(ttl=10)  # Sincronización rápida cada 10 segundos para los repartidores
def descargar_datos_despacho():
    try:
        respuesta = requests.get(f"{URL_API}?tipo_operacion=ObtenerDespachos", timeout=10)
        resultado = respuesta.json()
        
        # Si la API devuelve una lista directa de filas
        if isinstance(resultado, list):
            return resultado
        # Si viene envuelta en un formato de diccionario estándar con la clave "data"
        elif isinstance(resultado, dict) and "data" in resultado:
            return resultado.get("data", [])
            
        return []
    except Exception as e:
        st.error(f"Error de conexión con la central: {e}")
        return []
        
datos_ventas = descargar_datos_despacho()

if not datos_ventas:
    st.warning("No se encontraron registros de entregas en la pestaña Historico_Ventas o la API no respondió.")
else:
    # Convertimos los datos a DataFrame
    df = pd.DataFrame(datos_ventas)

    # MAPEADO RESILIENTE CON LAS COLUMNAS REALES DE HISTORICO_VENTAS
    columnas_reales = {
        'id_venta': 'ID_Venta',
        'cliente': 'Cliente',
        'producto': 'Producto',
        'cantidad_kgs': 'Cantidad_KGS',
        'direccion': 'Sede_Despacho',
        'estado': 'Estado_Despacho',
        'repartidor': 'Sede_Despacho', # Provisional mientras se añade campo de transportador específico
        'fecha': 'Fecha_Hora'
    }
    
    # Inyección segura de campos para prevenir cualquier KeyError si Sheets cambia
    for clave_app, columna_sheet in columnas_reales.items():
        if columna_sheet in df.columns:
            df[clave_app] = df[columna_sheet]
        elif clave_app not in df.columns:
            df[clave_app] = "N/A"

    # Forzar formato numérico limpio en los kilogramos para sumatorias seguras
    df['cantidad_kgs'] = pd.to_numeric(df['cantidad_kgs'], errors='coerce').fillna(0.0)

    # 4. MÉTRICAS CLAVE EN LA PARTE SUPERIOR (KPIs)
    # Filtra todo lo que no esté marcado exactamente como 'entregado'
    pendientes = len(df[df['estado'].astype(str).str.lower() != 'entregado'])
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
        estado = str(fila['estado']).strip()
        clase_badge = "badge-entregado" if estado.lower() == "entregado" else "badge-pendiente"
        
        # Estructura visual adaptada a pantallas de smartphones
        card_html = f"""
        <div class="delivery-card">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <span style="font-family: monospace; color: #8b949e; font-size: 11px;">ID VENTA #{fila['id_venta']}</span>
                    <h4 style="color: white; margin: 4px 0 0 0; font-size: 18px; font-weight: bold;">{fila['cliente']}</h4>
                </div>
                <span class="{clase_badge}">{estado.upper()}</span>
            </div>
            <div style="margin-top: 15px; border-top: 1px solid #30363d; pt-10px; font-size: 14px;">
                <p style="margin: 10px 0 5px 0; color: #c9d1d9;">📦 <b>Producto:</b> {fila['producto']} — <span style="color: #00f0ff; font-weight: bold;">{fila['cantidad_kgs']} KGS</span></p>
                <p style="margin: 5px 0 5px 0; color: #8b949e;">📍 <b>Sede Despacho:</b> {fila['direccion']}</p>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 15px; font-size: 11px; color: #58a6ff;">
                <span>🏢 Central: {fila['repartidor']}</span>
                <span>📅 Registro: {fila['fecha']}</span>
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

# 7. BOTÓN MANUAL DE REFRESCAR EN EL FOOTER
if st.button("🔄 Sincronizar Datos Ahora"):
    st.cache_data.clear()
    st.rerun()
