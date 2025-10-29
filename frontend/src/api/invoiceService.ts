// src/api/projectService.ts
import type { ElectronicInvoiceAPI, ManualInvoiceAPI } from '../types';
import apiClient from './apiClient';
import { isAxiosError } from 'axios';

/**
 * Obtiene los datos de un proyecto específico por su ID.
 * @param {string} invoiceId - El ID del proyecto.
 * @returns {Promise<any>} Los datos del proyecto, incluyendo sus facturas.
 */
export const getInvoiceById = async (invoiceId: string) => {
  try {
    const response = await apiClient.get(`/facturas/${invoiceId}`);
    return response.data;
  } catch (error) {
    if (isAxiosError(error)) {
      if (error.response?.status === 404) {
        throw new Error('El proyecto no fue encontrado.');
      }
      if (error.response?.status === 403) {
        throw new Error('No tienes permiso para ver este proyecto.');
      }
    }
    throw new Error('Ocurrió un error al cargar el proyecto.');
  }
};



interface ManualInvoicePayload {
  proyecto_id: string;
  Nit_Beneficiario: string;
  monto_total: number;
  fecha: string;
  nombre_empresa?: string;
  nit_emisor: string;
   batch_id?: number,
  category_id?: number
}

/**
 * Crea una nueva factura manual.
 * @param {ManualInvoicePayload} data - Los datos de la factura.
 * @returns {Promise<any>} La factura creada.
 */
export const createManualInvoice = async (data: ManualInvoicePayload) => {
  try {
    const response = await apiClient.post('/facturas/manuales', data); // Asegúrate que este sea tu endpoint
    return response.data;
  } catch (error) {
    if (isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'No se pudo crear la factura.');
    }
    throw new Error('Ocurrió un error inesperado.');
  }
};



/**
 * Elimina una factura manual por su ID.
 * @param {number} invoiceId - El ID de la factura manual.
 */
export const deleteManualInvoice = async (invoiceId: number) => {
  try {
    // Asegúrate que este sea tu endpoint para borrar facturas manuales
    await apiClient.delete(`/facturas/manuales/${invoiceId}`);
  } catch (error) {
    if (isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'No se pudo eliminar la factura manual.');
    }
    throw new Error('Ocurrió un error inesperado.');
  }
};

/**
 * Elimina una factura electrónica por su ID.
 * @param {number} invoiceId - El ID de la factura electrónica.
 */
export const deleteElectronicInvoice = async (invoiceId: number) => {
  try {
    // Asegúrate que este sea tu endpoint para borrar facturas electrónicas
    await apiClient.delete(`/facturas/electronicas/${invoiceId}`);
  } catch (error) {
    if (isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'No se pudo eliminar la factura electrónica.');
    }
    throw new Error('Ocurrió un error inesperado.');
  }
};


interface ElectronicInvoicePayload {
  proyecto_id: string;
  url: string;
  save_pdf: boolean;
  batch_id?: number;
  categoria_id?: number;
}

export const createElectronicInvoice = async (data: ElectronicInvoicePayload) => {
  try {
    await apiClient.post('/facturas/electronicas', data); // Asumiendo este endpoint
  } catch (error) {
    if (isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'No se pudo crear la factura electrónica.');
    }
    throw new Error('Ocurrió un error inesperado.');
  }
};


// Interfaz para actualizar facturas electrónicas (ya la teníamos)
interface UpdateElectronicInvoicePayload {
  save_pdf?: boolean;
  batch_id?: number | null;
  categoria_id?: number | null;
}


/**
 * Actualiza una factura electrónica por su ID.
 * @param {number} invoiceId - El ID de la factura.
 * @param {UpdateElectronicInvoicePayload} data - Los campos a actualizar.
 */
export const updateElectronicInvoice = async (invoiceId: number, data: UpdateElectronicInvoicePayload) => {
  try {
    // Asegúrate que este sea tu endpoint PUT
    await apiClient.put(`/facturas/electronicas/${invoiceId}`, data);
  } catch (error) {
    if (isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'No se pudo actualizar la factura.');
    }
    throw new Error('Ocurrió un error inesperado.');
  }
};


interface UpdateManualInvoicePayload {
  monto_total?: number;
  fecha?: string;
  categoria_id?: number | null;
  batch_id?: number | null;
}


