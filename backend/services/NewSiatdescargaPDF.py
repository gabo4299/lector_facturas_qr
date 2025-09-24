# 17 de septiembre descarga el pdf y souop para hacer scrapping validadcion 

import asyncio
from playwright_stealth import Stealth
from bs4 import BeautifulSoup
import asyncio
import datetime
from playwright.async_api import async_playwright
import re
from urllib.parse import urlparse, parse_qs
from backend.config import FACTURAS_DIR
from pathlib import Path
url_scraper="https://siat.impuestos.gob.bo/consulta/QR?nit=320876029&cuf=15F489E0D6750AAA8211EC26FF7AA7CA40D92202E7927ABFE56971F74&numero=43163&t=1"
poison_script = """
            console.log('☢️ Desplegando Antídoto de Envenenamiento del Depurador...');

            let lastTime = performance.now();
            let debuggerDetected = false;

            // 1. Sobrescribimos la función 'now' de 'performance' para que mienta sobre el tiempo.
            const originalPerformanceNow = performance.now;
            performance.now = () => {
                // Si detectamos una llamada a 'debugger', devolvemos el mismo tiempo para que la diferencia sea 0.
                if (debuggerDetected) {
                    debuggerDetected = false;
                    return lastTime;
                }
                lastTime = originalPerformanceNow();
                return lastTime;
            };
            
            // 2. Sobrescribimos la función 'toString' de las funciones de la consola.
            // Algunos scripts verifican si 'console.log.toString()' ha sido modificado.
            const originalToString = Function.prototype.toString;
            Function.prototype.toString = function(...args) {
                if (this.name.startsWith('bound ') || this.name === 'now') {
                    return 'function ' + this.name + '() { [native code] }';
                }
                return originalToString.apply(this, args);
            };

            // 3. Creamos un "worker" que se ejecuta en un hilo separado para detectar 'debugger'.
            // Esto es más difícil de bloquear para la página.
            const workerCode = `
                self.onmessage = function() {
                    setInterval(() => {
                        postMessage('debugger');
                    }, 500);
                };
            `;
            const blob = new Blob([workerCode], { type: 'application/javascript' });
            const worker = new Worker(URL.createObjectURL(blob));
            
            worker.onmessage = (e) => {
                if (e.data === 'debugger') {
                    debuggerDetected = true;
                    // Forzamos la ejecución de una función nuestra para que el 'debugger' se evalúe.
                    (()=>{}).constructor('debugger')();
                }
            };
            worker.postMessage('start');
        """
interceptor_script = """
            console.log('👮‍♂️ Desplegando el Interceptor de "addEventListener"...');

            // Guardamos una copia de la función original
            const originalAddEventListener = EventTarget.prototype.addEventListener;

            // La reemplazamos con nuestra versión "proxy"
            EventTarget.prototype.addEventListener = function(type, listener, options) {
                // Verificamos si la página intenta añadir un "escuchador" para eventos que queremos bloquear
                if (type === 'keydown' || type === 'keyup' || type === 'contextmenu') {
                    console.warn(`INTERCEPTADO: La página intentó añadir un bloqueador para el evento '${type}'. Petición denegada.`);
                    // Simplemente no hacemos nada y la petición de la página se desvanece
                    return;
                }

                // Si es cualquier otro evento, lo dejamos pasar a la función original para que la página funcione
                return originalAddEventListener.call(this, type, listener, options);
            };
        """

