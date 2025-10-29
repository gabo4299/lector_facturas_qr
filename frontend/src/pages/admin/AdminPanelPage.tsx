// src/pages/admin/AdminPanelPage.tsx
import { useState } from 'react';
import { UserManagementTab } from './UserManagementTab';
import { ProjectManagementTab } from './ProjectManagementTab';
import { CompanyManagementTab } from './CompanyManagementTab';
import { CategoryManagementTab } from './CategoryManagementTab';
import { InvoiceManagementTab } from './InvoiceManagementTab';

type Tab = 'usuarios' | 'proyectos' | 'facturas' | 'empresas' | 'categorias';

const tabs: { id: Tab; label: string }[] = [
  { id: 'usuarios', label: 'Usuarios' },
  { id: 'proyectos', label: 'Proyectos' },
  { id: 'facturas', label: 'Facturas' },
  { id: 'empresas', label: 'Empresas' },
  { id: 'categorias', label: 'Categorías' },
];

export const AdminPanelPage = () => {
  const [activeTab, setActiveTab] = useState<Tab>('usuarios');

  const renderContent = () => {
    switch (activeTab) {
      case 'usuarios': return <UserManagementTab />;
      case 'proyectos': return <ProjectManagementTab />; // Debes crear este componente
      case 'facturas': return <InvoiceManagementTab />;
      case 'empresas': return <CompanyManagementTab />; // Debes crear este componente
      case 'categorias': return <CategoryManagementTab />; // Debes crear este componente
      
      
      
      default: return null;
    }
  };

  return (
    <div className="max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Panel de Administración</h1>

      {/* Navegación de Pestañas */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-4" aria-label="Tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm
                ${activeTab === tab.id
                  ? 'border-blue-500 text-blue-600' // Estilo de pestaña activa
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300' // Estilo inactivo
                }
              `}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Contenido de la Pestaña Activa */}
      <div className="py-6">
        {renderContent()}
      </div>
    </div>
  );
};