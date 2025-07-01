from datetime import datetime

class Factura:
    """
    Clase base que representa una factura genérica.
    """
    def __init__(self, cinit: str, monto_total: float, fecha: datetime, empresa: str):
        """
        Constructor para los atributos comunes de todas las facturas.
        """
        self.cinit = cinit
        self.monto_total = monto_total
        self.fecha = fecha
        self.empresa = empresa

    def mostrar_info_base(self):
        """
        Muestra la información básica y común de la factura.
        Este método será reutilizado por las clases hijas.
        """
        print(f"  Empresa: {self.empresa}")
        print(f"  Fecha: {self.fecha.strftime('%d/%m/%Y')}")
        print(f"  CI/NIT Cliente: {self.cinit}")
        print(f"  Monto Total: {self.monto_total:.2f} Bs.")

    def __repr__(self):
        """
        Representación del objeto para desarrolladores.
        """
        return f"Factura(empresa='{self.empresa}', monto={self.monto_total})"


# --- 2. CLASES DERIVADAS (HIJAS) ---

# --- Factura Manual ---
class FacturaManual(Factura):
    """
    Representa una factura manual.
    Hereda de Factura y no añade nuevos atributos, pero sí especializa su tipo.
    """
    def __init__(self, cinit: str, monto_total: float, fecha: datetime, empresa: str):
        # Llama al constructor de la clase padre (Factura) para inicializar
        # los atributos comunes.
        super().__init__(cinit, monto_total, fecha, empresa)
        self.tipo_factura="Manual"

    def mostrar_info_completa(self):
        """
        Muestra la información completa de la factura manual.
        """
        print("---[ Factura Manual ]---")
        # Reutilizamos el método de la clase padre para mostrar la info base.
        self.mostrar_info_base()
        print("-" * 26)


# --- Factura Electrónica ---
class FacturaElectronica(Factura):
    """
    Representa una factura electrónica.
    Hereda de Factura y añade atributos específicos.
    """
    def __init__(self,url:str, 
                 cinit: str="", monto_total: float=0.0, fecha: datetime=datetime.now(), 
                 empresa: str="simon",
                 detalles:list =[], 
                 n_factura: int=0, 
                 monto_fiscal: float=0.0,
                 nit_emisor: str="", 
                 es_factura_especial: bool=False):

        # 1. Llama al constructor de la clase padre (Factura) para manejar
        #    los atributos comunes.
        super().__init__(cinit, monto_total, fecha, empresa)

        # 2. Inicializa los atributos propios de la factura electrónica.
        self.tipo_factura="Electronica"
        self.detalles = detalles
        self.n_factura = n_factura
        self.monto_fiscal = monto_fiscal
        self.nit_emisor = nit_emisor
        self.es_factura_especial = es_factura_especial

    def mostrar_info_completa(self):
        """
        Muestra la información completa, incluyendo los detalles específicos
        de la factura electrónica.
        """
        print("---[ Factura Electrónica ]---")
        # Reutilizamos el método de la clase padre
        self.mostrar_info_base()
        
        # Mostramos los detalles adicionales
        print("  --- Detalles Electrónicos ---")
        print(f"  Nro. Factura: {self.n_factura}")
        print(f"  NIT Emisor: {self.nit_emisor}")
        print(f"  Monto Fiscal: {self.monto_fiscal:.2f} Bs.")
        print(f"  Detalle: {self.detalles}")
        print(f"  Es Especial: {'Sí' if self.es_factura_especial else 'No'}")
        print("-" * 30)
