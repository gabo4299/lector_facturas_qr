// src/components/layout/MainLayout.tsx
import { Outlet } from 'react-router-dom';
import { Navbar } from './Navbar'; // Crearemos este componente a continuación

export const MainLayout = () => {
  return (
    <div className="min-h-screen bg-gray-100">
      {/* Barra de Navegación Fija en la Parte Superior */}
      <Navbar />

      {/* Contenido Principal de la Página */}
      <main className="p-4 sm:p-6 lg:p-8">
        {/* Outlet renderizará el componente de la ruta actual (Dashboard, Invoices, etc.) */}
        <Outlet />
      </main>
    </div>
  );
};