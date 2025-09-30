// src/routes/ProtectedRoute.tsx
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export const ProtectedRoute = () => {
  const { isAuthenticated, isLoading } = useAuth();

  // Muestra un spinner o nada mientras se verifica la autenticación inicial
  if (isLoading) {
    return <div>Cargando...</div>; // O un componente de Spinner
  }

  // Si no está autenticado, lo redirige a la página de login
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Si está autenticado, renderiza el contenido de la ruta (la página)
  return <Outlet />;
};