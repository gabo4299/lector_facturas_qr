import { useState, useRef, useEffect } from 'react';
import { deleteProject } from '../api/projectService';
import type { ProjectInfo } from '../types'; // Asumiendo que el tipo está en DashboardPage o en un archivo global
import { useNavigate } from 'react-router-dom';
import { AddMemberModal } from './modals/AddMemberModal';
import { EditProjectModal } from '../components/modals/editProjectModal';
interface ProjectCardProps {
  project: ProjectInfo; // Recibe el objeto completo del proyecto
  onProjectDeleted: (id: string) => void;
  onAddManualInvoice: () => void; // Nueva prop
  onAddBatchInvoice: () => void;  // Nueva prop
  refreshData:()=>void
  completeInfo?:boolean
}


export const ProjectDetailCard = ({ project, onProjectDeleted , onAddManualInvoice, onAddBatchInvoice,completeInfo,refreshData }: ProjectCardProps) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const [NBatchs,setNBatchs]=useState(0)
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isAddMemberModalOpen, setIsAddMemberModalOpen] = useState(false);
  const [viewFullData, setViewFullData]=useState(false);

    const navigate = useNavigate();
     
  // Cierra el menú si se hace clic afuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    setNBatchs(project.batches.length)
  
    return () => {
      
    }
  }, [project.batches])
  
  const handleDelete = async () => {
    if (window.confirm(`¿Estás seguro de que quieres eliminar el proyecto "${project.nombre}"?`)) {
      try {
        await deleteProject(project.id.toString());
        onProjectDeleted(project.id.toString());
      } catch (err) {
        alert((err as Error).message);
      }
    }
    setIsMenuOpen(false);
  };

