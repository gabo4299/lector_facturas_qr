import { createContext, useState, useEffect } from 'react';
// import type { ReactNode } from 'react';
import { login as apiLogin, logout as apiLogout } from '../api/authService';
import { jwtDecode } from 'jwt-decode';
import { loginWithGoogle as apiLoginWithGoogle } from '../api/authService';
import { googleLogout } from '@react-oauth/google';
// se crea un tipo de dato User
interface User {
  sub: string; // "subject", generalmente el email
  fullName: string; // Asumimos que podrías añadir el nombre al token
  email?:string;
  is_su?:boolean;
}


// 1. Definimos la "forma" de nuestro contexto
interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  login: (email:string, password:string) => Promise<User>;
  logout: () => void;
  isLoading: boolean;
  updateUser:(newUser: User, newToken?: string) => void; 
  googleLogin: (accessToken: string) => Promise<void>;
  sessionKey: number;
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
  const [sessionKey, setSessionKey] = useState(0); //


  const updateUser = (newUser: User, newToken?: string) => {
    setUser(newUser); // Actualiza el estado del usuario en el contexto
    
    // Es una buena práctica que el backend emita un nuevo token con la info actualizada
    if (newToken) {
      localStorage.setItem('authToken', newToken);
    }
  };


  const googleLogin = async (authCode: string) => {
    // Llama al servicio que se comunica con tu backend
    const jwtToken = await apiLoginWithGoogle(authCode);
    // Guarda tu propio JWT
    localStorage.setItem('authToken', jwtToken);
    // Decodifica tu JWT para obtener los datos del usuario
    const decodedUser: User = jwtDecode(jwtToken);
    setUser(decodedUser);
    setIsAuthenticated(true);
  };

  useEffect(() => {
    const token = localStorage.getItem('authToken');
    console.log("AuthProvider CARGANDO. Token encontrado:", token);
    if (token) {
      setIsAuthenticated(true);
      const decodedUser: User = jwtDecode(token); // Decodifica el token
      console.log("Usuario decodificado del token:", decodedUser); 
      
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
    setUser(decodedUser);
    return decodedUser
  };

  const logout = () => {
    googleLogout();
    
    apiLogout(); // Llama a la función que borra el token de localStorage
    setSessionKey(prevKey => prevKey + 1)
    setUser(null);
    setIsAuthenticated(false);
    window.location.href = '/login';
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated,user, login, logout, isLoading,updateUser,googleLogin,sessionKey }}>
      {children}
    </AuthContext.Provider>
  );
};
