// src/api/projectService.ts
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
  category_id?: number;
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