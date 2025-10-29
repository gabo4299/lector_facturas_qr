import os
from typing import List
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.colors import black
from reportlab.lib.utils import ImageReader # <--- IMPORTANTE
from reportlab.platypus import Frame, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import fitz  # PyMuPDF
from pyzbar import pyzbar
from PIL import Image
import io

from pydantic import BaseModel

from backend.config import BACKEND_DIR

class pdfItem(BaseModel):
    NombreEmpresa: str
    NitEmisor: str
    NFactura: int
    Fecha: str
    NitBeneficiario: str
    MontoTotal: float
    ruta: str # Ruta del PDF en el servidor desde donde se extraerá el QR


def extraer_qr_de_pdf(ruta_pdf: str) -> bytes | None:
    """
    Abre un archivo PDF, busca la primera imagen que sea un código QR válido
    y devuelve sus datos como bytes.

    :param ruta_pdf: La ruta completa al archivo PDF.
    :return: Los bytes de la imagen del QR, o None si no se encuentra ninguno.
    """
    try:
        # Abrir el documento PDF
        doc = fitz.open(ruta_pdf)
        
        for pagina_num in range(len(doc)):
            pagina = doc.load_page(pagina_num)
            
            # Obtener la lista de imágenes en la página
            lista_imagenes = pagina.get_images(full=True)
            
            if not lista_imagenes:
                continue

            # Iterar sobre cada imagen encontrada
            for img_info in lista_imagenes:
                xref = img_info[0]
                base_image = doc.extract_image(xref)
                imagen_bytes = base_image["image"]
                
                # Usar Pillow y pyzbar para verificar si es un QR
                try:
                    # Cargar los bytes de la imagen en un objeto de Pillow
                    img_pil = Image.open(io.BytesIO(imagen_bytes))
                    
                    # Intentar decodificar
                    decoded_objects = pyzbar.decode(img_pil)
                    
                    if decoded_objects:
                        # ¡Éxito! Es un QR. Devolvemos los bytes originales.
                        # print(f"✅ QR encontrado en '{ruta_pdf}'")
                        doc.close()
                        return imagen_bytes
                except Exception as e:
                    # Puede fallar si el formato de imagen no es estándar, lo ignoramos
                    # print(f"No se pudo analizar una imagen en {ruta_pdf}: {e}")
                    continue
        
        # Si terminamos el bucle sin encontrar un QR
        print(f"⚠️ No se encontró un QR en '{ruta_pdf}'")
        doc.close()
        return None

    except Exception as e:
        print(f"❌ Error al procesar el PDF '{ruta_pdf}': {e}")
        return None