class ResponseModel:
    def __init__(self):
        self.comercio = None
        self.monto =0.0
        self.estado_fact_url=None  # valida o invalida no esta en la factura
        self.statusGet=None 
        self.msgGet=None
        self.statusPost=None# falta
        self.msgPost=None# falta
        self.nitEmisor=None
        self.nFactura=None
        self.cuf=None
        self.nitBeneficiario=None
        self.fecha=None
        self.nombreBeneficiario=None
    def __str__(self):
        validez=f"'Factura Valida':{self.estado_fact_url} Fecha:{self.fecha}"
        com=f"'Comercio ':{self.comercio} 'NIT':{self.nitEmisor} 'Numero Factura':{self.nFactura}"
        cliente=f"a Nombre de {self.nombreBeneficiario} NIT:{self.nitBeneficiario} MONTO:{self.monto} "
        extradata=f"GET:{self.statusGet} , {self.msgGet}\nPOST:{self.statusPost} , {self.msgPost}\n CUF:{self.cuf}"

        div1="#########################FACTURA#############################################"
        div2="#########################COMERCIO############################################"
        div3="#########################CLIENTE#############################################"
        div4="#########################ESTADOS#############################################"

        estructura=f"{div1}\n{validez}\n{div2}\n{com}\n{div3}\n{cliente}\n{div4}\n{extradata}"

        return estructura
    def get_datetime(self):
        try:
            fec=datetime.datetime.strptime(self.fecha, "%d/%m/%Y %H:%M:%S")
            return fec
        except :
            print("errro al tratar de obtenre un datetime de fecha")
            return datetime.datetime(year=1999, month=1, day=1)
    def getDict(self):
        return {
        "comercio" : self.comercio,
        "monto" :self.monto,
        "estado_fact_url":self.estado_fact_url,  # valida o invalida no esta en la factura
        "statusGet":self.statusGet,
        "msgGet":self.msgGet,
        "statusPost":self.statusPost,# falta
        "msgPost":self.statusPost,# falta
        "nitEmisor":self.nitEmisor,
        "nFactura":self.nFactura,
        "cuf" :self.cuf,
        "nitBeneficiario":self.nitBeneficiario,
        "fecha":self.fecha,
        "nombreBeneficiario":self.nombreBeneficiario
            }
response_model=ResponseModel()


class ScraperError(Exception):
    """Clase base para errores de este scraper."""
    pass
class GETRequestError(Exception):
    """Error específico para cuando falla la petición GET inicial."""
    pass

class PDFRequestError(Exception):
    """Error específico para cuando falla la petición Descarga."""
    pass
def getScrapp(data):
    global response_model
    try:
        soup = BeautifulSoup(data, 'html.parser')
        datos_factura = {}
        key_map = { "Número de Factura:": "numero_factura", #✅
                    "CUF:": "cuf",#✅
                    "Fecha Emisión:": "fecha_emision",#✅
                    "Monto Total:": "monto_total",#✅
                    "Estado de la Factura:": "estado_factura", #✅
                    "NIT Emisor:": "nit_emisor", #✅
                    "Razón Social:": "razon_social_emisor",#✅
                    "Nombre / Razón Social:": "nombre_cliente",#✅ 
                    "Número Documento:": "documento_cliente" #✅
                      }
        all_labels = soup.find_all('span', class_='f-w-600')
        for label_span in all_labels:
            label_text = label_span.text.strip()
            if label_text in key_map:
                value_span = label_span.find_next_sibling('span')
                if value_span:
                    if label_text== "Monto Total:":
                        numero = re.findall(r"\d+\.\d+", value_span.text.strip())
                        # Si se encontró el número, lo convertimos a float
                        if numero:
                            numero_float = float(numero[0])
                            
                            datos_factura[key_map[label_text]] = numero_float
                        else:
                            datos_factura[key_map[label_text]] = 0.0
                    else:
                        datos_factura[key_map[label_text]] = value_span.text.strip()
        return datos_factura,True
    except Exception as e:
        print(f"Error aqui  {e}")
        return None,e
