// src/api/authService.ts
import apiClient from './apiClient';
import { isAxiosError } from 'axios'; 
// 🧠 ¡Importante! El endpoint /token de FastAPI para JWT espera los datos
// como 'form data' (application/x-www-form-urlencoded), no como JSON.
// Por eso usamos URLSearchParams para formatear los datos correctamente.

/**
 * Función para iniciar sesión.
 * Envía email y password al backend y espera un token de acceso.
 * @param {string} email - El email del usuario.
 * @param {string} password - La contraseña del usuario.
 * @returns {Promise<string>} El token de acceso.
 */
export const login = async (email:string, password:string) => {
  // Creamos el cuerpo de la petición en formato 'form data'
  const formData = new URLSearchParams();
  formData.append('username', email); // FastAPI espera 'username'
  formData.append('password', password);

  try {
    const response = await apiClient.post('/auth/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    // Si la petición es exitosa, el backend nos devuelve el token
    return response.data.access_token;
  } catch (error) {
    // Si hay un error (ej: credenciales incorrectas), lo relanzamos
    // para que el componente que llama a la función pueda manejarlo.
    if (isAxiosError(error)) {
      // Si lo es, sabemos que podemos acceder de forma segura a error.response
      const detail = error.response?.data?.detail;
      // 3. Lanzamos un nuevo error con un mensaje claro para el componente
      throw new Error(detail || 'Credenciales incorrectas o error del servidor.');
    }
    // Si no es un error de Axios, lanzamos un error genérico
    throw new Error('Ocurrió un error inesperado.');
    // --- FIN DE LA CORRECCIÓN ---
  }
};

export const logout = () => {
  localStorage.removeItem('authToken');
};

// 👇 AÑADE ESTA NUEVA FUNCIÓN
/**
 *  Registra un nuevo usuario en la base de datos.
 * @param {string} fullName - El nombre completo del usuario.
 * @param {string} email - El email del usuario.
 * @param {string} password - La contraseña del usuario.
 * @returns {Promise<any>} Los datos del usuario creado.
 */
export const register = async (fullName:string, email:string, password:string) => {
  try {
    // A diferencia del login, este endpoint espera un JSON normal.
    const response = await apiClient.post('/usuarios/', {
      name: fullName, // Asegúrate de que los nombres coincidan con tu schema Pydantic
      email: email,
      password: password,
    });
    return response.data;

  } catch (error) {
    if (isAxiosError(error)) {
      const detail = error.response?.data?.detail;
      // Lanza un error con un mensaje claro para el componente
      throw new Error(detail || 'No se pudo completar el registro.');
    }
    throw new Error('Ocurrió un error inesperado.');
  }
};
