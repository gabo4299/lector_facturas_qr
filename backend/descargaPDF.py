import requests
from bs4 import BeautifulSoup
import PyPDF2
from io import BytesIO
import datetime
# --- URLs ESPECÍFICAS PARA IMPUESTOS BOLIVIA ---
# URL para cargar la página y obtener los parámetros iniciales
get_url = 'https://siat.impuestos.gob.bo/consulta/QR?nit=176360023&cuf=C1129B1EA5B84FD1C229FA2CC46E6004BD8B1A7643DC55CF9AD81F74&numero=44463&t=2'

# URL a la que el formulario envía la petición POST para generar el archivo
post_url = 'https://siat.impuestos.gob.bo/consulta/public/QR.xhtml'



class ObtenerFacrura:
    """ Realiza la peticion a SIAT obtiene datos y obtiene el detalle de la factura """
    def __init__(self, get_url: str,
                 post_url:str="https://siat.impuestos.gob.bo/consulta/public/QR.xhtml",
                 boton_id='formQr:j_idt218' ,
                 header_base={
                'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}):
            self.get_url = get_url
            self.post_url = post_url
            self.Factura="Factura Obj"
            self.responsePost=None
            self.boton_id= boton_id
            self.headers=header_base
            self.viewState=""
            self.comercio=""
            # --- Atributos para el manejo de estado y errores ---
            self.statusGet=None
            # self.errorGet = None
            self.statusPost = None
            self.statusPDF = None
            self.session=None

    def req_get(self):
        self.session = requests.Session()
        try:
            print(f"Paso 1: Conectando a {self.get_url[:40]}...")
            response_get = self.session.get(self.get_url, headers=self.headers)
            response_get.raise_for_status()

            soup = BeautifulSoup(response_get.text, 'html.parser')
            
            # Extraemos el ViewState que el servidor nos envió.
            view_state_tag = soup.find('input', {'name': 'javax.faces.ViewState'})
            if not view_state_tag or not view_state_tag.has_attr('value'):
                self.statusGet=False
                raise ValueError("No se pudo encontrar el 'javax.faces.ViewState' en la página.")
            
                
            view_state = view_state_tag['value']
            print("Éxito! ViewState y cookie de sesión obtenidos. view state es ", view_state)
            self.statusGet=True
            self.viewState=view_state
            # Agregar Valores Minimos a la factura 
            self.Factura=""
            return True

        except requests.exceptions.RequestException as e:
            self.statusGet=False
            print(f"Error CRÍTICO al conectar con la URL: {e}")
            return False
        except ValueError as e:
            self.statusGet=False
            print(f"Error CRÍTICO: {e}")
            return False
    def req_post(self):
        form_data = {
            'formQr': 'formQr',
            'formQr:idTipoSistema': '1', # Este valor viene en un input oculto en la página
            self.boton_id: '',               # El ID del botón presionado, con valor vacío
            'javax.faces.ViewState': self.viewState,
            'javax.faces.source': self.boton_id,
            'javax.faces.partial.ajax': 'true',
            'javax.faces.partial.execute': '@all',
        }   
        post_headers = self.headers.copy()
        post_headers['Faces-Request'] = 'partial/ajax'
        post_headers['Referer'] = self.get_url 
        try:
            response_post = self.session.post(self.post_url, data=form_data, headers=post_headers)
            response_post.raise_for_status()

            # PASO 3: Procesar la respuesta
            if 'application/pdf' in response_post.headers.get('Content-Type', ''):

                print("¡Éxito! El servidor respondió con un PDF.")
                
                self.responsePost=response_post.content
                self.statusPost=True
                return True

            else:
                print("\nERROR: La respuesta del servidor NO fue un PDF.")
                print("Revisa la lógica o los parámetros. Respuesta del servidor:")
                self.statusPost=True
                return False
                # print(response_post.text)
        except requests.exceptions.RequestException as e:
            self.statusPost=True
            print(f"Error CRÍTICO durante la petición POST: {e}")
            return False

    def processPDF(self):
        if self.statusPost == True:
            # nombre_archivo = "Factura_"+self.comercio+"_"+datetime.datetime.now()+".pdf"
            # Ruta_a_guardad=""
            # try:
            #     with open(nombre_archivo, 'wb') as f:
            #         f.write(self.responsePost)
            # except:
            #     self.statusPDF=False
            #     print("fallo al leer")
            #     return False
            try:
                pdf_reader = PyPDF2.PdfReader(BytesIO(self.responsePost))
                num_paginas = len(pdf_reader.pages)
                print(f"El documento tiene {num_paginas} página(s).")

                if num_paginas > 0:
                    texto = pdf_reader.pages[0].extract_text()
                    print("\n--- INICIO DEL TEXTO (Página 1) ---")
                    print(texto)
                    print("--- FIN DEL TEXTO ---")
            except:
                
                self.statusPDF=False
                return False
        else:
            self.statusPDF=False
            return False
    def get_Factura(self):
        return self.Factura
# Creamos una sesión que manejará las cookies por nosotros.
