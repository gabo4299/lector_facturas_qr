// src/api/projectService.ts
import apiClient from './apiClient';
import { isAxiosError } from 'axios';
import {logout} from './authService'
// import { useAuth } from '../hooks/useAuth'; // Importamos nuestro hook

import type {addMemberToProject} from '../types'


 
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
      if (error.response?.status === 403 || error.response?.status === 401) {
        logout()
        window.location.href = '/login';
        
        throw new Error('No tienes permiso para ver este proyecto.');

      }
    }
    throw new Error('Ocurrió un error al cargar el proyecto.');
  }
};


/**
 * Obtiene todos los proyectos asociados al usuario actual.
 * @returns {Promise<any[]>} Una lista de proyectos.
 */
export const getProjectsByUser = async () => {
  try {
    const response = await apiClient.get('/proyectos'); // Asegúrate que este sea tu endpoint
    return response.data;
  } catch (error) {
   if (isAxiosError(error)) {
      if (error.response?.status === 404) {
        throw new Error('El proyecto no fue encontrado.');
      }
      if (error.response?.status === 403 || error.response?.status === 401) {
        logout()
        window.location.href = '/login';
        throw new Error('No tienes permiso para ver este proyecto.');

      }
    }
    throw new Error('Ocurrió un error al cargar el proyecto.');
  }
};


export const getProjectsall = async () => {
  try {
    const response = await apiClient.get('/proyectos/all'); // Asegúrate que este sea tu endpoint
    return response.data;
  } catch (error) {
   if (isAxiosError(error)) {
      if (error.response?.status === 404) {
        throw new Error('El proyecto no fue encontrado.');
      }
      if (error.response?.status === 403 || error.response?.status === 401) {
        logout()
        window.location.href = '/login';
        throw new Error('No tienes permiso para ver este proyecto.');

      }
    }
    throw new Error('Ocurrió un error al cargar el proyecto.');
  }
};

/**
 * Elimina un proyecto por su ID.
 * @param {string} projectId - El ID del proyecto a eliminar.
 */
export const deleteProject = async (projectId: string) => {
  try {
    await apiClient.delete(`/proyectos/${projectId}`); // Asegúrate que este sea tu endpoint
  } catch (error) {
    if (isAxiosError(error)) {
      if (error.response?.status === 404) {
        throw new Error('El proyecto no fue encontrado.');
      }
      if (error.response?.status === 403 || error.response?.status === 401) {
        logout()
        window.location.href = '/login';
        throw new Error('No tienes permiso para ver este proyecto.');

      }
    }
    throw new Error('Ocurrió un error al cargar el proyecto.');
  }
};

/**
 * Agrega un usuario al proyecto.
 * @param {string} projectId - El ID del proyecto a eliminar.
 * @param {addMemberToProject} data - la info de del miebmro a añadir
 * 
 */
export const addUserToProject = async (projectId: string,data: addMemberToProject) => {
  try {
    await apiClient.post(`/proyectos/${projectId}/miembros`,data); // Asegúrate que este sea tu endpoint
  } catch (error) {
    if (isAxiosError(error)) {
      if (error.response?.status === 404) {
        throw new Error('El proyecto no fue encontrado.');
      }
      if (error.response?.status === 403 || error.response?.status === 401) {
        throw new Error('No tienes permiso para agregar a este proyecto.');

      }
      if (error.response?.status === 400) {
        
        throw new Error(error?.response?.data?.detail||"error en parametros");

      }      if (error.response?.status === 409) {
        throw new Error('Usuario ya pertenece a proyecto');

      }
    }
    throw new Error('Ocurrió un error al intentar agregar.');
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

export const getResumeProject = async (projectId: string) => {
  try {

    const response = await apiClient.get(`/proyectos/${projectId}/fullresume`); // Asumiendo este endpoint
    return response.data;
  } catch (error) {
    console.error("Error al obtener resumen de proyecto:", error);
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


interface ProjectPayload {
  nombre: string;
  fecha_inicio: string;
  fecha_fin: string;
  nit_beneficiario: string;
}

/**
 * Crea un nuevo proyecto.
 * @param {ProjectPayload} data - Los datos del nuevo proyecto.
 */
export const createProject = async (data: ProjectPayload) => {
  try {
    const response = await apiClient.post('/proyectos', data); // Asegúrate que este sea tu endpoint
    return response.data;
  } catch (error) {
    if (isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'No se pudo crear el proyecto.');
    }
    throw new Error('Ocurrió un error inesperado.');
  }
};



interface UpdateProjectPayload {
  nombre?: string;
  fecha_inicio?: string;
  fecha_fin?: string;
}

/**
 * Actualiza los detalles de un proyecto (nombre, fechas).
 */
export const updateProject = async (projectId: string, data: UpdateProjectPayload) => {
  try {
    const response = await apiClient.put(`/proyectos/${projectId}`, data);
    return response.data;
  } catch (error) {
    if (isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'No se pudo actualizar el proyecto.');
    }
    throw new Error('Ocurrió un error inesperado.');
  }
};

/**
 * Actualiza el rol de un usuario en un proyecto.
 */
export const updateCollaboratorRole = async (projectId: string, userId: number, newRole: string) => {
  try {
    // Asegúrate de que este endpoint coincida con tu API
    const response = await apiClient.put(`/proyectos/${projectId}/miembros/${userId}`, { rol: newRole });
    return response.data;
  } catch (error) {
    if (isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'No se pudo cambiar el rol.');
    }
    throw new Error('Ocurrió un error inesperado.');
  }
};



/**
 * Elimina un colaborador de un proyecto.
 * @param {string} projectId - El ID del proyecto.
 * @param {number} userId - El ID del usuario a eliminar.
 */
export const deleteCollaborator = async (projectId: string, userId: number) => {
  try {
    // Asegúrate de que este endpoint coincida con tu API
    await apiClient.delete(`/proyectos/${projectId}/miembros/${userId}`);
  } catch (error) {
    if (isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'No se pudo eliminar al colaborador.');
    }
    throw new Error('Ocurrió un error inesperado.');
  }
};


export const getPaginatedProjects = async (page: number,
   limit: number, 
   searchTerm: string,
    sortBy: string,
     sortOrder: string) => {
  

  try {
    const response = await apiClient.get('/proyectos/paginated', {
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



export const getReport = async (projectId: string) => {
  try {
    const response = await apiClient.get(`/proyectos/${projectId}/reporte`,{responseType: 'arraybuffer'});
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
      if (error.response?.status === 404) {
        throw new Error('El proyecto no fue encontrado.');
      }
      if (error.response?.status === 403 || error.response?.status === 401) {
        logout()
        window.location.href = '/login';
        throw new Error('No tienes permiso para ver este proyecto.');

      }
          if (error.response?.status === 400) {
        throw new Error('No hay facturas virutales.');
      }
    }
    throw new Error('Ocurrió un error al procesar el proyecto.');
  }
};