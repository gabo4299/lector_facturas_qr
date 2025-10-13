// src/api/categoryService.ts
import type { Category } from '../types';
import apiClient from './apiClient';
import { isAxiosError } from 'axios';

interface CategoryPayload {
  nombre: string;
  descripcion: string;
}

/**
 * Crea una nueva categoría.
 * @param {CategoryPayload} data - Los datos de la nueva categoría.
 */
export const createCategory = async (data: CategoryPayload) => {
  try {
    // Asegúrate de que este sea tu endpoint para crear categorías
    const response = await apiClient.post('/categorias', data);
    return response.data;
  } catch (error) {
    if (isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'No se pudo crear la categoría.');
    }
    throw new Error('Ocurrió un error inesperado.');
  }
};


export const getCategories = async () => {
  try {
    // Asegúrate de que este sea tu endpoint para crear categorías
    const response = await apiClient.get('/categorias');
    return response.data;
  } catch (error) {
    if (isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'No se pudo crear la categoría.');
    }
    throw new Error('Ocurrió un error inesperado.');
  }
};


export const deleteCategory = async (idCategory:number) => {
  try {
    // Asegúrate de que este sea tu endpoint para crear categorías
    const response = await apiClient.delete(`/categorias/${idCategory}`);
    return response.data;
  } catch (error) {
    if (isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'No se pudo crear la categoría.');
    }
    throw new Error('Ocurrió un error inesperado.');
  }
};


export interface PaginatedCategoryResponse {
  items: Category[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

/**
 * Obtiene una lista paginada y filtrada de empresas.
 */
export const getCategoriesPagination = async (page: number, 
  searchTerm: string,
  limit: number,
  sortBy: string,
  sortOrder: string): Promise<PaginatedCategoryResponse> => {
  try {
    const response = await apiClient.get('/categorias/paginated', {
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
    console.error("Error al obtener empresas:", error);
    throw new Error('No se pudieron cargar las empresas.');
  }
};

interface UpdateCategoryPayload {
  nombre?: string;
  descripcion?: string;
}

/**
 * Actualiza una empresa por su ID.
 */
export const updateCategory = async (categoryId: number, data: UpdateCategoryPayload) => {
  try {
    const response = await apiClient.put(`/categorias/${categoryId}`, data);
    return response.data;
  } catch (error) {
    if (isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'No se pudo actualizar la empresa.');
    }
    throw new Error('Ocurrió un error inesperado.');
  }
};