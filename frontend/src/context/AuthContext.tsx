import { createContext, useState, useEffect } from 'react';
// import type { ReactNode } from 'react';
import { login as apiLogin, logout as apiLogout } from '../api/authService';
import { jwtDecode } from 'jwt-decode';
// se crea un tipo de dato User
interface User {
  sub: string; // "subject", generalmente el email
  fullName: string; // Asumimos que podrías añadir el nombre al token
}

// 1. Definimos la "forma" de nuestro contexto
interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  login: (email:string, password:string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

// 2. Creamos el contexto con un valor inicial por defecto
// eslint-disable-next-line react-refresh/only-export-components
export const AuthContext = createContext<AuthContextType | undefined>(undefined);


// 3. Creamos el componente "Proveedor" que envolverá nuestra app
export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  // ... (toda la lógica del AuthProvider se queda igual) ...
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token) {
      setIsAuthenticated(true);
      const decodedUser: User = jwtDecode(token); // Decodifica el token
      
      setUser(decodedUser); // Guarda los datos del usuario
    }
    setIsLoading(false);
  }, []);

  const login = async (email:string, password:string) => {
    const token = await apiLogin(email, password);
    localStorage.setItem('authToken', token);
    const decodedUser: User = jwtDecode(token); 
    console.log(decodedUser.fullName)
    setIsAuthenticated(true);
  };

  const logout = () => {
    apiLogout(); // Llama a la función que borra el token de localStorage
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated,user, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};
