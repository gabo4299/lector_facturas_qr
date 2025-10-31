import base64
import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from .NewSiatdescargaPDF import downloadFactura
from .processPDF import ProcesadorPDF_Rollo
# from FacturaOb import FacturaElectronica
from backend.schemas import DetalleItem,FacturaElectronicaCreate,FacturaElectronicaCreateScrapping

from backend.crud import crud_facturas_electronicas
from backend.db.database import AsyncSessionLocal
import asyncio
from io import BytesIO
from backend.config import FACTURAS_DIR,BACKEND_DIR
import httpx
class FacturaValidationError(Exception):
    """Clase base para errores de este scraper."""
    pass

DATA_ENDPOINT_URL = "https://siatrest.impuestos.gob.bo/sre-sfe-shared-v2-rest/consulta/factura"
PDF_ENDPOINT_URL = "https://siatrest.impuestos.gob.bo/sre-sfe-shared-v2-rest/consulta/representacionGrafica"

async def getPDFSiat(cuf:str,nit:str,nFact:int,rollo:bool=True):
    async with httpx.AsyncClient(timeout=30.0) as client:
        if rollo :
            tam=1
        else:
            tam=0
        print("INFO: Obteniendo pdf de la factura vía API...")
        headers_data = {"Content-Type": "application/json", "Accept": "application/json"}
        payload_data = {"cuf": cuf, "nit": nit,"numeroFactura":nFact,"tamanio":tam} # Ejemplo
        
        response_data = await client.put(PDF_ENDPOINT_URL, json=payload_data, headers=headers_data)
        response_data.raise_for_status() # Lanza un error si el status no es 2xx
        
        datos_crudos = response_data.json()
        
        if datos_crudos.get("transaccion") == True:
            data_factura=datos_crudos.get("representacionGrafica")
            return data_factura
        else :
            # print("error  al descargar pdf")
            return None

async def getDataSiat(cuf:str,nit:str,nFact:int):
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("INFO: Obteniendo datos de la factura vía API...")
            
        # Construye las cabeceras y el payload que descubriste
        headers_data = {"Content-Type": "application/json", "Accept": "application/json"}
        payload_data = {"cuf": cuf, "nitEmisor": nit,"numeroFactura":nFact} # Ejemplo
        
        response_data = await client.put(DATA_ENDPOINT_URL, json=payload_data, headers=headers_data)
        response_data.raise_for_status() # Lanza un error si el status no es 2xx
        
        datos_crudos = response_data.json()
        if datos_crudos.get("transaccion") == True:
            data_factura=datos_crudos.get("objeto")
            return data_factura
        else :
            print("error ")
            raise Exception("Fallo al hacer fetch")

