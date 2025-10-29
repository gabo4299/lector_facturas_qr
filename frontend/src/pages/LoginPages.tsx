// src/pages/LoginPage.tsx
// src/pages/LoginPage.tsx

import { useState, useEffect } from 'react';
// import { login } from '../api/authService';
import type { FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth'; // 👈 1. Importa useAuth
import { register } from '../api/authService'; 
import { GoogleLoginButton } from '../components/ui/GoogleLoginButton';


const LoginPage = () => {

const [isLoginMode, setIsLoginMode] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState(''); 
  const [error, setError] = useState<string | null>(null);
  

  const { login,googleLogin, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [success, setSuccess] = useState<string | null>(null); // Para mensajes de éxito
  // Redirige si el usuario ya está autenticado


  
  
  const handleGoogleSuccess = async (authCode: string) => {
    try {
      await googleLogin(authCode);
      // navigate('/'); // Redirige al dashboard
    } catch (err) {
      console.log("error ",err)
      setError('No se pudo iniciar sesión con Google.');
    }
  };
  const handleGoogleError = () => {
    setError('Hubo un problema con la autenticación de Google.');
  };

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/', { replace: true });
    }
  }, [isAuthenticated, navigate]);

   const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setSuccess(null);
    try {
      if (isLoginMode) {
        // --- LÓGICA DE LOGIN ---
        await login(email, password);
        // navigate('/');
      } else {
        // --- LÓGICA DE REGISTRO ---
        await register(fullName, email, password);
        setSuccess('¡Usuario registrado con éxito! Ahora puedes iniciar sesión.');
        setIsLoginMode(true); // Cambia al modo login después del registro
        setFullName('');
        setEmail('');
        setPassword('');
      }
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Ocurrió un error inesperado.');
      }
    }
  };

  return (
     <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md">
        
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">
            {isLoginMode ? 'Iniciar Sesión' : 'Crear Cuenta'}
          </h1>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* 3. Campo de Nombre, solo visible en modo Registro */}
          {!isLoginMode && (
            <div>
              <label htmlFor="fullName" className="block text-sm font-medium text-gray-700">Nombre Completo</label>
              <input
                id="fullName" type="text" required value={fullName} onChange={(e) => setFullName(e.target.value)}
                className="w-full px-3 py-2 mt-1 border rounded-md shadow-sm bg-gray-50 border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          )}

          {/* Campos de Email y Contraseña (siempre visibles) */}
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">Correo Electrónico</label>
            <input id="email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} className="w-full px-3 py-2 mt-1 border rounded-md shadow-sm bg-gray-50 border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700">Contraseña</label>
            <input id="password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} className="w-full px-3 py-2 mt-1 border rounded-md shadow-sm bg-gray-50 border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>

          {/* Mensajes de Éxito o Error */}
          {error && <div className="p-3 text-sm text-center text-red-800 bg-red-100 border border-red-300 rounded-md">{error}</div>}
          {success && <div className="p-3 text-sm text-center text-green-800 bg-green-100 border border-green-300 rounded-md">{success}</div>}

          <div>
            <button
              type="submit"
              className="w-full px-4 py-2 font-bold text-white transition-colors bg-blue-600 rounded-md hover:bg-blue-700"
            >
              {isLoginMode ? 'Ingresar' : 'Registrarse'}
            </button>
          </div>

          <div className="my-6 flex items-center">
          <div className="flex-grow border-t border-gray-300"></div>
          <span className="mx-4 flex-shrink text-sm text-gray-500">O</span>
          <div className="flex-grow border-t border-gray-300"></div>
        </div>
        
        {/* 👇 Botón de Google 👇 */}
        <GoogleLoginButton
          onSuccess={handleGoogleSuccess}
          onError={handleGoogleError}
        />
        </form>

        {/* 4. Botón para cambiar entre modos */}
        <div className="text-sm text-center">
          <button 
            onClick={() => setIsLoginMode(!isLoginMode)}
            className="font-medium text-blue-600 hover:text-blue-500"
          >
            {isLoginMode ? '¿No tienes cuenta? Regístrate' : '¿Ya tienes cuenta? Inicia sesión'}
          </button>
        </div>
      </div>
    </div>
  );
};
export default LoginPage;