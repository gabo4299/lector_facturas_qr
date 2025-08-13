from .descargaPDF import ObtenerFactura
from .processPDF import ProcesadorPDF_Rollo
# from FacturaOb import FacturaElectronica
from backend.schemas import DetalleItem,FacturaElectronicaCreate

from backend.crud import crud_facturas_electronicas
from backend.db.database import AsyncSessionLocal
import asyncio
from io import BytesIO
class procesadorFacturaElectronica():
    '''
    Obtiene el pdf del siat, lo procesa y lo guarda en el Objeto Factura, para guardarlo en la db
    si es que el todos los procesos estan ok se borra la info del pdf, sino se mantiene en el objeto o db 
    para poder procesarlo o ver los errores 
    
    '''
    def __init__(self,url=None,facturaElectronica:FacturaElectronicaCreate=None):
        if not url and not facturaElectronica :
            raise  Exception("error al crear procesador de factura")
     
            
        if facturaElectronica:
            self.facturaElec=facturaElectronica
            self.url=facturaElectronica.url
        else:
            self.facturaElec=FacturaElectronicaCreate(url=url)
            self.url=url
        self.requestPDF=None


    async def getCompleteFacturaSIAT(self,savePDF=False):
 
        self.requestPDF=ObtenerFactura(get_url=self.url)
        
        status=await self.requestPDF.Doit()
        self.facturaElec.save_pdf=savePDF
        if self.requestPDF.statusGet:
            self.facturaElec.monto_total=self.requestPDF.monto
            self.facturaElec.empresa=self.requestPDF.comercio
            self.facturaElec.nit_emisor=self.requestPDF.nitEmisor
            self.facturaElec.n_factura=int(self.requestPDF.Nfactura)
        
        if status == True:
            print("Se hizo factura")
            pdf=self.requestPDF.responsePost
            if savePDF:
                self.facturaElec.pdfIO=pdf
            else:
                self.facturaElec.pdfIO=None
            print("PDF tipo",type(pdf))
            dataPDF=await ProcesadorPDF_Rollo.crear(BytesEntrada=BytesIO(pdf),Modo=1)

            estadopdf=dataPDF.get_controlador()
            self.facturaElec.msg_pdf_request=estadopdf
            self.facturaElec.status_PDFrequest=all(valor[1] for valor in estadopdf.values())

            self.facturaElec.Nit_Beneficiario=dataPDF.get_nit_beneficiario()
            self.facturaElec.fecha=dataPDF.get_datetime()
            self.facturaElec.detalles=dataPDF.get_detalle()
            self.facturaElec.monto_fiscal=dataPDF.get_monto_fiscal()
            self.facturaElec.factura_especial=dataPDF.facturaEspecial

        
        self.facturaElec.status_Getrequest=self.requestPDF.statusGet
        self.facturaElec.status_Postrequest=self.requestPDF.statusPost
        self.facturaElec.msg_get_request=self.requestPDF.msgGet
        self.facturaElec.msg_post_request=self.requestPDF.msgPost
        
        
        
        return self.facturaElec
    
    async def tarea_de_scraping_y_actualizacion(self):
        print(f"Tarea en segundo plano iniciada para factura ID: {factura_id}")
        try:
            # 1. Ejecuta el scraping
            datos_completos = await self.getCompleteFacturaSIAT(url)
            
            # 2. Crea una nueva sesión de DB para esta tarea
            async with AsyncSessionLocal() as db:
                # 3. Llama al CRUD para actualizar la factura
                await crud_facturas_electronicas.update_factura_desde_scraping(
                    db=db, 
                    factura_id=factura_id, 
                    datos_completos=datos_completos
                )
            print(f"Tarea en segundo plano completada para factura ID: {factura_id}")
        except Exception as e:
            print(f"Error en la tarea en segundo plano para factura ID {factura_id}: {e}")


    def getFacturaElectroni(self):
        return self.facturaElec


async def main ():
    pd=procesadorFacturaElectronica(URL)
    factura =await pd.getCompleteFacturaSIAT()
    if factura:
        print(factura.model_dump(mode='json'))
        return True
    else: 
        return False
    

if __name__ == "__main__":
    URL="https://siat.impuestos.gob.bo/consulta/QR?nit=176360023&cuf=C1129B1EA5B84FD1C229FA2CC46E6004BD8B1A7643DC55CF9AD81F74&numero=44463&t=2"
    RESULTADO=asyncio.run(main()) 
    # RESULTADO.mostrar_info_completa()
    print("Elr resultado final es ")
