// src/components/layout/Navbar.tsx
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth'; // Importamos nuestro hook
import { useEffect, useRef, useState } from 'react';

export const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const handleLogout = () => {
    logout(); // Llama a la función del contexto para limpiar el estado y el token
    navigate('/login'); // Redirige al usuario a la página de login
  };

// Cierra el dropdown si se hace clic fuera de él
    useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <header className="bg-white shadow-md">
      <nav className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* GRUPO IZQUIERDO: Perfil de Usuario y Logo */}
       

          {/* GRUPO DERECHO: Enlaces de Navegación */}
          <div className="hidden md:block">
            
            <div className="flex items-center space-x-4">
              {/* Logo o Nombre de la App */}
            <Link to="/" className="text-xl font-bold text-gray-800">
              FacturaApp
            </Link>
              <Link
                to="/"
                className="px-3 py-2 text-sm font-medium text-gray-500 rounded-md hover:text-gray-900 hover:bg-gray-100"
              >
                Dashboard
              </Link>
              <Link
                to="/projects" // Ruta para Proyectos
                className="px-3 py-2 text-sm font-medium text-gray-500 rounded-md hover:text-gray-900 hover:bg-gray-100"
              >
                Proyectos
              </Link>
              <Link
                to="/companies" // Ruta para Empresas
                className="px-3 py-2 text-sm font-medium text-gray-500 rounded-md hover:text-gray-900 hover:bg-gray-100"
              >
                Empresas
              </Link>
            </div>
            
          </div>

          <div className=" xs:block md:hidden">
            <Link
                to="/"
                className="px-3 py-2 text-sm font-medium text-gray-500 rounded-md hover:text-gray-900 hover:bg-gray-100"
              >
                Dashboard
              </Link>
              <Link
                to="/projects" // Ruta para Proyectos
                className="px-3 py-2 text-sm font-medium text-gray-500 rounded-md hover:text-gray-900 hover:bg-gray-100"
              >
                Proyectos
              </Link>
          </div>

             <div className="flex items-center space-x-4">
            {/* Perfil de Usuario con Menú Desplegable */}
            <div className="relative" ref={dropdownRef}>
              <button
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="flex items-center space-x-2 rounded-full p-1 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-gray-600" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-6-3a2 2 0 11-4 0 2 2 0 014 0zm-2 4a5 5 0 00-4.546 2.916A5.986 5.986 0 0010 16a5.986 5.986 0 004.546-2.084A5 5 0 0012 11z" clipRule="evenodd" />
                </svg>
                <span className="text-sm font-medium text-gray-700 hidden sm:block">
                  {user?.fullName }
                </span>
              </button>

              {isDropdownOpen && (
                <div className="absolute left-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-20">
                  <Link
                    to="/profile"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    onClick={() => setIsDropdownOpen(false)}
                  >
                    Editar Perfil
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="w-full text-left block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Cerrar Sesión
                  </button>
                </div>
              )}
            </div>
            
            
          </div>

        </div>
      </nav>
    </header>
  );
};