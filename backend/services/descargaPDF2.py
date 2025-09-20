#deprecated
import requests

from bs4 import BeautifulSoup
import PyPDF2
from io import BytesIO
import datetime
import asyncio
import httpx
import validators
import pandas as pd
import re
from urllib.parse import urlparse, parse_qs

# --- URLs ESPECÍFICAS PARA IMPUESTOS BOLIVIA ---
# URL para cargar la página y obtener los parámetros iniciales
get_url = 'https://siat.impuestos.gob.bo/consulta/QR?nit=176360023&cuf=C1129B1EA5B84FD1C229FA2CC46E6004BD8B1A7643DC55CF9AD81F74&numero=44463&t=2'

# URL a la que el formulario envía la petición POST para generar el archivo
post_url = 'https://siat.impuestos.gob.bo/consulta/public/QR.xhtml'

class ScraperError(Exception):
    """Clase base para errores de este scraper."""
    pass
class GETRequestError(Exception):
    """Error específico para cuando falla la petición GET inicial."""
    pass

class ObtenerFactura:
    """
    Realiza la petición a SIAT, maneja el ciclo de vida de JSF ViewState de forma
    inteligente, valida los datos de la página y descarga el PDF de la factura.
    """
    def __init__(self, url: str):
        if not isinstance(url, str) or not url.startswith('http'):
            raise TypeError("La entrada debe ser una URL válida en formato string.")
        self.post_url='https://siat.impuestos.gob.bo/consulta/public/QR.xhtml'
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        }

        # --- Parseo Robusto de la URL ---
        # Usamos la librería estándar de Python para analizar la URL.
        try:
            parsed_url = urlparse(self.url)
            params = parse_qs(parsed_url.query)

            # Extraemos los parámetros requeridos. parse_qs devuelve una lista, por eso [0].
            self.nitEmisor = params['nit'][0]
            self.Nfactura = params['numero'][0]
            self.cuf = params['cuf'][0]
            param_t = params['t'][0]

            # El ID del botón de descarga se calcula dinámicamente.
            # self.boton_id='formQr:j_idt218'
            # self.boton_id = f"formQr:j_idt{int(param_t) + 21}"

        except (KeyError, IndexError, ValueError) as e:
            raise ValueError(f"La URL no contiene los parámetros requeridos (nit, numero, cuf, t) o son inválidos. Error: {str(e)}")

        # Atributos para almacenar los resultados del scraping
        self.comercio = None
        self.monto = 0.0
        self.estado_fact_url=None  # valida o invalida no esta en la factura
        self.statusGet=None 
        self.msgGet=None
        self.statusPost=None# falta
        self.msgPost=None# falta
        

    def _extraer_nuevo_viewstate(self, xml_text: str) -> str | None:
        """Usa regex para extraer el ViewState de una respuesta XML de JSF."""
        # print("respuesta del post: ",xml_text, " \n procedemos a extraer nuevo viewstate")
        match = re.search(r"<update id=.*?javax\.faces\.ViewState.*?>\s*<!\[CDATA\[(.*?)\]\]>", xml_text)
        if match:
            nuevo_viewstate = match.group(1)
            print(f"INFO: Servidor envió un nuevo ViewState: {nuevo_viewstate}")
            return nuevo_viewstate
        return None

    def _validar_tabla_inicial(self, soup: BeautifulSoup) -> bool:
        """Valida que los datos de la tabla en la página coincidan con los de la URL."""
        print("el soup es .... ",soup)
        try:
            # Encuentra la fila de datos en la tabla
            fila = soup.select_one('#formQr\:idListaDatoSistema_data tr')
            

            if not fila:
                print("ERROR: No se encontró la tabla de datos en la página.")
                return False

            celdas = [td.get_text(strip=True) for td in fila.find_all('td')]
            
            # Comparamos los datos extraídos con los de la URL
            nit_tabla = celdas[1]
            nro_factura_tabla = celdas[3]
            monto_tabla = float(celdas[4])
            estado_tabla = celdas[5]
            self.estado_fact_url=estado_tabla
                

            if self.nitEmisor == nit_tabla and self.Nfactura == nro_factura_tabla and estado_tabla == "VALIDA":
                print("INFO: Los datos de la tabla coinciden con la URL. Factura VÁLIDA.")
                self.comercio = celdas[2]
                self.monto = monto_tabla
                return True
            
            else:

                   
                print("ERROR: Los datos de la tabla NO coinciden con la URL o la factura no es VÁLIDA.")
                return False
            
        except (AttributeError, IndexError, ValueError) as e:
            print(f"ERROR: Ocurrió un error al procesar la tabla de validación: {str(e)}")
            return False
    async def _obtener_estado_inicial(self, session: httpx.AsyncClient,validation=True):
        """
        Realiza la petición GET inicial y extrae toda la información necesaria:
        ViewState, ID del botón de descarga y valida los datos de la tabla.
        """
        print(f"INFO: Obteniendo estado inicial de {self.url[:50]}...")
        response_get = await session.get(self.url, headers=self.headers)
        if response_get.status_code ==503:
            raise GETRequestError("Servidor caido")

        response_get.raise_for_status()
        soup = BeautifulSoup(response_get.text, 'html.parser')
        if validation:
            print("validando tabla inciial ")
            if not (self._validar_tabla_inicial(soup=soup)):
                raise GETRequestError("No se valido la info del url con la tabla ")
            if not self.estado_fact_url :
                raise GETRequestError("Factura invalida en SIAT")
        

        # Extraer ViewState
        view_state_tag = soup.find('input', {'name': 'javax.faces.ViewState'})
        if not view_state_tag:
            raise ScraperError("No se pudo encontrar el ViewState inicial.")
        
        # --- LÓGICA CLAVE: EXTRAER EL ID DEL BOTÓN DINÁMICAMENTE ---
        # Buscamos el primer botón dentro del div con id 'ui-toolbar-group-left'
        #formQr\:j_idt247
            
        boton_tag = None
        
        # Intento 1: Selector de CSS por clase de contenedor (Recomendado)
        selector_1 = 'div.ui-toolbar-group-left button'
        boton_tag = soup.select_one(selector_1)
        print(f"INFO: Intentando con selector: '{selector_1}'... {'Encontrado!' if boton_tag else 'No encontrado.'}")
        # Intento 2: Búsqueda por texto (si el intento 1 falla)
        if not boton_tag:
            # re.compile es para buscar texto que contenga "Ver Factura", ignorando mayúsculas/minúsculas
            boton_tag = soup.find('button', string=re.compile(r'Ver Factura', re.IGNORECASE))
            print(f"INFO: Intentando con búsqueda de texto 'Ver Factura'... {'Encontrado!' if boton_tag else 'No encontrado.'}")

        # Comprobación final
        if not boton_tag or not boton_tag.has_attr('id'):
            raise ScraperError("No se pudo encontrar el ID del botón de descarga con ninguna de las estrategias.")
        
        boton_id = boton_tag['id']
        print(f"INFO: ID del botón de descarga final encontrado: '{boton_id}'")

        # (Aquí tu lógica de validación de la tabla)
        
        return view_state_tag['value'], boton_id
    
    async def descargar_pdf(self, max_intentos_post: int = 3,timeout: float = 30.0):
        """
        Orquesta el proceso de GET y POST de forma inteligente.
        Retorna una tupla: (contenido_del_pdf_en_bytes, mensaje_de_estado)
        """
        async with httpx.AsyncClient(timeout=timeout) as session:
            try:
                current_viewstate, boton_id_dinamico = await self._obtener_estado_inicial(session)
                self.msgGet="Succes"
                self.statusGet=True
            except (httpx.RequestError, GETRequestError) as e:
                print("error get",e)
                self.msgGet=str(e)
                self.statusGet=False
                return None, f"CRITICAL:  {str(e)}"
            
            except ScraperError as e :
                print("error Scrapper",e)
                self.msgGet="WARNIG:"+str(e)
                self.statusGet=True
                return None, f"WARNIG::  {str(e)}"

            # --- BUCLE DE POST INTELIGENTE ---
            for i in range(max_intentos_post):
                print(f"INFO: Intento de POST N°{i+1}/{max_intentos_post} con ID: '{boton_id_dinamico}'...")
                form_data = {
                    'formQr': 'formQr',
                    'formQr:idTipoSistema': '1',
                    boton_id_dinamico: '', # <-- Usamos el ID dinámico
                    'javax.faces.ViewState': current_viewstate,
                    'javax.faces.source': boton_id_dinamico, # <-- Usamos el ID dinámico
                    'javax.faces.partial.ajax': 'true',
                    'javax.faces.partial.execute': '@all',
                }
                post_headers = self.headers.copy()
                post_headers['Faces-Request'] = 'partial/ajax'
                post_headers['Referer'] = self.url 
                try:
                    response_post = await session.post(self.post_url, data=form_data, headers=post_headers)
                    content_type = response_post.headers.get('Content-Type', '')

                    if 'application/pdf' in content_type:
                        print("✅ Éxito! PDF descargado.")
                        self.msgPost="Succes"
                        self.statusPost=True
                        return response_post.content, "Descarga exitosa"
                    
                    elif 'text/xml' in content_type:
                        print("txto ")
                        # ✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅
                        try:
                            # print("cokkies ", session.cookies)
                            current_viewstate, boton_id_dinamico = await self._obtener_estado_inicial(session,validation=False)
                            continue
                        except (httpx.RequestError, GETRequestError,ScraperError) as e:
                            print("error get",e)
                            self.msgPost="Error al reintentar obtenener el viewstate"
                            self.statusPost=False
                            return None, f"CRITICAL: Falló la obtención del estado inicial en reintento: {str(e)}"
                        # ✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅
                        #               SOLAMENTE CAMBIA EL VIEWSTATE DE ACUERDO A LA RESPUESTA XML 
                        # nuevo_viewstate = self._extraer_nuevo_viewstate(response_post.text)
                        # if nuevo_viewstate:
                        #     current_viewstate = nuevo_viewstate
                        #     await asyncio.sleep(1)
                        #     continue
                        else: return None, "ERROR: XML inesperado sin nuevo ViewState."
                    else: 
                        print(f"ERROR: Respuesta inesperada (Content-Type: {response_post}).")
                        self.msgPost=f"Error Respuesta inesperada {content_type} "
                        self.statusPost=False
                        return None, f"ERROR: Respuesta inesperada (Content-Type: {content_type})."
                
                except httpx.RequestError as e:
                    print(f"WARN: Error de red durante el POST: {e}. Reintentando...")
                    await asyncio.sleep(2)
                except Exception as e:
                    print(f"error en post general {e}")

            self.msgPost=f"Error despues de {max_intentos_post} intentos "
            self.statusPost=False
            print("despues de intentos mn ose logro.")
            return None, f"ERROR: No se pudo obtener el PDF después de {max_intentos_post} intentos."

    async def get_pdf(self):
        pass


# ⚠️ falta ver todos los status post get y demas que estan en los schemas para obtener los mismos con sus respuestas 
# y usar directametne este pdf en el procesador de factura 
# Creamos una sesión que manejará las cookies por nosotros.

if __name__ == "__main__":
    A=ObtenerFactura(url=get_url)
    data=asyncio.run( A.descargar_pdf())

    print("GET: ",A.statusGet," ",A.msgGet)
    print("POST: ",A.statusPost," ",A.msgPost)
    print("pdf: ",data[1])
    # print(f"Get:{A.statusGet} Get_msg:{A.msgGet} Monto:{A.monto} Nit:{A.nitEmisor} \nPost:{A.statusPost}, Post_status:{A.msgPost}")
    # print(A.responsePost)
   