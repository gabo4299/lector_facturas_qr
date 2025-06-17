import httpx
from bs4 import BeautifulSoup
def HTTPException(status_code,detail):
    print(status_code,detail)
def scrape_monto_total(input_data):
    """
    Realiza web scraping en la URL proporcionada y extrae el texto del div con id 'monto_total'.
    """
    try:
        with httpx.Client() as client:
            response = client.get(str(input_data))
            response.raise_for_status()  # Lanza una excepción para códigos de estado HTTP erróneos (4xx o 5xx)
    except httpx.RequestError as e:
        return HTTPException(status_code=400, detail=f"Error al conectar con la URL: {e}")
    except httpx.HTTPStatusError as e:
        return HTTPException(status_code=e.response.status_code, detail=f"Error en la respuesta HTTP de la URL: {e.response.status_code} - {e.response.reason}")

    soup = BeautifulSoup(response.text, 'html.parser')
    # print(soup.prettify())
    
    tbody = soup.find('tbody', id='formQr:idListaDatoSistema_data')

    if tbody:
        # 2. Encontrar todas las filas (tr) dentro de ese tbody
        tabla= tbody.find_parent('table')
        filas = tbody.find_all('tr')
        cols=tabla.find('thead')
        columnas = cols.find_all('th')
        # Ahora puedes acceder a una fila específica por su índice
        # print ("als fials son :",filas)
        if len(filas) > 0:
            
            primera_fila = filas[0]
            data=primera_fila.find_all('td')
            print([i.get_text(strip=True) for i in columnas] )
            print([i.get_text(strip=True) for i in data])
    view_state_tag = soup.find('input', {'name': 'javax.faces.ViewState'})
    # print("llegoa a find")
    if not view_state_tag:
        raise ValueError("No se pudo encontrar el 'javax.faces.ViewState' en la página.")
        
    view_state = view_state_tag['value']
    print(f"ViewState encontrado: {view_state}...")

    #monto_total_div = soup.find('div', id='monto_total')

    #if monto_total_div:
        #return {"monto_total": monto_total_div.get_text(strip=True)}
    #else:
         #HTTPException(status_code=404, detail="Div con id 'monto_total' no encontrado en la página.")


url="https://siat.impuestos.gob.bo/consulta/QR?nit=176360023&cuf=C1129B1EA5B84FD1C229FA2CC46E6004BD8B1A7643DC55CF9AD81F74&numero=44463&t=2"


scrape_monto_total(url)
