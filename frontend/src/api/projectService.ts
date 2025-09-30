// src/api/projectService.ts
import apiClient from './apiClient';
import { isAxiosError } from 'axios';


/**
 * Obtiene los datos de un proyecto específico por su ID.
 * @param {string} projectId - El ID del proyecto.
 * @returns {Promise<any>} Los datos del proyecto, incluyendo sus facturas.
 */
export const getProjectById = async (projectId: string) => {
  try {
    const response = await apiClient.get(`/proyectos/${projectId}`);
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


/**
 * Obtiene las facturas de un proyecto específico por su ID.
 * @param {string} projectId - El ID del proyecto.
 * @returns {Promise<any>} Los datos del proyecto, incluyendo sus facturas.
 */
export const getInvoicesByProjectId = async (projectId: string) => {
  try {
    const response = await apiClient.get(`/proyectos/${projectId}/facturas`);
    return response.data;
  } catch (error) {
    if (isAxiosError(error)) {
      if (error.response?.status === 404) {
        throw new Error('Facturas no encontradas.');
      }
      if (error.response?.status === 403) {
        throw new Error('No tienes permiso para ver facturas de este proyecto.');
      }
    }
    throw new Error('Ocurrió un error al cargar las facturas del proyecto.');
  }
};

/**
 * Crea un nuevo lote (batch) para un proyecto específico.
 * @param {string} projectId - El ID del proyecto al que pertenece el lote.
 * @param {string} nombre - El nombre del nuevo lote.
 * @param {string} descripcion - La descripción del nuevo lote.
 * @returns {Promise<any>} Los datos del lote creado.
 */


export const getBatchesForProject = async (projectId: string) => {
  try {
    const response = await apiClient.get(`/proyectos/${projectId}/batch`);
    return response.data;
  } catch (error) {
    console.error("Error al obtener lotes:", error);
    return [];
  }
};

export const getCategoriesForProject = async () => {
  try {

    const response = await apiClient.get(`/categorias`); // Asumiendo este endpoint
    return response.data;
  } catch (error) {
    console.error("Error al obtener categorías:", error);
    return [];
  }
};
export const createBatch = async (proyecto_id: string, nombre: string, descripcion: string) => {
  try {
    const response = await apiClient.post(`/batch`, {
      proyecto_id,
     nombre,
      descripcion,
    });
    return response.data;
  } catch (error) {
    if (isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'No se pudo crear el lote.');
    }
    throw new Error('Ocurrió un error inesperado al crear el lote.');
  }
};