from backend.app.controllers.descargaPDF import ObtenerFactura
from backend.app.controllers.processPDF import ProcesadorPDF_Rollo
from backend.app.controllers.FacturaOb import FacturaElectronica
import asyncio
from io import BytesIO
class procesadorFacturaElectronica():
    '''
    Obtiene el pdf del siat, lo procesa y lo guarda en el Objeto Factura, para guardarlo en la db
    si es que el todos los procesos estan ok se borra la info del pdf, sino se mantiene en el objeto o db 
    para poder procesarlo o ver los errores 
    
    '''
    def __init__(self):
        self.facturaElec=None


    async def getFacturaSIAT(self,url):
        requestPDF=ObtenerFactura(get_url=url)

        status=await requestPDF.Doit()
        if status == True:
            print("Se hizo factura")
            pdfIO=requestPDF.responsePost
            print("PDF tipo",type(pdfIO))
            dataPDF=await ProcesadorPDF_Rollo.crear(BytesEntrada=BytesIO(pdfIO),Modo=1)
            if dataPDF.get_nit_emisor() == requestPDF.nitEmisor:
                print("Mismo nit emisor y nit de query")
            self.facturaElec=FacturaElectronica(url,
                               cinit=dataPDF.get_nit_beneficiario(),
                               monto_total=dataPDF.get_monto_total(),
                               fecha=dataPDF.get_datetime(),
                               empresa=dataPDF.get_empresa(),
                               detalles=dataPDF.get_detalle(),
                               n_factura=dataPDF.N_factura,
                               monto_fiscal=dataPDF.get_monto_fiscal(),
                               nit_emisor=dataPDF.get_nit_emisor(),
                               es_factura_especial=dataPDF.facturaEspecial

                               )
            return True
        return False
    def getFacturaElectroni(self):
        return self.facturaElec
    def procesarFacturaDB(self,id,url):
        pass

async def main ():
    pd=procesadorFacturaElectronica()
    factura =await pd.getFacturaSIAT(URL)
    if factura:
        pd.getFacturaElectroni().mostrar_info_completa()
        return True
    else: 
        return False
    

if __name__ == "__main__":
    URL="https://siat.impuestos.gob.bo/consulta/QR?nit=176360023&cuf=C1129B1EA5B84FD1C229FA2CC46E6004BD8B1A7643DC55CF9AD81F74&numero=44463&t=2"
    RESULTADO=asyncio.run(main()) 
    # RESULTADO.mostrar_info_completa()
    print("Elr resultado final es ")