const getGridColsClass = () => {
  
  if (NBatchs === 1) return 'sm:grid-cols-1';
  if (NBatchs === 2) return 'sm:grid-cols-2';
    return 'sm:grid-cols-3'; // máximo 3 columnas
    };
  // Cálculos basados en los datos recibidos
  const totalInvoices = project.cantidad_facturas_electronicas + project.cantidad_facturas_manuales;
  const totalVat = project.porcentajeGanado; // IVA calculado
  const handleView=()=>{
    if (viewFullData === false){
      setViewFullData(true)
    }
    else{
      setViewFullData(false)
    }

  }
  return (
    <>
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="p-6">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-xl font-bold text-gray-800">{project.nombre}</h3>
            <p className="text-sm text-gray-500">NIT: {project.nit_beneficiario}</p>
            <p className="text-xs text-gray-400">
              {new Date(project.fecha_inicio).toLocaleDateString()} - {new Date(project.fecha_fin).toLocaleDateString()}
            </p>
          </div>
          {/* Menú de 3 puntos */}

           {/* Controles: Agregar Colaborador y Menú */}
          <div className="flex items-center space-x-2" ref={menuRef}>
            {/* ✨ NUEVO BOTÓN PARA AGREGAR COLABORADORES ✨ */}
             <button 
              onClick={() => navigate(`/project/${project.id}`, { replace: true })}
              className="p-2 rounded-full hover:bg-gray-100 text-gray-500 hover:text-gray-700"
              title="Ir a proyecto"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
               <g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"><path fill="#000000" fill-rule="evenodd" d="M8 3.517a1 1 0 011.62-.784l5.348 4.233a1 1 0 010 1.568l-5.347 4.233A1 1 0 018 11.983v-1.545c-.76-.043-1.484.003-2.254.218-.994.279-2.118.857-3.506 1.99a.993.993 0 01-1.129.096.962.962 0 01-.445-1.099c.415-1.5 1.425-3.141 2.808-4.412C4.69 6.114 6.244 5.241 8 5.042V3.517zm1.5 1.034v1.2a.75.75 0 01-.75.75c-1.586 0-3.066.738-4.261 1.835a8.996 8.996 0 00-1.635 2.014c.878-.552 1.695-.916 2.488-1.138 1.247-.35 2.377-.33 3.49-.207a.75.75 0 01.668.745v1.2l4.042-3.2L9.5 4.55z" clip-rule="evenodd"></path></g>
              </svg>
            </button>
            
            <button 
              onClick={() => setIsAddMemberModalOpen(true)}
              className="p-2 rounded-full hover:bg-gray-100 text-gray-500 hover:text-gray-700"
              title="Agregar colaborador"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path d="M8 9a3 3 0 100-6 3 3 0 000 6zM8 11a6 6 0 016 6H2a6 6 0 016-6zM16 11a1 1 0 10-2 0v1h-1a1 1 0 100 2h1v1a1 1 0 102 0v-1h1a1 1 0 100-2h-1v-1z" />
              </svg>
            </button>
             
             {completeInfo&&(<button 
              onClick={handleView}
              className="p-2 rounded-full hover:bg-gray-100 text-gray-500 hover:text-gray-700"
              title="ver Info completa"
            >
              {viewFullData ? "▲" : "▼"}
            </button>)}
            
            {/* Menú de 3 puntos mejorado */}
            <div className="relative">
              <button onClick={() => setIsMenuOpen(!isMenuOpen)} className="p-2 rounded-full hover:bg-gray-100">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01" /></svg>
              </button>

              {/* ✨ MENÚ DESPLEGABLE CON ESTILOS MEJORADOS ✨ */}
              <div 
                className={`
                  absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-20 border border-gray-200
                  transition-all duration-150 ease-out
                  ${isMenuOpen ? 'opacity-100 scale-100' : 'opacity-0 scale-95 pointer-events-none'}
                `}
                style={{ transformOrigin: 'top right' }}
              >
                <button 
                onClick={()=>setIsEditModalOpen(true)}
                className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.5L15.232 5.232z" /></svg>
                  Editar
                </button>
                <button onClick={handleDelete} className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-gray-100">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                  Eliminar
                </button>
              </div>
            </div>
          </div>

        </div>
        
        {/* Estadísticas del proyecto */}
        <div className="mt-4 grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-xs text-gray-500">Gasto Total</p>
            <p className="text-lg font-semibold text-gray-800">Bs. {project.suma_total.toLocaleString('es-BO')}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Ganancia acumulada</p>
            <p className="text-lg font-semibold text-green-600">Bs. {totalVat.toLocaleString('es-BO')}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Nº Facturas</p>
            <p className="text-lg font-semibold text-gray-800">{totalInvoices}</p>
          </div>
        </div>
      
      {viewFullData && (
        <>
        {/* cabecera sde facturas */}
        <div className="mt-4 grid grid-cols-2 gap-4 text-center">
            <div>
                <p className="text-s font-semibold text-gray-800 ">Facturas Electronicas</p>
            </div>
                        <div>
                <p className="text-s font-semibold text-gray-800 ">Facturas Manuales</p>
            </div>
        </div>
        {/* data de facturas  */}
         <div className="mt-4 grid grid-cols-4 gap-4 text-center">
          <div>
            <p className="text-xs text-gray-500">Nº Facturas</p>
            <p className="text-lg font-semibold text-gray-800">{project.cantidad_facturas_electronicas}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Suma</p>
            <p className="text-lg font-semibold text-gray-800">Bs {project.suma_facturas_electronicas?.toLocaleString('es-BO')}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Nº Facturas</p>
            <p className="text-lg font-semibold text-gray-800">{project.cantidad_facturas_manuales}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Suma</p>
            <p className="text-lg font-semibold text-gray-800">Bs {project.suma_facturas_manuales?.toLocaleString('es-BO')}</p>
          </div>
        </div>
        {/* Cantidad de lotes */}
        <div className="mt-2 grid grid-cols-1 gap-1 text-center">
            <div>
                <p className="text-s font-semibold text-gray-800">Lotes</p>
            </div>
            <div>
                <p className="text-lg font-semibold text-gray-800">{NBatchs}</p>
            </div>
        </div>
        <div className={`mt-4 grid grid-cols-1 gap-4 text-center ${getGridColsClass()}`}>
        {project.batches.map ((i,index)=>(
            <div key={index} className=''>
                <div>
                     <p className="text-xs text-gray-500">
                        {i.batch_info.nombre}</p>
                    <p className="text-lg font-semibold text-gray-500">
                        Bs. {i.monto_total_batch.toLocaleString('es-BO')}</p>
                </div>
            <p className="text-xs font-semibold text-green-600">
               Ganancia: Bs {(i.monto_total_batch*0.03).toLocaleString('es-BO')}</p>
            <p className="text-xs text-gray-500">
               Electronicas: {i.cantidad_electronicas}</p>
            
            <p className="text-xs text-gray-500">
               Manuales:{i.cantidad_manuales}</p>

            
            </div>
        ))}

        </div>
        
        </>
      )}
      </div>
      {/* Botones de Acción Rápida */}
      <div className="bg-gray-50 px-6 py-3 flex space-x-3">
        <button onClick={onAddManualInvoice} className="flex-1 px-4 py-2 text-sm font-bold text-white bg-blue-600 rounded-md hover:bg-blue-700">
            Agregar Factura Manual</button>
        <button onClick={onAddBatchInvoice} className="flex-1 px-4 py-2 text-sm font-bold text-white bg-green-600 rounded-md hover:bg-green-700">
            Escanear Facturas</button>
      </div>
    </div>
  <AddMemberModal
            isOpen={isAddMemberModalOpen}
            onClose={() => setIsAddMemberModalOpen(false)}
            projectId={project.id}
          />

    <EditProjectModal
        isOpen={isEditModalOpen}
        onClose={()=>setIsEditModalOpen(false)}
        project={project}
        onProjectUpdated={refreshData}
      />
  </>
  );
};