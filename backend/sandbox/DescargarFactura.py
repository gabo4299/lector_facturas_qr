import requests
from bs4 import BeautifulSoup
import PyPDF2
from io import BytesIO

# --- URLs ESPECÍFICAS PARA IMPUESTOS BOLIVIA ---
# URL para cargar la página y obtener los parámetros iniciales
get_url = 'https://siat.impuestos.gob.bo/consulta/QR?nit=176360023&cuf=C1129B1EA5B84FD1C229FA2CC46E6004BD8B1A7643DC55CF9AD81F74&numero=44463&t=2'

# URL a la que el formulario envía la petición POST para generar el archivo
post_url = 'https://siat.impuestos.gob.bo/consulta/public/QR.xhtml'



session = requests.Session()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Obtener la página, la cookie de sesión y el ViewState dinamico.
try:
    print(f"Paso 1: Conectando a {get_url[:40]}...")
    response_get = session.get(get_url, headers=headers)
    response_get.raise_for_status()

    soup = BeautifulSoup(response_get.text, 'html.parser')
    
    # Extraemos el ViewState que el servidor nos envió.
    view_state_tag = soup.find('input', {'name': 'javax.faces.ViewState'})
    if not view_state_tag or not view_state_tag.has_attr('value'):
        raise ValueError("No se pudo encontrar el 'javax.faces.ViewState' en la página.")
        
    view_state = view_state_tag['value']
    print("Éxito! ViewState y cookie de sesión obtenidos. view state es ", view_state)

except requests.exceptions.RequestException as e:
    print(f"Error CRÍTICO al conectar con la URL: {e}")
    exit()
except ValueError as e:
    print(f"Error CRÍTICO: {e}")
    exit()


# PASO 2: Construir el payload y enviarlo a la URL de POST.

boton_id = 'formQr:j_idt218' 
print(f"\nPreparando descarga para el formato: {'CARTA' if boton_id == 'formQr:j_idt216' else 'ROLLO'}")


form_data = {
    'formQr': 'formQr',
    'formQr:idTipoSistema': '1', # Este valor viene en un input oculto en la página
    boton_id: '',               # El ID del botón presionado, con valor vacío
    'javax.faces.ViewState': view_state,
    'javax.faces.source': boton_id,
    'javax.faces.partial.ajax': 'true',
    'javax.faces.partial.execute': '@all',
}

post_headers = headers.copy()
post_headers['Faces-Request'] = 'partial/ajax'
post_headers['Referer'] = get_url # Buena práctica añadir el Referer

try:
    print("Paso 2: Enviando petición POST para generar el PDF...")
    response_post = session.post(post_url, data=form_data, headers=post_headers)
    response_post.raise_for_status()

    # PASO 3: Procesar la respuesta
    if 'application/pdf' in response_post.headers.get('Content-Type', ''):
        print("¡Éxito! El servidor respondió con un PDF.")
        
        nombre_archivo = 'factura_formato_carta.pdf' if boton_id == 'formQr:j_idt216' else 'factura_formato_rollo.pdf'
        
        with open(nombre_archivo, 'wb') as f:
            f.write(response_post.content)
        # print("response content es ",response_post.content)
        print(f"PDF guardado como '{nombre_archivo}'")


        print("\nPaso 3: Analizando contenido del PDF...")
        pdf_reader = PyPDF2.PdfReader(BytesIO(response_post.content))
        num_paginas = len(pdf_reader.pages)
        print(f"El documento tiene {num_paginas} página(s).")

        if num_paginas > 0:
            texto = pdf_reader.pages[0].extract_text()
            print("\n--- INICIO DEL TEXTO (Página 1) ---")
            print(texto)
            print("--- FIN DEL TEXTO ---")

    else:
        print("\nERROR: La respuesta del servidor NO fue un PDF.")
        print("Revisa la lógica o los parámetros. Respuesta del servidor:")
        # print(response_post.text)
except requests.exceptions.RequestException as e:
    print(f"Error CRÍTICO durante la petición POST: {e}")