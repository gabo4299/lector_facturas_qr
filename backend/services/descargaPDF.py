import requests
from bs4 import BeautifulSoup
import PyPDF2
from io import BytesIO
import datetime
import asyncio
import httpx
import validators
import pandas as pd
# --- URLs ESPECÍFICAS PARA IMPUESTOS BOLIVIA ---
# URL para cargar la página y obtener los parámetros iniciales
get_url = 'https://siat.impuestos.gob.bo/consulta/QR?nit=176360023&cuf=C1129B1EA5B84FD1C229FA2CC46E6004BD8B1A7643DC55CF9AD81F74&numero=44463&t=2'

# URL a la que el formulario envía la petición POST para generar el archivo
post_url = 'https://siat.impuestos.gob.bo/consulta/public/QR.xhtml'

def parsear_query(url: str) -> dict:
    """
    Analiza una URL para extraer sus parámetros de consulta (query)
    sin usar ninguna librería, solo manipulación de strings.

    Args:
        url (str): La URL completa.

    Returns:
        dict: Un diccionario con los parámetros y sus valores.
    """
    parametros = {}
    
    # 1. Encontrar la parte de la consulta (lo que viene después de '?')
    try:
        # Dividimos la url en dos partes usando '?' como separador. 
        # El [1] se queda con la parte de la derecha.
        parte_query = url.split('?', 1)[1]
    except IndexError:
        # Si no hay '?', la URL no tiene consulta, devolvemos un diccionario vacío.
        return parametros

    # 2. Separar cada par de clave-valor. Están unidos por '&'.
    pares = parte_query.split('&')
    
    # 3. Recorrer cada par y separarlo en clave y valor usando '='.
    for par in pares:
        # Usamos split('=', 1) para dividir solo en el primer '=' que encuentre,
        # en caso de que el valor también contenga un '='.
        if '=' in par:
            clave, valor = par.split('=', 1)
            parametros[clave] = valor
        else:
            # Maneja casos donde un parámetro no tiene valor (ej: ...?enviar)
            if par: # Asegurarse de que no sea una cadena vacía
                parametros[par] = '' # Asignamos un valor vacío
                
    return parametros

