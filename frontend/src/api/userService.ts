// src/api/projectService.ts
import { isAxiosError } from 'axios';
import type { UserProject } from '../types';
import apiClient from './apiClient';
// import { isAxiosError } from 'axios';


export interface PaginatedUserResponse {
  items: UserProject[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

/**
 * Obtiene una lista paginada y filtrada de empresas.
 */
export const getUsersPagination = async (
 page: number, 
 limit: number,
  searchTerm: string,
  sortBy: string,
  sortOrder: string): Promise<PaginatedUserResponse> => {
  try {
    const response = await apiClient.get('/usuarios/paginated', {
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
      throw new Error(error.response?.data?.detail || 'No se pudo encontrar usuarios.');
    }
    throw new Error('Ocurrió un error inesperado.');
  }
};


interface UpdateUsuariosPayload {
  name?: string;
}

/**
 * Actualiza una empresa por su ID.
 */
export const updateUser = async (userId: number, data: UpdateUsuariosPayload) => {
  try {
    const response = await apiClient.put(`/usuarios/${userId}`, data);
    return response.data;
  } catch (error) {
    if (isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'No se pudo actualizar el usuario.');
    }
    throw new Error('Ocurrió un error inesperado.');
  }
};


export const deleteUser = async (idUser:number) => {
  try {
    // Asegúrate de que este sea tu endpoint para crear categorías
    const response = await apiClient.delete(`/usuarios/${idUser}`);
    return response.data;
  } catch (error) {
    if (isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'No se pudo eliminar el usuario.');
    }
    throw new Error('Ocurrió un error inesperado.');
  }
};
