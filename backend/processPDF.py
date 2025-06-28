
from io import BytesIO
import pdfplumber
import re
import asyncio
class ProcesadorPDF_Rollo():
    async def __init__ (self,
                  BytesEntrada:BytesIO=BytesIO(),
                  Ruta:str="",
                  Modo:int=1):
    
        self.BytesEntrada=BytesEntrada
        self.ruta=Ruta

        self.empresa=""#
        self.nit_emisor=""
        self.nombre_razon=""#
        self.nit_ben=""#
        self.monto_total=""
        self.monto_fiscal=""
        self.detalles=""#
        self.fecha=""#
        self.facturaEspecial=False

        self.regexNumeros = r'\d{1,3}(?:,\d{3})*\.\d+'
        self.Zonas=[]

        self.pdf=None
        try:
            if Modo ==1 :
                self.pdf = await pdfplumber.open(BytesIO(BytesEntrada))
            else:
                self.pdf = await pdfplumber.open(Ruta)
            self.Zonas=await self.extraerTextoZonas()
            await self.procesarTexto()
        except Exception:
            self.error_pdf=True
            
        finally:
            if self.pdf:
                self.pdf.close()
            if self.error_pdf:
                raise RuntimeError(f"error al leer el pdf en modo {"Bytes" if Modo ==1 else "Ruta "}")
    async def extraerTextoZonas(self)->list:
        result=[]
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
            result.append(texto_zona)
            if not texto_zona:
                result.append("Zona vacia")
                continue
        return result
    async def procesarTexto(self):
        if "FISCAL" in self.Zonas[0]:
        # Usamos regex para buscar entre "CRÉDITO FISCAL" y "Sucursal"
            match = re.search(r'CRÉDITO FISCAL\s*(.*?)\s*Sucursal',  self.Zonas[0], re.DOTALL)
        if match:
            self.empresa=" ".join(match.group(1).strip().split())
        
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
                    self.fecha=linea.split(':')[1].strip()

        if "DETALLE" in self.Zonas[5]:
                        # Podrías hacer un procesamiento más detallado aquí
                        # Quitamos la palabra "DETALLE" y limpiamos
                        detalle_limpio = self.Zonas[5].replace("DETALLE", "").strip()
                        # self.detalles = " ".join(detalle_limpio.split('\n'))
                        firstTime=True
                        arrayDetalles=[]
                        aux=""
                        arraycompra=[]
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
                            print("linea : ",linea)
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
                            
                        self.detalles=Listas_reducidas.copy()
                        
        
        if "TOTAL" in self.Zonas[6]:
            for linea in self.Zonas[6].split('\n'):
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
