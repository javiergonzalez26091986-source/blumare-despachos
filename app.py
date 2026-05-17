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
@st.cache_data(ttl=10)  # Sincronización rápida cada 10 segundos
def descargar_datos_despacho():
    try:
        respuesta = requests.get(f"{URL_API}?tipo_operacion=ObtenerDespachos", timeout=10)
        resultado = respuesta.json()
        
        # Si es una lista directa de registros
        if isinstance(resultado, list):
            return resultado
        # Si viene envuelta en un diccionario con la clave "data"
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
    # Convertimos a DataFrame inicial
    df_crudo = pd.DataFrame(datos_ventas)

    # ESTABILIZACIÓN DE LLAVES: Forzamos a que todas las columnas sean minúsculas para evitar conflictos
    df_crudo.columns = [str(col).lower().strip() for col in df_crudo.columns]

    # Buscamos variaciones comunes del ID de Venta en minúsculas ('id_venta', 'id_venta ', etc.)
    columna_id_min = None
    for col in df_crudo.columns:
        if 'id_venta' in col or 'id_lote_origen' in col:  # Si no encuentra venta, busca lote para guiarse
            columna_id_min = col
            break
            
    if not columna_id_min and len(df_crudo.columns) > 0:
        # Si por alguna razón sigue sin hacer match, tomamos la primera columna disponible como ID
        columna_id_min = df_crudo.columns[0]

    if columna_id_min:
        # Filtramos de raíz eliminando filas vacías, nulas o con texto "nan"
        df = df_crudo[
            (df_crudo[columna_id_min].astype(str).str.strip() != '') & 
            (df_crudo[columna_id_min].notna()) & 
            (df_crudo[columna_id_min].astype(str).str.lower() != 'nan')
        ].copy()
    else:
        df = df_crudo.copy()

    # Validación final del DataFrame limpio
    if df.empty:
        st.info("Aún no hay registros válidos con contenido en la base de datos.")
    else:
        # MAPEADO NORMALIZADO (Buscamos coincidencias parciales en minúsculas)
        def extraer_columna(df_obj, palabras_clave):
            for col in df_obj.columns:
                if any(pc in col for pc in palabras_clave):
                    return df_obj[col]
            return pd.Series(["N/A"] * len(df_obj), index=df_obj.index)

        # Asignación inteligente basada en lo que contenga el JSON de tu macro
        df['id_venta'] = extraer_columna(df, ['id_venta', 'venta'])
        df['cliente'] = extraer_columna(df, ['cliente', 'nombre'])
        df['producto'] = extraer_columna(df, ['producto', 'item'])
        df['cantidad_kgs'] = extraer_columna(df, ['cantidad_kgs', 'kgs', 'cantidad'])
        df['direccion'] = extraer_columna(df, ['sede_despacho', 'direccion', 'sede'])
        df['estado'] = extraer_columna(df, ['estado_despacho', 'estado'])
        df['repartidor'] = extraer_columna(df, ['sede_despacho', 'repartidor'])
        df['fecha'] = extraer_columna(df, ['fecha_hora', 'fecha'])

        # Forzar formato numérico limpio en los kilogramos
        df['cantidad_kgs'] = pd.to_numeric(df['cantidad_kgs'], errors='coerce').fillna(0.0)

        # 4. MÉTRICAS CLAVE EN LA PARTE SUPERIOR (KPIs)
        # Cuenta los elementos cuyo estado no sea 'entregado'
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
            estado = str(fila['estado']).strip()
            clase_badge = "badge-entregado" if estado.lower() == "entregado" else "badge-pendiente"
            
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
