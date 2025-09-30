// src/api/apiClient.ts
import axios from 'axios';

// Creamos una instancia de Axios con configuración centralizada
const apiClient = axios.create({
  // La URL base de nuestra API de FastAPI.
  // Es una buena práctica guardarla en una variable de entorno.
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// 🧠 Aquí es donde más adelante añadiremos la magia del JWT.
// Usaremos un "interceptor" para añadir el token de autenticación
// a cada petición que lo necesite, de forma automática.
apiClient.interceptors.request.use(
  (config) => {
    // 1. Busca el token en localStorage
    const token = localStorage.getItem('authToken');

    // 2. Si el token existe, lo añade a las cabeceras de la petición
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // 3. Devuelve la configuración modificada para que la petición continúe
    return config;
  },
  (error) => {
    // Maneja errores en la configuración de la petición
    return Promise.reject(error);
  }
);
// 👆 --- FIN DE LA MODIFICACIÓN ---



export default apiClient;