async def downloadFactura(url_factura=url_scraper,
               savePdf=False,
               path=FACTURAS_DIR) ->tuple[ResponseModel,None|str]:
    
    pdf_io=None
    async with async_playwright() as p:
        try:
            if not isinstance(url_factura, str) or not url_factura.startswith('http'):
                raise GETRequestError(" URL ERROR La entrada debe ser una URL válida en formato string.")

            
            try : 
                parsed_url = urlparse(url_factura)
                params = parse_qs(parsed_url.query)
                url_nitEmisor = params['nit'][0]
                url_Nfactura = params['numero'][0]
                url_cuf = params['cuf'][0]

            except:
                raise  GETRequestError(" URL ERROR no se pudieron extraer los parametros cuf,numero y nit")

            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            # evitamos cargas inesesarias 
            await page.route(re.compile(r"\.(jpg|jpeg|png|gif|svg|woff|woff2|ttf|css)$"), lambda route: route.abort())
            
            #  inyectamos los scripts
            await context.add_init_script(poison_script)
            await context.add_init_script(interceptor_script)

       
            # print("Navegando al sitio con el antídoto inyectado...")
            try:
                response= await page.goto(url_factura, timeout=60000, wait_until='networkidle')
            except Exception as e :
                raise GETRequestError(f"error talvez URL : {str(e)}")
            # #  MEJORA antes teniamos esta linea y wait until era 'domcontentloaded'
            # # Damos tiempo a que la aplicación React cargue y renderice todo
            # await page.wait_for_load_state('networkidle', timeout=30000)
            # print("respuesta",response, response.ok)
            if not response.ok:
                raise GETRequestError(f"Servidor caido  code: {str(response.status)}")
            # print ("estatus response ", response.status)
            error_locator = page.locator('text="Factura no encontrada"')
            error_locator2 = page.locator('text="No se puede acceder a este sitio web"')
            if await error_locator2.is_visible():
                raise GETRequestError("No se puede acceder a SIAT ")
                
            if await error_locator.is_visible():
                raise GETRequestError("Factura incorrecta verifique url")
                
            response_model.statusGet=True
            response_model.msgGet="Succes"
            print("✅ ¡Éxito! La página cargó, las defensas fueron neutralizadas.")
            # verificamos el mat-card esto podria cambiar despues atento al sitio 
            try:
                html_content = await page.locator('mat-card-content:has-text("Detalle de la Factura")').inner_html()
            except:
                raise ScraperError("Error no se encontro contenedor de los datos")
            
            scraper=getScrapp(html_content)
            data=scraper[0]
            if data:
                print("exxtraccion exitosa ")
                for key, value in data.items():
                    print(f"{key}: {value}")
                response_model.nFactura=int(data["numero_factura"])
                response_model.cuf=data["cuf"]
                response_model.fecha=data["fecha_emision"]
                response_model.monto=float(data["monto_total"])
                response_model.estado_fact_url=data["estado_factura"]
                response_model.nitEmisor=data["nit_emisor"]
                response_model.comercio=data["razon_social_emisor"]
                response_model.nombreBeneficiario=data["nombre_cliente"]
                response_model.nitBeneficiario=data["documento_cliente"]

            else:
                raise ScraperError(f"Error en scrapping {scraper[1]}")
            
            response_model.statusPost=True
            response_model.msgPost="Succes"
            # validar????? no lo se 

            if savePdf:
                
                print("Iniciando secuencia de descarga del PDF...")
                
                try:
                    if type (path) == type("str"):
                        ruta = Path(path)
                        if not ruta.exists():
                            print("¡La ruta existe!")
                            raise PDFRequestError(" error en la path de guardado")
                        path = Path(path)
                    # Preparamos a Playwright para que espere una descarga.
                    async with page.expect_download() as download_info:
                        # 1. Localizamos el botón "Descargar Factura" por su texto y hacemos clic.
                        #    Esto abrirá el menú desplegable.
                        await page.get_by_role("button", name="Descargar Factura").click()
                        
                        # 2. Localizamos la opción "ROLLO" en el menú que acaba de aparecer y hacemos clic.
                        #    Playwright esperará automáticamente a que este elemento sea visible.
                        await page.get_by_role("menuitem", name="ROLLO").click()
                    
                    # 3. La descarga ya ha sido capturada por 'download_info'.
                    download = await download_info.value
                    
                        
                    nombre_archivo=data["nit_emisor"]+"_"+response_model.get_datetime().strftime("%Y-%m-%d")+"_factN_"+str(response_model.nFactura)+".pdf"
                    file_path = path / nombre_archivo

                    await download.save_as(file_path)
                    pdf_io=file_path
                    print(f"🎉 ¡PDF descargado con éxito! Guardado como: {file_path}")
                except Exception as e:
                    raise PDFRequestError(f"error al descargar pdf {e}")
            
            # return response_model,pdf_io
        except GETRequestError as e:
            print(f"Error GET: {e}")
            response_model.msgGet=f"Error GET: {str(e)}"
            response_model.statusGet=False
        except ScraperError as e:
            print(f"Error scrapping: {e}")
            response_model.msgPost=f"Error Scrapping: {str(e)}"
            response_model.statusPost=False
            
        except PDFRequestError as e :
            response_model.msgPost=f"Error PDF: {str(e)}"
            response_model.statusPost=False
            
        except Exception as e:
            print(f"❌ Ocurrió un error: {e}")
            response_model.msgPost=f"Error desconocido: {str(e)}"
            response_model.statusPost=False
            response_model.msgGet=f"Error desconocido: {str(e)}"
            response_model.statusGet=False
        except KeyboardInterrupt :
            print(f"❌ keyboard interrupt: ")
            response_model.msgPost=f"se cancelo manualmente"
            response_model.statusPost=False
            response_model.msgGet=f"se cancelo manualmente"
            response_model.statusGet=False

        finally:
            print("La automatización ha terminado")
            await browser.close()
            return response_model,pdf_io

if __name__ == '__main__':
    response=asyncio.run(downloadFactura(savePdf=True))
    print("mensaje : \n",response[0],response[1])
