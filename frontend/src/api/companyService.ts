// src/api/companyService.ts
import apiClient from './apiClient';
import type { Company } from '../types';
import { isAxiosError } from 'axios';
import { logout } from './authService';



/**
 * Obtiene una lista de todas las empresas.
 * @returns {Promise<Company[]>}
 */
export const getCompanies = async (): Promise<Company[]> => {
  try {
    const response = await apiClient.get('/empresas/'); // Asegúrate que este sea tu endpoint
    return response.data;
  } catch (error) {
    console.error("Error al obtener empresas:", error);
    // Devuelve un array vacío en caso de error para no romper el autocompletado
    return [];
  }
};





// Interfaz para la respuesta paginada de la API
export interface PaginatedCompaniesResponse {
  items: Company[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

/**
 * Obtiene una lista paginada y filtrada de empresas.
 */
export const getCompaniesPagination = async (page: number, 
  searchTerm: string,
  limit: number,
  sortBy: string,
  sortOrder: string): Promise<PaginatedCompaniesResponse> => {
  try {
    const response = await apiClient.get('/empresas/paginated', {
      params: {
        page: page,
        size: limit, // 10 empresas por página
        search: searchTerm,
        sort_by: sortBy,
        sort_order: sortOrder,
      }
    });
    return response.data;
  } catch (error) {
    


    if (isAxiosError(error)) {
          if (error.response?.status === 404) {
            throw new Error('Empresa no  encontrada.');
          }
          if (error.response?.status === 403 || error.response?.status === 401) {
            logout()
            window.location.href = '/login';
            throw new Error('No tienes permiso para ver empresas.');
    
          }
             
        }
        throw new Error('No se pudieron cargar las empresas');
      }
  }
;

/**
 * Elimina una empresa por su ID.
 */
export const deleteCompany = async (companyId: number) => {
  try {
    await apiClient.delete(`/empresas/${companyId}`);
  } catch (error) {
    console.error("Error al eliminar empresas:", error);
    throw new Error('No se pudn eliminar la empresas.');
  }
};


interface UpdateCompanyPayload {
  nombre?: string;
  rubro?: string;
}

/**
 * Actualiza una empresa por su ID.
 */
export const updateCompany = async (companyId: number, data: UpdateCompanyPayload) => {
  try {
    const response = await apiClient.put(`/empresas/${companyId}`, data);
    return response.data;
  } catch (error) {
    if (isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'No se pudo actualizar la empresa.');
    }
    throw new Error('Ocurrió un error inesperado.');
  }
};