/**
 * Actualiza una factura MANUAL por su ID.
 */
export const updateManualInvoice = async (invoiceId: number, data: UpdateManualInvoicePayload) => {
  try {
    await apiClient.put(`/facturas/manuales/${invoiceId}`, data);
  } catch (error) {
    if (isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'No se pudo actualizar la factura manual.');
    }
    throw new Error('Ocurrió un error inesperado.');
  }
};

export interface InvoiceFiltersType {
  tipo_factura?: 'todas' | 'manual' | 'electronica';
  fecha_inicio?: string;
  fecha_fin?: string;
  monto_min?: number;
  monto_max?: number;
  categoria_id?: number;
  empresa_id?: number;
  batch_id?: number;
  complete?: boolean;
  factura_especial?: boolean;
  factura_virtual?: boolean;
  proyecto_id?: number;
}


// Interfaz para la respuesta paginada
export interface PaginatedInvoicesResponse {
  items: (ManualInvoiceAPI| ElectronicInvoiceAPI)[]; // Deberías usar un tipo más específico como (ManualInvoiceAPI | ElectronicInvoiceAPI)[]
  total: number;
  page: number;
  size: number;
  total_pages: number;
}

/**
 * Obtiene una lista paginada y filtrada de facturas para un proyecto.
 */
export const getPaginatedInvoices = async (
  projectId: string,
  page: number,
  size: number,
  sortBy: string,
  sortOrder: string,
  filters: InvoiceFiltersType
): Promise<PaginatedInvoicesResponse> => {
  try {
    const response = await apiClient.get(`/proyectos/facturas/paginated`, {
      params: {
        proyecto_id: projectId,
        page,
        size,
        sort_by: sortBy,
        sort_order: sortOrder,
        ...filters, // Añade todos los filtros al query
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error al obtener facturas paginadas:", error);
    throw new Error('No se pudieron cargar las facturas.');
  }
};



export const getPaginatedInvoicesAdmin = async (
  page: number,
  size: number,
  sortBy: string,
  sortOrder: string,
  filters: InvoiceFiltersType
): Promise<PaginatedInvoicesResponse> => {
  try {
    const response = await apiClient.get(`/proyectos/facturas/paginated/admin`, {
      params: {
        page,
        size,
        sort_by: sortBy,
        sort_order: sortOrder,
        ...filters, // Añade todos los filtros al query
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error al obtener facturas paginadas:", error);
    throw new Error('No se pudieron cargar las facturas.');
  }
};





/**
 * Descarga el pdf de la factura
 * @param {number} invoiceId - El ID de la factura.
 
 */
export const dowloadInvoicePdf = async (invoiceId: string) => {
  try {
    // Asegúrate que este sea tu endpoint get
    
     const response=await apiClient.get(`/facturas/electronicas/download/${invoiceId}`,{
      responseType: 'arraybuffer', // Especificamos que la respuesta será binaria
    });
     const contentDisposition= response.headers['content-disposition']
     let filename = 'archivo.pdf'; // Valor por defecto

    if (contentDisposition) {
      
      const match = contentDisposition.match(/filename="(.+)"/);

      
      if (match && match[1]) {
        filename = match[1]; // Si encontramos el nombre, lo asignamos
      }
    }
   

    // Convertimos el arraybuffer a un Blob
    const blob = new Blob([response.data], { type: 'application/pdf' });

    // Usamos FileSaver.js para guardar el archivo con el nombre obtenido
    const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;  // Nombre del archivo que se descargará
      a.click();

      // Limpia el objeto URL después de usarlo
      window.URL.revokeObjectURL(url);
    
    
  } catch (error) {
    if (isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'No se pudo actualizar la factura.');
    }
    throw new Error('Ocurrió un error inesperado.');
  }
};






/**
 * Descarga el pdf de la factura
 * @param {number} invoiceId - El ID de la factura.
 
 */
export const checkInvoice  = async (invoiceId: string) => {
  try {
    // Asegúrate que este sea tu endpoint get
    
     const response=await apiClient.get(`/facturas/electronicas/check/${invoiceId}`);
     return response
    
    
  } catch (error) {
    if (isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'No se pudo actualizar la factura.');
    }
    throw new Error('Ocurrió un error inesperado.');
  }
};
