// src/pages/DashboardPage.tsx
import { useState, useEffect } from 'react';
import { getProjectsByUser } from '../api/projectService';
import { ProjectDetailCard } from '../components/ProjectDetailCard';
import type { ProjectInfoDetail } from '../types';
import { AddManualInvoiceModal } from '../components/modals/AddManualInvoiceModal';
import { AddBatchInvoicesModal } from '../components/modals/AddBatchInvoicesModal';
import { AddProjectModal } from '../components/modals/AddProjectModal';
import { AddCategoryModal } from '../components/modals/AddCategoryModal'; 
// Exportamos el tipo para que otros componentes puedan usarlo



export const ListProjects = () => {
  const [projects, setProjects] = useState<ProjectInfoDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);


  // --- 👇 1. ESTADOS PARA CONTROLAR LOS MODALES ---
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [selectedProjectNit, setSelectedProjectNit] = useState<string | null>(null);
  const [isManualModalOpen, setIsManualModalOpen] = useState(false);
  const [isBatchScanModalOpen, setIsBatchScanModalOpen] = useState(false);
  const [isAddProjectModalOpen, setIsAddProjectModalOpen] = useState(false);
  const [isCategoryModalOpen, setIsCategoryModalOpen] = useState(false);
  useEffect(() => {
    setLoading(true);
    getProjectsByUser()
      .then(data => setProjects(data))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);
  
  const handleProjectDeleted = (deletedProjectId: string) => {
    setProjects(currentProjects => currentProjects.filter(p => p.id.toString() !== deletedProjectId));
  };

  // --- 👇 2. FUNCIONES PARA ABRIR Y CERRAR MODALES ---
  const handleOpenManualModal = (projectId: string, nit: string) => {
    setSelectedProjectId(projectId);
    setSelectedProjectNit(nit);
    setIsManualModalOpen(true);
  };
   const handleOpenBatchScanModal = (projectId: string) => {
    setSelectedProjectId(projectId);
    setIsBatchScanModalOpen(true);
  };

  const handleCloseModals = () => {
    setIsManualModalOpen(false);
    setIsBatchScanModalOpen(false);
    setSelectedProjectId(null);
    setSelectedProjectNit(null);
  };

  const refreshData = () => {
    // Vuelve a cargar los proyectos para reflejar los nuevos totales
    setLoading(true);
    getProjectsByUser()
      .then(data => setProjects(data))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  };

  return (
    <>
    <div className="max-w-4xl mx-auto">
      {/* Acciones Globales */}
      <h1 className="text-2xl font-bold text-gray-800 mb-4">Mis Proyectos</h1>
      <div className="flex space-x-4 mb-8">
        <button 
          onClick={() => setIsAddProjectModalOpen(true)}
          className="px-6 py-3 font-bold text-white bg-blue-600 rounded-md hover:bg-blue-700 shadow-lg">
          Agregar Proyecto
        </button>
        <button 
          onClick={()=>setIsCategoryModalOpen(true)}
          className="px-4 py-2 font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-100">
          Agregar Categoria
        </button>
      </div>

      
      
      {loading && <p>Cargando proyectos...</p>}
      {error && <p className="text-red-600">{error}</p>}
      
      {!loading && !error && (
        <div className="space-y-6">
          {projects.length > 0 ? (
            projects.map(project => (
              <ProjectDetailCard 
                key={project.id} 
                project={project} // ✨ Pasa el objeto completo como prop
                onProjectDeleted={handleProjectDeleted}
                onAddManualInvoice={() => handleOpenManualModal(project.id.toString(), project.nit_beneficiario)}
                onAddBatchInvoice={() => handleOpenBatchScanModal(project.id.toString())}
                completeInfo={true}
                refreshData={()=>refreshData()}
              />
            ))
          ) : (
            <p className="text-gray-500">No tienes proyectos creados. ¡Añade uno para empezar!</p>
          )}
        </div>
      )}
    </div>

    {selectedProjectId && (
        <>
          <AddManualInvoiceModal
            isOpen={isManualModalOpen}
            onClose={handleCloseModals}
            projectId={selectedProjectId}
            nitBeneficiario={selectedProjectNit!}
            onInvoiceCreated={() => {
              handleCloseModals();
              refreshData(); // Refresca los datos del dashboard
            }}
          />
          <AddBatchInvoicesModal
            isOpen={isBatchScanModalOpen}
            onClose={handleCloseModals}
            projectId={selectedProjectId}
            onInvoiceCreated={refreshData} // Refresca en tiempo real
          />
        </>
      )}
       <AddProjectModal
              isOpen={isAddProjectModalOpen}
              onClose={() => setIsAddProjectModalOpen(false)}
              onProjectCreated={() => {
                setIsAddProjectModalOpen(false); // Cierra el modal
                refreshData(); // Refresca la lista de proyectos
              }}
            />
            <AddCategoryModal
        isOpen={isCategoryModalOpen}
        onClose={() => setIsCategoryModalOpen(false)}
        onCategoryCreated={() => {
          alert('Categoría creada con éxito.');
          // Aquí podrías añadir lógica para refrescar una lista de categorías si fuera necesario
        }}
      />
      </>
  );
};