async def procesar_factura_completa_desde_url (url: str,
                                                save_pdf: bool = False):
    parsed_url = urlparse(url)
    datos_factura={"url": url,"complete": False}
    if parsed_url.netloc == "siat.impuestos.gob.bo":
        try :
            params = parse_qs(parsed_url.query)
            url_nitEmisor = params['nit'][0]
            url_Nfactura = params['numero'][0]
            url_cuf = params['cuf'][0]
            
        except :
            print("error en la url siat faltan datos ")
            datos_factura["complete"]=False
            datos_factura["status"]="error en la url siat faltan datos"
            return datos_factura
        
        try:
            data=await getDataSiat(url_cuf,url_nitEmisor,url_Nfactura)
            if not data:
                raise Exception ("objeto de datos vacio .. getDataSiat")
            
            datos_factura["monto_total"]= round(float(data.get("montoTotal")),2) or 0.0
            datos_factura["empresa"]= data.get("razonSocialEmisor")
            datos_factura["nit_emisor"]= str(data.get("nitEmisor"))
            datos_factura["n_factura"]= int(data.get("numeroFactura")) if data.get("numeroFactura") else None
            datos_factura["save_pdf"]= save_pdf
            datos_factura["fecha"]=datetime.datetime.strptime(data.get("fechaEmision"), "%Y-%m-%dT%H:%M:%S.%f") or None
            datos_factura["Nit_Beneficiario"]=data.get("numeroDocumento")
            datos_factura["status"]= "Complete"
            datos_factura["complete"]= True
            datos_factura["monto_fiscal"]=-1
            
            
        except Exception as e:
            print('error en la getdata: ' ,e )
            datos_factura["complete"]=False
            datos_factura["status"]=f"Error al solicitar datos: {e}"
            return datos_factura

        if save_pdf :
                pdfBytes=await getPDFSiat(url_cuf,url_nitEmisor,url_Nfactura)
                if not pdfBytes:
                    datos_factura["complete"]=False
                    datos_factura["status"]=f"Error al descargar PDF del servidor"
                    return datos_factura
                try:
                    pdfBytes=base64.b64decode(pdfBytes) 
                except :
                    datos_factura["complete"]=False
                    datos_factura["status"]=f"Error al convertir a pdf"
                    return datos_factura
                path=FACTURAS_DIR
                if type (path) == type("str"):
                    ruta = Path(path)
                    if not ruta.exists():
                        datos_factura["complete"]=False
                        datos_factura["status"]=f"Error en el path de guardado"
                        return datos_factura
                    path = Path(path)

                pdf_stream = BytesIO(pdfBytes)
                try :
                    # print("intentao guardar en ", path)
                    nombre_archivo=datos_factura["nit_emisor"]+"_"+datos_factura["fecha"].strftime("%Y-%m-%d")+"_factN_"+str(datos_factura["n_factura"])+".pdf"
                    file_path = path / nombre_archivo
                    with open(file_path, "wb") as f:
                        f.write(pdf_stream.getvalue())
                except Exception as e :
                    datos_factura["complete"]=False
                    datos_factura["status"]=f"Error al guardar  pdf : {e}"
                    return datos_factura
                pdf_processor = await ProcesadorPDF_Rollo.crear(BytesEntrada=pdf_stream, Modo=1)
                datos_factura.update({

                        "detalles": pdf_processor.get_detalle(),
                        "monto_fiscal": pdf_processor.get_monto_fiscal(),
                        "factura_especial": pdf_processor.facturaEspecial,
                        "pdfIO":str((file_path.relative_to(BACKEND_DIR)).as_posix())if save_pdf else None
                    })
    else:
        # ver si se hara de kingdom 🚩
        datos_factura["complete"]=False
        datos_factura["status"]=f"Error al solicitar datos: {e}"
    
    return datos_factura



# --- Tarea para BackgroundTasks (como vimos antes) ---

async def tarea_de_scraping_y_actualizacion(factura_id: int, url: str,proyect_id:int,savePdf:bool=False):
    
    """
    Tarea en segundo plano que usa el nuevo servicio.
    """
    
    try:
    

        datos_factura = await procesar_factura_completa_desde_url(url=url,save_pdf=savePdf)
        # print("\n \n \n \n  aqui estan los datos",datos_factura)
        # 2. Crea una nueva sesión de DB

        async with AsyncSessionLocal() as db:
            # 3. Llama al CRUD para actualizar la factura
           db_fact_update= await crud_facturas_electronicas.update_factura_desde_scraping(
                db=db, 
                factura_id=factura_id, 
                datos_completos=FacturaElectronicaCreateScrapping(**datos_factura,proyecto_id=proyect_id)
            )
        
        return db_fact_update

    except Exception as e:
        print(f"   Tipo de Error: {type(e).__name__}")
        print(f"Error en la tarea en segundo plano para factura ID {factura_id}: {e}")
        async with AsyncSessionLocal() as db:
            # 3. Llama al CRUD para actualizar 
            crud_facturas_electronicas.update_status_factura_electronica(db,factura_id,f"Error en el proceso { {type(e).__name__}}",False)
        # Aquí podrías actualizar la factura con un estado de "error"




if __name__ == '__main__':
    # asyncio.run(actualizacionFactuas())
    pass
