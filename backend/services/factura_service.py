from .NewSiatdescargaPDF import downloadFactura
from .processPDF import ProcesadorPDF_Rollo
# from FacturaOb import FacturaElectronica
from backend.schemas import DetalleItem,FacturaElectronicaCreate

from backend.crud import crud_facturas_electronicas
from backend.db.database import AsyncSessionLocal
import asyncio
from io import BytesIO
from backend.config import FACTURAS_DIR

async def procesar_factura_completa_desde_url(url: str, save_pdf: bool = False) -> FacturaElectronicaCreate:
    """
    Orquesta el proceso de descarga y procesamiento, capturando resultados parciales y errores.
    """
    # 1. Descargar los datos iniciales (GET) y el PDF (POST)
    data_scraped,pdfRuta = await downloadFactura(url_factura=url,savePdf=save_pdf)
    

    
    # Preparamos un diccionario con los datos que tenemos hasta ahora, incluyendo el estado.
    datos_factura = {
        "url": url,
        "monto_total": data_scraped.monto or 0.0,
        "empresa": data_scraped.comercio,
        "nit_emisor": data_scraped.nitEmisor,
        "n_factura": int(data_scraped.nFactura) if data_scraped.nFactura else None,
        "status_Getrequest": data_scraped.statusGet,
        "msg_get_request": data_scraped.msgGet,
        "status_Postrequest": data_scraped.statusPost,
        "msg_post_request": data_scraped.msgPost,
        "save_pdf": save_pdf,
        "fecha":data_scraped.get_datetime(),
        "Nit_Beneficiario":data_scraped.nitBeneficiario
    }

    # 2. Si la descarga del PDF fue exitosa, intentamos procesarlo
    if data_scraped.statusPost and save_pdf:
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
            "status_PDFrequest": all(valor[1] for valor in pdf_processor.get_controlador().values()),
            "msg_pdf_request": pdf_processor.get_controlador(),
            "pdfIO":str(pdfRuta)if save_pdf else None

        })

        
        
    else:
        # Si la descarga del PDF falló, llenamos los campos restantes con valores por defecto
        datos_factura["status_PDFrequest"] = False
        datos_factura["msg_pdf_request"] = {"error": "No se pudo descargar el PDF para procesarlo."}


    # 3. Creamos el objeto Pydantic final con todos los datos recopilados
    factura_final = FacturaElectronicaCreate(**datos_factura)

    return factura_final


# --- Tarea para BackgroundTasks (como vimos antes) ---

async def tarea_de_scraping_y_actualizacion(factura_id: int, url: str,savePdf:bool=False):
    """
    Tarea en segundo plano que usa el nuevo servicio.
    """
    print(f"Tarea en segundo plano iniciada para factura ID: {factura_id}")
    try:
        # 1. Llama a la función orquestadora para obtener el objeto Pydantic completo
        datos_completos = await procesar_factura_completa_desde_url(url=url,save_pdf=savePdf)
        
        # 2. Crea una nueva sesión de DB
        async with AsyncSessionLocal() as db:
            # 3. Llama al CRUD para actualizar la factura
           db_fact_update= await crud_facturas_electronicas.update_factura_desde_scraping(
                db=db, 
                factura_id=factura_id, 
                datos_completos=datos_completos
            )
        print(f"Tarea en segundo plano completada para factura ID: {factura_id}, empresa encontra:{datos_completos.empresa}  get_status:{datos_completos.status_Getrequest}, post_status:{datos_completos.status_Postrequest} ")
        return db_fact_update
    except Exception as e:
        print(f"Error en la tarea en segundo plano para factura ID {factura_id}: {e}")
        # Aquí podrías actualizar la factura con un estado de "error"