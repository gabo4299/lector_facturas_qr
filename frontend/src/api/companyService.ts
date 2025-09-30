// src/api/companyService.ts
import apiClient from './apiClient';

// import { isAxiosError } from 'axios';

export interface Company {
  id: number;
  nombre: string;
  nit: string;
}

/**
 * Obtiene una lista de todas las empresas.
 * @returns {Promise<Company[]>}
 */
export const getCompanies = async (): Promise<Company[]> => {
  try {
    const response = await apiClient.get('/empresas'); // Asegúrate que este sea tu endpoint
    return response.data;
  } catch (error) {
    console.error("Error al obtener empresas:", error);
    // Devuelve un array vacío en caso de error para no romper el autocompletado
    return [];
  }
};