class GeneradorPDF:
    def __init__(self, datos_facturas,buffer=None, archivo_salida:str=None):
        """
        Inicializa el generador.
        :param datos_facturas: Una lista de diccionarios con los datos de cada factura.
        :param archivo_salida: El nombre del archivo PDF que se creará.
        """
        self.datos_facturas = datos_facturas
        
        self.ancho_pagina, self.alto_pagina = A4

        # --- CONFIGURACIÓN DE LA CUADRÍCULA Y DISEÑO ---
        self.COLUMNAS = 2
        self.FILAS = 4
        self.MARGEN_HORIZONTAL = 1.5 * cm
        self.MARGEN_VERTICAL = 2 * cm
        # ----------------------------------------------

        self.ancho_util = self.ancho_pagina - (2 * self.MARGEN_HORIZONTAL)
        self.alto_util = self.alto_pagina - (2 * self.MARGEN_VERTICAL)
        self.ancho_celda = self.ancho_util / self.COLUMNAS
        self.alto_celda = self.alto_util / self.FILAS
        if archivo_salida:
            self.archivo_salida = archivo_salida
            self.c = canvas.Canvas(self.archivo_salida, pagesize=A4)
        else :
            self.archivo_salida=""
            self.buffer = buffer
            self.c = canvas.Canvas(self.buffer, pagesize=A4)
        
        self.estilos = getSampleStyleSheet()

    def _dibujar_celda(self, x, y, datos):
        """Dibuja el contenido de una sola celda en las coordenadas dadas."""
        # --- Dibuja un borde para la celda (opcional) ---
        self.c.rect(x, y, self.ancho_celda, self.alto_celda)

        # --- Márgenes internos de la celda ---
        padding = 0.4 * cm
        x_contenido = x + padding
        y_actual = y + self.alto_celda - padding
        ancho_contenido = self.ancho_celda - (2 * padding)

        # 1. Nombre de la Empresa (en negrita)
        estilo_titulo = self.estilos['h5']
        estilo_titulo.fontName = 'Helvetica-Bold'
        p_titulo = Paragraph(datos['NombreEmpresa'], estilo_titulo)
        p_titulo.wrapOn(self.c, ancho_contenido, self.alto_celda)
        ancho_p, alto_p = p_titulo.wrap(ancho_contenido, self.alto_celda)
        y_actual -= alto_p
        p_titulo.drawOn(self.c, x_contenido, y_actual)
        y_actual -= padding # Espacio extra

        # 2. Datos de texto alineados a la izquierda
        self.c.setFont('Helvetica', 9)
        lineas_texto = [
            f"Nit Emisor: {datos['NitEmisor']}",
            f"N° Factura: {datos['NFactura']}",
            f"Fecha: {datos['Fecha']}",
            f"Nit Beneficiario: {datos['NitBeneficiario']}",
            f"Monto: {datos['MontoTotal']}",
        ]
        
        for linea in lineas_texto:
            y_actual -= 12 # Espacio entre líneas (12 puntos)
            self.c.drawString(x_contenido, y_actual, linea)

        # 3. Código QR
        bytes_qr = datos.get('bytes_qr')
        if bytes_qr:
            qr_size = 2.5 * cm
            qr_x = x + padding
            qr_y = y + padding
            
            # Envolvemos los bytes en un objeto que ReportLab entiende
            imagen_en_memoria = ImageReader(io.BytesIO(bytes_qr))
            
            self.c.drawImage(imagen_en_memoria, qr_x, qr_y, width=qr_size, height=qr_size, preserveAspectRatio=True)
        else:
            self.c.drawString(x_contenido, y + padding, "[QR no disponible]")

    def generar_reporte(self):
        """Recorre los datos y crea el PDF página por página."""
        items_por_pagina = self.COLUMNAS * self.FILAS
        
        for i, datos_factura in enumerate(self.datos_facturas):
            # Calcula la posición en la página actual
            item_en_pagina = i % items_por_pagina
            columna = item_en_pagina % self.COLUMNAS
            fila = item_en_pagina // self.COLUMNAS

            # Calcula las coordenadas (el origen (0,0) es la esquina inferior izquierda)
            x = self.MARGEN_HORIZONTAL + (columna * self.ancho_celda)
            y = self.alto_pagina - self.MARGEN_VERTICAL - ((fila + 1) * self.alto_celda)
            
            self._dibujar_celda(x, y, datos_factura)

            # Si la página está llena y no es el último elemento, crea una nueva página
            es_ultima_celda_pagina = (i + 1) % items_por_pagina == 0
            es_ultimo_item_total = (i + 1) == len(self.datos_facturas)
            
            if es_ultima_celda_pagina and not es_ultimo_item_total:
                self.c.showPage()
        
        self.c.save()
        # print(f"✅ PDF '{self.archivo_salida}' generado exitosamente.")


def getReportePdf(data:List[pdfItem]=[],buffer=None):
    
    datos_ejemplo=[]
    for i in data:

        ruta_absoluta_en_servidor = BACKEND_DIR / i.ruta
        ruta_local=str(ruta_absoluta_en_servidor)
        data=extraer_qr_de_pdf(ruta_local)
        datos_ejemplo.append({
            'NombreEmpresa': i.NombreEmpresa,
            'NitEmisor': i.NitEmisor,
            'NFactura': str(i.NFactura),
            'Fecha': i.Fecha,
            'NitBeneficiario': i.NitBeneficiario,
            'MontoTotal': f'{(i.MontoTotal)} Bs.',
            'bytes_qr': data # Asegúrate de que este archivo exista
        })
    
    if buffer:
        generador = GeneradorPDF(datos_facturas=datos_ejemplo, buffer=buffer)
    else:
        generador = GeneradorPDF(datos_facturas=datos_ejemplo, archivo_salida="MiReporteDeFacturas.pdf")
    generador.generar_reporte()




# --- EJEMPLO DE USO ---
if __name__ == "__main__":
    # 1. Prepara una lista con tus datos.
    #    Cada diccionario representa una celda en el PDF.
    #    'ruta_qr' debe apuntar a la imagen de tu código QR.
    ruta=r"C:\Users\gabri\Proyectos\finanzas\lector_facturas_qr\backend\data\facturas\GOBIERNO AUTONOMO DEPARTAMENTAL DE COCHABAMBA_2025-03-14_factN_44463.pdf"
    datos_ejemplo = []
    for i in range(1, 11): # Generamos 10 facturas de ejemplo
        datos_ejemplo.append(pdfItem(
            NombreEmpresa= 'MI EMPRESA S.R.L.',
            NitEmisor= '123456789',
            NFactura= i,
            Fecha= '19/10/2025',
            NitBeneficiario= '987654321',
            MontoTotal= i*150,
            ruta= ruta # Asegúrate de que este archivo exista
        ))

    # 2. Crea una instancia de la clase y genera el reporte.
    getReportePdf(datos_ejemplo)