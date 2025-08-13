from .descargaPDF import ObtenerFactura
from .processPDF import ProcesadorPDF_Rollo
# from FacturaOb import FacturaElectronica
from backend.schemas import DetalleItem,FacturaElectronicaCreate

from backend.crud import crud_facturas_electronicas
from backend.db.database import AsyncSessionLocal
import asyncio
from io import BytesIO

async def procesar_factura_completa_desde_url(url: str, save_pdf: bool = False) -> FacturaElectronicaCreate:
    """
    Orquesta el proceso de descarga y procesamiento, capturando resultados parciales y errores.
    """
    # 1. Descargar los datos iniciales (GET) y el PDF (POST)
    http_downloader = ObtenerFactura(get_url=url)
    await http_downloader.Doit()

    # Preparamos un diccionario con los datos que tenemos hasta ahora, incluyendo el estado.
    datos_factura = {
        "url": url,
        "monto_total": http_downloader.monto or 0.0,
        "empresa": http_downloader.comercio,
        "nit_emisor": http_downloader.nitEmisor,
        "n_factura": int(http_downloader.Nfactura) if http_downloader.Nfactura else None,
        "status_Getrequest": http_downloader.statusGet,
        "msg_get_request": http_downloader.msgGet,
        "status_Postrequest": http_downloader.statusPost,
        "msg_post_request": http_downloader.msgPost,
        "save_pdf": save_pdf,
    }

    # 2. Si la descarga del PDF fue exitosa, intentamos procesarlo
    if http_downloader.statusPost and http_downloader.responsePost:
        pdf_bytes = http_downloader.responsePost
        pdf_processor = await ProcesadorPDF_Rollo.crear(BytesEntrada=BytesIO(pdf_bytes), Modo=1)
        
        # Agregamos los datos extraídos del PDF
        datos_factura.update({
            "Nit_Beneficiario": pdf_processor.get_nit_beneficiario(),
            "fecha": pdf_processor.get_datetime(),
            "detalles": pdf_processor.get_detalle(),
            "monto_fiscal": pdf_processor.get_monto_fiscal(),
            "factura_especial": pdf_processor.facturaEspecial,
            "status_PDFrequest": all(valor[1] for valor in pdf_processor.get_controlador().values()),
            "msg_pdf_request": pdf_processor.get_controlador(),
            "pdfIO":pdf_bytes if save_pdf else None

        })
        
        
    else:
        # Si la descarga del PDF falló, llenamos los campos restantes con valores por defecto
        datos_factura["status_PDFrequest"] = False
        datos_factura["msg_pdf_request"] = {"error": "No se pudo descargar el PDF para procesarlo."}


    # 3. Creamos el objeto Pydantic final con todos los datos recopilados
    factura_final = FacturaElectronicaCreate(**datos_factura)

    return factura_final


# --- Tarea para BackgroundTasks (como vimos antes) ---

async def tarea_de_scraping_y_actualizacion(factura_id: int, url: str):
    """
    Tarea en segundo plano que usa el nuevo servicio.
    """
    print(f"Tarea en segundo plano iniciada para factura ID: {factura_id}")
    try:
        # 1. Llama a la función orquestadora para obtener el objeto Pydantic completo
        datos_completos = await procesar_factura_completa_desde_url(url)
        
        # 2. Crea una nueva sesión de DB
        async with AsyncSessionLocal() as db:
            # 3. Llama al CRUD para actualizar la factura
           db_fact_update= await crud_facturas_electronicas.update_factura_desde_scraping(
                db=db, 
                factura_id=factura_id, 
                datos_completos=datos_completos
            )
        print(f"Tarea en segundo plano completada para factura ID: {factura_id}")
        return db_fact_update
    except Exception as e:
        print(f"Error en la tarea en segundo plano para factura ID {factura_id}: {e}")
        # Aquí podrías actualizar la factura con un estado de "error"