class ObtenerFactura:
    """ Realiza la peticion a SIAT obtiene datos y obtiene el detalle de la factura """
    def __init__(self, get_url: str,
                 post_url:str="https://siat.impuestos.gob.bo/consulta/public/QR.xhtml",
                 boton_id='formQr:j_idt218' ,
                 header_base={
                'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}):
            if not isinstance(get_url, str) or not isinstance(post_url, str):
                raise TypeError("La entrada debe ser una cadena de texto (str). get_url o post_url")
            
            # validators.url() devuelve True si la URL es válida
            if not validators.url(get_url) or not validators.url(post_url):
                raise ValueError(f"La URL proporcionada ('{get_url}' o '{post_url}') no es válida.")

            params=parsear_query(get_url)
            try:
                self.cuf=params['cuf']
                self.nitEmisor=params['nit']
                self.Nfactura=params['numero']
            except:
                raise ValueError("NO SE PUDO REALIZAR EL PARSEO DE CUF NIT O N FACTURA")
            self.get_url = get_url
            self.post_url = post_url
            self.Factura="Factura Obj"
            self.responsePost=None
            self.boton_id= boton_id
            self.headers=header_base
            self.viewState=""
            self.comercio=""
            self.monto=0.0
            self.get_times=3
            self.post_times=2
            self.total_times=4
            # --- Atributos para el manejo de estado y errores ---
            self.statusGet=False
            self.msgGet=None
            self.msgPost=None
            self.msgPDF=None
            self.msgDoIt=None
            self.statusPost = False
            self.statusPDF = False
            self.session=None

  

        

    async def req_get(self):

        
        try:
            
            
                # print(f"Paso 1: Conectando a {self.get_url[:40]}...")
                response_get = await self.session.get(self.get_url, headers=self.headers)
                response_get.raise_for_status()

                soup = BeautifulSoup(response_get.text, 'html.parser')
                
                # Extraemos el ViewState que el servidor nos envió.
                view_state_tag = soup.find('input', {'name': 'javax.faces.ViewState'})
                if not view_state_tag or not view_state_tag.has_attr('value'):
                    self.statusGet=False
                    raise ValueError("No se pudo encontrar el 'javax.faces.ViewState' en la página.")
                
                    
                view_state = view_state_tag['value']
                print("Éxito! ViewState y cookie de sesión obtenidos. view state es ", view_state)
                
                self.viewState=view_state

                try:            
                    tbody = soup.find('tbody', id='formQr:idListaDatoSistema_data')

                    if tbody:
                        tabla= tbody.find_parent('table')
                        encabezados = [th.get_text(strip=True) for th in tabla.find_all('th')]
                        datos = []
                        for fila in tabla.find('tbody').find_all('tr'):
                            celdas = [td.get_text(strip=True) for td in fila.find_all('td')]
                            datos.append(celdas)
                    df = pd.DataFrame(datos, columns=encabezados)
                    # print("la tabla es \n",df.head(1))
                    # validar que el url es igual a lso datos de la pagina 
                    if (self.nitEmisor == str(df.iloc[0, 1]) and self.Nfactura ==str(df.iloc[0, 3]) and df.iloc[0,5] == "VALIDA"  ):
                        self.comercio=df.iloc[0, 2]
                        self.monto=float(df.iloc[0, 4])
                        self.statusGet=True
                        self.msgGet="Succes"
                        # Agregar Valores Minimos a la factura 
                        self.Factura=""
                        print("verificado")
                        return True


                    else:

                        print("error de validacion")
                        self.statusGet=False
                        self.msgGet=("Error de validacion de url y data de tabla")
                        return False
                    



                except :
                    print("error al revisar la tabla de siat")
                    self.statusGet=False
                    self.msgGet="Error al revisar la tabla de siat"
                    return False


        except httpx.RequestError as e:
            self.statusGet=False
            print(f"Error CRÍTICO al conectar con la URL: {e}")
            # raise RuntimeError(f"Error CRÍTICO al conectar con la URL: {e}")
            self.msgGet=(f"Error CRÍTICO al conectar con la URL: {e}")
            return False
        except ValueError as e:
            self.statusGet=False
            # raise RuntimeError(f"Error CRÍTICO: {e}")
            self.msgGet=(f"Error CRÍTICO: {e}")
            return False
        

    async def req_post(self):
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
            print(f"intentado POST con {self.viewState}")
            response_post = await self.session.post(self.post_url, data=form_data, headers=post_headers)
            response_post.raise_for_status()

            # PASO 3: Procesar la respuesta
            if 'application/pdf' in response_post.headers.get('Content-Type', ''):

                print("¡Éxito! El servidor respondió con un PDF.")
                
                self.responsePost=response_post.content
                self.statusPost=True
                self.msgPost="Succes"
                return True 


            else:
                self.msgPost=("ERROR: La respuesta del servidor NO fue un PDF.")
                # print("Revisa la lógica o los parámetros. Respuesta del servidor:")
                self.statusPost=False
                return False
                # print(response_post.text)
        except requests.exceptions.RequestException as e:
            self.statusPost=False
            self.msgPost=(f"Error CRÍTICO durante la petición POST: {e}")
            return False

    def processPDF(self):
        if self.statusPost == True:
            # nombre_archivo = "Factura_"+self.comercio+"_"+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+".pdf"
            # Ruta_a_guardad=""
            # try:
            #     print("tratandode guardar con ",nombre_archivo)
            #     with open(nombre_archivo, 'wb') as f:
            #         f.write(self.responsePost)
            # except Exception as e:
            #     self.statusPDF=False
            #     print("fallo al leer",e)
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
                self.statusPDF=True
                return True
            except Exception as e :
                print("error al leer pdf ",e )
                self.statusPDF=False
                return False
        else:
            self.statusPDF=False
            return False
    def get_Factura(self):
        return self.Factura
    
    async def Doit(self,imrpimirPdf=False):
        try:

            async with httpx.AsyncClient() as self.session:
                for a in range (0,self.total_times):
                    print(f"Intento general N:{a+1} ")
                    for i in range (0,self.get_times):
                        print(f"Intento {i+1} de GET")
                        if (await self.req_get() == True):
                            break
                        await asyncio.sleep(0.3)

                    for i in range (0,self.post_times):
                        print(f"Intento {i+1} de POST")
                        await asyncio.sleep(2)
                        if (await self.req_post() == True):
                            break
                        await asyncio.sleep(1)
                    
                    if imrpimirPdf:
                        pass
                        # for i in range (0,self.pdf_times):
                        #     print(f"Intento {i+1} de POST")
                        #     if (self.processPDF() == True):
                        #         break
                        # if self.statusPDF == False:
                        #     raise Exception (self.msgPDF)
                    if self.statusGet == True and  self.statusPost == True:
                        return True
                    await asyncio.sleep(1)
                if self.statusGet == False:
                        raise Exception (self.msgGet)
                if self.statusPost == False:
                        raise Exception (self.msgPost)
                return True
            
            #          
            
            
            
        except Exception as e :
            print(f"error en doit:  {e}")
            self.msgDoIt=e
            return False

# Creamos una sesión que manejará las cookies por nosotros.

if __name__ == "__main__":
    A=ObtenerFactura(get_url=get_url)
    asyncio.run( A.Doit())
    print(f"Get:{A.statusGet} Get_msg:{A.msgGet} Monto:{A.monto} Nit:{A.nitEmisor} \nPost:{A.statusPost}, Post_status:{A.msgPost}")
    # print(A.responsePost)
   