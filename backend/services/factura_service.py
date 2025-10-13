from .NewSiatdescargaPDF import downloadFactura
from .processPDF import ProcesadorPDF_Rollo
# from FacturaOb import FacturaElectronica
from backend.schemas import DetalleItem,FacturaElectronicaCreate,FacturaElectronicaCreateScrapping

from backend.crud import crud_facturas_electronicas
from backend.db.database import AsyncSessionLocal
import asyncio
from io import BytesIO
from backend.config import FACTURAS_DIR
class FacturaValidationError(Exception):
    """Clase base para errores de este scraper."""
    pass
async def procesar_factura_completa_desde_url(url: str,
                                                save_pdf: bool = False) -> FacturaElectronicaCreate:
    """
    Orquesta el proceso de descarga y procesamiento, capturando resultados parciales y errores.
    el 30/09/2025 se hizo cambio fuerte en data_scraped,pdfRuta envez de await un asyncio to thread
    """
    # 1. Descargar los datos iniciales (GET) y el PDF (POST)
    # data_scraped,pdfRuta = await downloadFactura(url_factura=url,savePdf=save_pdf)
    data_scraped, pdfRuta = await asyncio.to_thread(
            downloadFactura,    # La función síncrona a ejecutar
            url_factura=url,    # Argumentos para esa función
            savePdf=save_pdf
        )
    
    


    # Preparamos un diccionario con los datos que tenemos hasta ahora, incluyendo el estado.
    datos_factura = {
        "url": url,
        "monto_total": data_scraped.monto or 0.0,
        "empresa": data_scraped.comercio,
        "nit_emisor": data_scraped.nitEmisor,
        "n_factura": int(data_scraped.nFactura) if data_scraped.nFactura else None,
        "status": data_scraped.status,
        "complete": data_scraped.complete,
        "save_pdf": save_pdf,
        "fecha":data_scraped.get_datetime(),
        "Nit_Beneficiario":data_scraped.nitBeneficiario
    }

    # 2. Si la descarga del PDF fue exitosa, intentamos procesarlo
    if data_scraped.complete and save_pdf:
        pdf_bytes = None
        with open(pdfRuta, 'rb') as f:
            pdf_read = f.read()

        # Paso 2: Cargar los bytes en un objeto BytesIO
        pdf_bytes = BytesIO(pdf_read)
        pdf_processor = await ProcesadorPDF_Rollo.crear(BytesEntrada=pdf_bytes, Modo=1)
        
        # Agregamos los datos extraídos del PDFsa
        
        
        

        datos_factura.update({
            # "Nit_Beneficiario": pdf_processor.get_nit_beneficiario(),
            # "fecha": pdf_processor.get_datetime(),
            "detalles": pdf_processor.get_detalle(),
            "monto_fiscal": pdf_processor.get_monto_fiscal(),
            "factura_especial": pdf_processor.facturaEspecial,
            "pdfIO":str(pdfRuta)if save_pdf else None

        })
        
        
        


    # 3. Creamos el objeto Pydantic final con todos los datos recopilados
    # antes de crear se debe hacer validaciones de empresa y fechas 
    # aquimequede
    #= despues de comprobar nit 
    
    
    # print(f"lo que se crea es {datos_factura}")

    # factura_final = FacturaElectronicaCreateScrapping(**datos_factura,proyecto_id=proyect_id)

    return datos_factura


# --- Tarea para BackgroundTasks (como vimos antes) ---

async def tarea_de_scraping_y_actualizacion(factura_id: int, url: str,proyect_id:int,savePdf:bool=False):
    
    """
    Tarea en segundo plano que usa el nuevo servicio.
    """
    print(f"Tarea en segundo plano iniciada para factura ID: {factura_id}")
    try:
        # 1. Llama a la función orquestadora para obtener el objeto Pydantic completo

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
        # Aquí podrías actualizar la factura con un estado de "error"


# async def actualizacionFactuas (filtro=""):
#     try:
#         async with AsyncSessionLocal() as db:
#             print("empezando con ",db)
#             lista_facturas=await crud_facturas_electronicas.get_facturas_incompletas(db)
#             for i in lista_facturas:
#                 print("\n\n\n\n\n\n\n",i,i.complete,i.empresa,i.url,i.monto_fiscal,i.status)
#                 # mientras veremos el montofiscal sea = 0.0
#                 # falta la validacion 
#                 await asyncio.sleep(4)
#                 datos_factura = await procesar_factura_completa_desde_url(url=i.url,save_pdf=i.save_pdf)
#                 db_fact_update= await crud_facturas_electronicas.update_factura_desde_scraping(
#                     db=db, 
#                     factura_id=i.id, 
#                     datos_completos=FacturaElectronicaCreateScrapping(**datos_factura,proyecto_id=i.proyecto_id)
#                 )
#         return True
#     except Exception as e:
#         print ("\n\n\n\n Error al momento de actualizar las faltantes ",e)
#         return False

if __name__ == '__main__':
    # asyncio.run(actualizacionFactuas())
    pass
