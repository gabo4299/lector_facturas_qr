// src/routes/AppRouter.tsx
import {  Routes, Route } from 'react-router-dom';
import LoginPage from '../pages/LoginPages'; // <-- 1. Importar el componente real
import { ProtectedRoute } from './ProtectedRoute'; // 👈 1. Importa el guardia
import { Navigate, Outlet } from 'react-router-dom';
import { MainLayout } from '../components/layout/MainLayout';
import { ProjectDetailPage } from '../pages/ProjectDetailPage'; 
import { DashboardPage } from '../pages/DashboardPage';
import { ListProjects } from '../pages/ListProjects';
import { CompaniesPage } from '../pages/CompaniesPage';
// import QrInputModal from '../features/QrReader/QrInputModal';
import { AdminPanelPage } from '../pages/admin/AdminPanelPage';
import { useAuth } from '../hooks/useAuth';
import { QrScanner2 } from '../features/QrScanner2';
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

const AdminRoute = () => {
  const { user } = useAuth();
  if (user?.is_su) {
    return <Outlet />; // Permite el acceso
  }
  return <Navigate to="/" replace />; // Redirige a la página principal si no es SU
};

 


export const AppRouter = () => {
  return (
    
      <Routes>
        {/* Rutas Públicas */}
        <Route path="/login" element={<LoginPage  />} />

         <Route element={<ProtectedRoute />}>
            <Route element={<MainLayout />}>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/project/:projectId" element={<ProjectDetailPage />} />
                {/* <Route path="/projects" element={<ProjectPage />} />  */}
                {/* <Route path="/companies" element={<CompaniesPage />} /> Asumiendo que esta página existe */}
                <Route path="/projects" element={<ListProjects/>} />
                <Route path="/companies" element={<CompaniesPage/>} />
                
               
            </Route>
            <Route element={<AdminRoute />}>
            <Route element={<MainLayout />}>
              <Route path="/admin" element={<AdminPanelPage/>} />
            
            </Route>
            </Route>
          {/* Todas las rutas que pongas aquí adentro estarán protegidas */}
        </Route>
        
        {/* Ruta para páginas no encontradas */}
         <Route path='/qr_test' element={
                     <div className="App">
                          <h1>Escáner de Códigos QR</h1>
                           <QrScanner2
                           onScanSuccess={(e)=>console.log(e)}
                           onScanError={(e)=>console.error(e)}/>
                        </div>
                }/>
        <Route path="*" element={<PlaceholderPage title="404 - Not Found" />} />
      </Routes>
    
  );
};