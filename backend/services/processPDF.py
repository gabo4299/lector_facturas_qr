
from io import BytesIO
import pdfplumber
import re
import asyncio
from datetime import datetime
class ProcesadorPDF_Rollo():
    def __init__ (self,
                  BytesEntrada:BytesIO=BytesIO(),
                  Ruta:str="",
                  Modo:int=1):
    
        self.BytesEntrada=BytesEntrada
        self.ruta=Ruta
        self.modo=Modo
        self.empresa=""#
        self.nit_emisor=""
        self.nombre_razon=""#
        self.nit_ben=""#
        self.monto_total=0
        self.monto_fiscal=0
        self.detalles=""#
        self.N_factura=""
        self.fecha=""#
        self.facturaEspecial=False
        self.controlador={}
        self.controlador["Empresa"]=(None,None)
        self.controlador["Nit_NFactura"]=(None,None)
        self.controlador["Razon_Social"]=(None,None)
        self.controlador["Detalles"]=(None,None)
        self.controlador["Montos"]=(None,None)
        self.regexNumeros = r'\d{1,3}(?:,\d{3})*\.\d+'
        self.Zonas=[]
        self.formatoFecha = '%d/%m/%Y %I:%M %p'
        self.pdf=None
    @classmethod
    async def crear(cls, BytesEntrada: BytesIO = None, Ruta: str = "", Modo: int = 1):
        """
        Crea, abre el PDF, procesa y devuelve una instancia lista de ProcesadorPDF_Rollo.
        """
        procesador = cls(BytesEntrada, Ruta, Modo)
        pdf_temp = None
        
        
        try:
            # 4. Usamos asyncio.to_thread para llamar a la función bloqueante pdfplumber.open
            print("Abriendo PDF en un hilo separado para no bloquear asyncio...")
            if Modo == 1:
                # OJO: Se pasa la función y sus argumentos por separado
                pdf_temp = await asyncio.to_thread(pdfplumber.open, procesador.BytesEntrada)
            else:
                
                pdf_temp = await asyncio.to_thread(pdfplumber.open, procesador.ruta)
                # pdf_temp=pdfplumber.open(procesador.ruta)
            
            procesador.pdf = pdf_temp
            
            # 5. Ejecutamos los otros métodos bloqueantes también en hilos separados
            await asyncio.to_thread(procesador.extraerTextoZonas)
            
            await asyncio.to_thread(procesador.procesarTexto)
            
            print("Procesador completamente inicializado y listo.")
            return procesador

        except Exception as e:
            # Capturamos el error para dar un mensaje claro
            modo_str = "Bytes" if Modo == 1 else "Ruta"
            raise RuntimeError(f"Error al leer o procesar el PDF en modo '{modo_str}': {e}")
        
        finally:
            # 6. Nos aseguramos de cerrar el PDF sin importar lo que pase
            if pdf_temp:
                print("Cerrando el archivo PDF.")
                pdf_temp.close()
    def extraerTextoZonas(self)->list:
        try:
            page = self.pdf.pages[0]
            posiciones_y_separadores = sorted([line['top'] for line in page.lines])
            limites_y = sorted(list(set([0] + posiciones_y_separadores + [page.height])))

            for i in range(len(limites_y) - 1):
                y_inicio = limites_y[i]
                y_fin = limites_y[i+1]

                # 3. "Cortar" la página para crear una zona de interés (bounding box)
                # El bounding box es (x0, top, x1, bottom)
                zona = page.crop((0, y_inicio, page.width, y_fin))

                # 4. Extraer el texto SOLO de esa zona
                texto_zona = zona.extract_text()
                self.Zonas.append(texto_zona)
                if not texto_zona:
                    self.Zonas.append("Zona vacia")
                    continue
                # print(f"--- ZONA {i+1} (de y={y_inicio:.2f} a y={y_fin:.2f}) ---")
                # print(texto_zona)
                # print("-------------------------------------------\n")
            # self.Zonas=result
            return self.Zonas
        except Exception as e:
            raise RuntimeError(f"Error al extraer zonas de la factura, {e} ")
    
    def findEmpresa(self)->list:
        try:
            if "FISCAL" in self.Zonas[0]:
        
                match = re.search(r'CRÉDITO FISCAL\s*(.*?)\s*(?:Sucursal|Casa Matriz)',  self.Zonas[0], re.DOTALL)
                print(match , "  dentro de ",self.Zonas[0])
                if match:
                    
                    self.empresa=" ".join(match.group(1).strip().split())
                    return ["Exito",True]
                else:
                    raise Exception("No se encontro data entre credito fiscal y sucursal")
            else:
                raise Exception("No se encontro La Zona 0")
        except Exception as e:
            return[f"Error al encontrar la empresa error: ,{e}",False]
            

    def findNitNFactura(self):
        try:
            if "FACTURA" in self.Zonas[1] and "AUTORIZACIÓN" in self.Zonas[1] :

                patron_nit = r"NIT\s+(\d+)"
                match_nit = re.search(patron_nit, self.Zonas[1])
                patron_factura = r"FACTURA N°\s+(\d+)"
                match_factura = re.search(patron_factura, self.Zonas[1])
                if match_nit and match_factura:
                    # Si se encontró una coincidencia, el grupo 1 contiene el número capturado
                    self.nit_emisor = match_nit.group(1)
                    self.N_factura= match_factura.group(1)
                    return ["Exito",True]
                else:
                    raise Exception("No se encontro nit o factura en el regex")
                
            else:
                raise Exception("No se encontro La Zona 1")
        except Exception as e:
            return[f"Error al encontrar nit y Nfactura error:{e} ",False]
    

    def findRazonSocial(self):
        try:
            if "NOMBRE/RAZÓN SOCIAL:" in self.Zonas[2]:
                    # Aquí el análisis es más simple porque el texto está aislado
                ciclo_nombre=False
                for linea in self.Zonas[2].split('\n'):
                    if ciclo_nombre and not "NIT/CI/CEX:" in linea:
                        self.nombre_razon=self.nombre_razon+ " "+ linea
                    if "NOMBRE/RAZÓN SOCIAL:" in linea:
                        self.nombre_razon= linea.split(':')[1].strip()
                        ciclo_nombre=True
                    
                    if "NIT/CI/CEX:" in linea:
                        self.nit_ben= linea.split(':')[1].strip()
                        ciclo_nombre=False
                    if "FECHA DE" in linea:
                        print("fecha es, ",linea)
                        self.fecha=linea.split(':')[1].strip() + ":"+linea.split(':')[2].strip()
                if self.nit_ben != "" and self.fecha != "" and self.nombre_razon != "":
                    return ["Exito",True]
                else:
                    raise Exception("No se hallaron datos en el regex ") 
            else:
                raise Exception("No se encontro La Zona 2")
        except Exception as e:
            return[f"Error al encontrar razon social, fecha y nit   error: {e} ",False]
    
    def findDetalles(self):
        try:
            if "DETALLE" in self.Zonas[3]:
                detalle_limpio = self.Zonas[3].replace("DETALLE", "").strip()
                firstTime=True
                arrayDetalles=[]
                aux=""
                arraycompra=[]
                salto_de_linea_num=False
                for linea in detalle_limpio.split('\n'):
                    if "Unidad de Medida" in linea:
                        if firstTime:
                            firstTime=False
                        else:
                            aux=arrayDetalles.pop()
                            arraycompra.append(arrayDetalles.copy())
                            arrayDetalles.clear()
                            arrayDetalles.append(aux)
                   
                    arrayDetalles.append(linea)
                    # print("linea : ",linea)
                arraycompra.append(arrayDetalles)
                # print("arra ed compre \n" ,arraycompra)
                Listas_reducidas=[]
                for sublista in arraycompra:
                    if len(sublista) >= 2:
                        numeros_encontrados = re.findall(self.regexNumeros,  sublista[-1])
                        # print("numeros encotnrados ",numeros_encontrados," en la " , sublista[-1])
                        arr_new=[0,0,0,0]
                        if len(numeros_encontrados) == 4:
                            cantidad = float(numeros_encontrados[0].replace(',', ''))
                            precio_unitario = float(numeros_encontrados[1].replace(',', ''))
                            descuento = float(numeros_encontrados[2].replace(',', ''))
                            total = float(numeros_encontrados[3].replace(',', ''))
                            arr_new=[cantidad,precio_unitario,descuento,total]
                        if len(numeros_encontrados) ==1 :
                            numeros_encontrados2=re.findall(self.regexNumeros,  sublista[-2])
                            cantidad = float(numeros_encontrados2[0].replace(',', ''))
                            precio_unitario = float(numeros_encontrados2[1].replace(',', ''))
                            descuento = float(numeros_encontrados2[2].replace(',', ''))
                            total = float(numeros_encontrados[0].replace(',', ''))
                            arr_new=[cantidad,precio_unitario,descuento,total]
                        else:
                            numeros_encontrados = re.findall(self.regexNumeros,  sublista[-2])
                            if len(numeros_encontrados) == 4:
                                cantidad = float(numeros_encontrados[0].replace(',', ''))
                                precio_unitario = float(numeros_encontrados[1].replace(',', ''))
                                descuento = float(numeros_encontrados[2].replace(',', ''))
                                total = float(numeros_encontrados[3].replace(',', ''))
                                arr_new=[cantidad,precio_unitario,descuento,total]

                        nueva_sublista = [sublista[0], arr_new]
                        Listas_reducidas.append(nueva_sublista)
                    else:
                        # Si tiene 1 o 0 elementos, simplemente la añadimos tal como está
                        Listas_reducidas.append(sublista)
                if len(Listas_reducidas)>0:
                    self.detalles=Listas_reducidas.copy()
                    return ["Exito",True]
                else:
                    raise Exception("Error al procesar los detalles")
            else:
                raise Exception("No se encontro La Zona 3 de detalles")
        except Exception as e:
            return[f"Error al encontrar Detalles error: {e}",False]
    
    def findMontos(self):
        try:
            if "TOTAL" in self.Zonas[4]:
                
                for linea in self.Zonas[4].split('\n'):
                        
                        if "TOTAL" in linea and not "SUBTOTAL" in linea: 
                            montoTotal = re.findall(self.regexNumeros,  linea)
                            montoTotal=float(montoTotal[0].replace(',', ''))
                            self.monto_total=montoTotal
                        if "IMPORTE BASE" in linea:
                            montoFiscal = re.findall(self.regexNumeros,  linea)
                            montoFiscal=float(montoFiscal[0].replace(',', ''))
                            self.monto_fiscal=montoFiscal
                if montoFiscal != montoTotal :
                    self.facturaEspecial=True
                if self.monto_fiscal != 0 and self.monto_total !=0:
                    return ["Exito",True]
                else:
                    raise Exception ("error montos fiscales y totales no se encontraron o son 0 ")
            else:
                raise Exception("No se encontro La Zona 3 de detalles")
        except Exception as e:
            return[f"Error al procesar los montos totales : {e}",False]  
    
    def procesarTexto(self):
        
        
        self.controlador["Empresa"]=self.findEmpresa()
        self.controlador["Nit_NFactura"]=self.findNitNFactura()
        self.controlador["Razon_Social"]=self.findRazonSocial()
        self.controlador["Detalles"]=self.findDetalles()
        self.controlador["Montos"]=self.findMontos()
        

    def get_datetime(self):
        return datetime.strptime(self.fecha, self.formatoFecha)
    def get_empresa(self):
        return self.empresa
    def get_nit_emisor(self):
        return self.nit_emisor
    def get_nit_beneficiario(self): 
        return self.nit_ben
    def get_monto_total(self):
        return self.monto_total
    def get_monto_fiscal(self):
        return self.monto_fiscal
    def get_detalle(self):
        return self.detalles
    def get_fecha(self):
        return self.fecha
    def get_controlador(self):
        return self.controlador
    def get_data(self):
        aux={

        }
        aux["N_Factura"]=self.N_factura
        aux["Nombre_Razon_Social"]=self.nombre_razon
        aux["Nit_Emisor"]=self.nit_emisor
        aux["Nit_Beneficiario"]=self.nit_ben
        aux["Empresa"]=self.empresa
        aux["Monto_Fiscal"]=self.monto_fiscal
        aux["Monto_Total"]=self.monto_total
        aux["Factura_especial"]=self.facturaEspecial
        aux["Fecha"]=self.fecha

        aux["Cantidad_Productos"]=len(self.detalles)
        return aux


async def main():
    # Crear un BytesIO de ejemplo
    # En un caso real, esto vendría de una subida de archivo, una petición web, etc.
    ejemplo_bytes = BytesIO() # PDF vacío para el ejemplo
    ruta=r"C:\Users\gabri\Proyectos\finanzas\lector_facturas_qr\factura_rollo4.pdf"
    print("--- Intentando crear instancia de ProcesadorPDF_Rollo ---")
    try:
        # La inicialización ahora es una única llamada 'await' a la fábrica 'crear'
        procesador_final = await ProcesadorPDF_Rollo.crear(Ruta=ruta, Modo=2)
        
        # El objeto ya está procesado y listo para usar sus resultados
        print("\n--- Objeto Creado Exitosamente ---")
        print(f"Monto total extraído: {procesador_final.monto_total}")
        print(f"controlador \n {procesador_final.get_controlador()}")
        print(f"data es \n {procesador_final.get_data()}")
        # print(f"Zonas: {procesador_final.Zonas}") # Descomentar para ver las zonas
    
    except Exception as e:
        # Como mi PDF de ejemplo está vacío, pdfplumber dará un error, que será capturado.
        print(f"\nSe produjo un error controlado: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 