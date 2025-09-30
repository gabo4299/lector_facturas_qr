// src/routes/AppRouter.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LoginPage from '../pages/LoginPages'; // <-- 1. Importar el componente real
import { ProtectedRoute } from './ProtectedRoute'; // 👈 1. Importa el guardia
import { MainLayout } from '../components/layout/MainLayout';
import { ProjectDetailPage } from '../pages/ProjectDetailPage'; 

// Aún no hemos creado estas páginas, pero ya definimos las rutas
// import LoginPage from '../pages/LoginPage';
// import DashboardPage from '../pages/DashboardPage';
// import InvoicesPage from '../pages/InvoicesPage';

// Componente temporal para simular una página
const PlaceholderPage = ({ title }: { title: string }) => (
  <div className="flex items-center justify-center h-screen">
    <h1 className="text-4xl font-bold text-primary">{title}</h1>
  </div>
);


const DashboardPage = () => (
  <div className="flex items-center justify-center h-screen">
    <h1 className="text-4xl font-bold text-gray-800">¡Bienvenido al Dashboard!</h1>
    {/* Más adelante aquí irá el botón de logout */}
  </div>
);

export const AppRouter = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Rutas Públicas */}
        <Route path="/login" element={<LoginPage  />} />

         <Route element={<ProtectedRoute />}>
            <Route element={<MainLayout />}>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/project/:projectId" element={<ProjectDetailPage />} />
                {/* <Route path="/projects" element={<ProjectPage />} />  */}
                {/* <Route path="/companies" element={<CompaniesPage />} /> Asumiendo que esta página existe */}
            
                <Route path="/invoices" element={<div>Página de Facturas</div>} />
            </Route>
          {/* Todas las rutas que pongas aquí adentro estarán protegidas */}
        </Route>
        
        {/* Ruta para páginas no encontradas */}
        <Route path="*" element={<PlaceholderPage title="404 - Not Found" />} />
      </Routes>
    </BrowserRouter>
  );
};