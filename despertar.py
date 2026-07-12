import time
from playwright.sync_api import sync_playwright

def despertar_portal():
    print("Iniciando navegador virtual en la nube...")
    with sync_playwright() as p:
        # Lanzamos el navegador
        browser = p.chromium.launch(headless=True)
        
        # 1. INYECCIÓN DE USER-AGENT (Simula ser un humano desde un PC con Windows para saltar Cloudflare)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        url = "https://blumare-despachos-q45bu7xnguhecu4w8kdenk.streamlit.app/" 
        
        print(f"Visitando el portal: {url}")
        # Hacemos la visita y esperamos a que el DOM base cargue
        page.goto(url, wait_until="domcontentloaded")
        
        print("Esperando 10 segundos para evaluar el estado del servidor...")
        time.sleep(10)
        
        # 2. LÓGICA DE REACTIVACIÓN (Busca el botón de Streamlit si la app está dormida)
        try:
            # Streamlit utiliza este texto exacto en su botón para reactivar las apps
            boton_reactivar = page.get_by_role("button", name="Yes, get this app back up!")
            
            if boton_reactivar.count() > 0:
                print("¡La app estaba dormida! Haciendo clic para encender los contenedores...")
                boton_reactivar.first.click()
                print("Clic exitoso. Esperando 25 segundos a que la aplicación inicie por completo...")
                time.sleep(25)
            else:
                print("La app ya estaba despierta y operando. Visita registrada con éxito.")
                
        except Exception as e:
            print("Evaluación de estado completada sin botón de reposo.")
        
        # Validación final
        print(f"Misión cumplida. Título actual de la pestaña: '{page.title()}'")
        browser.close()

if __name__ == "__main__":
    despertar_portal()
