// src/pages/ProjectDetailPage.tsx
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getProjectById ,getInvoicesByProjectId} from '../api/projectService';
// modales
import { AddManualInvoiceModal } from '../components/modals/AddManualInvoiceModal';
import { AddBatchModal } from '../components/modals/AddBatchModal';
import { AddBatchInvoicesModal } from '../components/modals/AddBatchInvoicesModal';
import { AddElectronicInvoiceModal } from '../components/modals/AddElectronicInvoiceModal';
// Tipos básicos para el ejemplo, deberías refinarlos según tu API
import { deleteManualInvoice, deleteElectronicInvoice } from '../api/invoiceService';
import { EditInvoiceModal } from '../components/modals/EditInvoiceModal';
import type {Category} from '../types'

interface Empresa {
    nombre: string;
}
export interface Batch{
    nombre:string;
    descripcion:string;
    id:number;
}
interface ManualInvoiceAPI {
  id: number;
  fecha: string;
  empresa: Empresa | null;
  monto_total: number;
  batch: Batch | null;
  categoria: Category | null;
}
interface ElectronicInvoiceAPI {
  id: number;
  fecha: string;
  url?:string;
  empresa: Empresa | null;
  monto_total: number;
  monto_fiscal: number;
  batch: Batch | null;
  categoria: Category | null;
  factura_especial:boolean|null;
   status: string;
   save_pdf:boolean;
   complete:boolean;
}
interface InvoicesAPIResponse {
  facturas_manuales: ManualInvoiceAPI[];
  facturas_electronicas: ElectronicInvoiceAPI[];
}

export interface UnifiedInvoice {
  id: string;
  type: 'Manual' | 'Electrónica';
  url?:string;
  date: string;
  provider: string;
  status: string;
  batch: string;
  categoria_id?:number;
  batch_id?:number;
  save_pdf:boolean;
  category: string;
  total_amount: number;
  complete:boolean;
  vat: number;
  fecha_date?:Date;
}
// Tipos para los datos que vienen de la API
interface ProjectData { // Solo datos del proyecto
  id: number;
  nombre: string;
  fecha_inicio: Date;
  fecha_fin:Date;
  nit_beneficiario:string;
  batches:Batch[];
  // ... otros campos del proyecto
}


export const ProjectDetailPage = () => {
  const { projectId } = useParams<{ projectId: string }>(); // Obtiene el ID de la URL
  const [project, setProject] = useState<ProjectData | null>(null);
  const [unifiedInvoices, setUnifiedInvoices] = useState<UnifiedInvoice[]>([]);
  const [invoicesResponse, setInvoicesResponse] = useState<InvoicesAPIResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [isBatchScanModalOpen, setIsBatchScanModalOpen] = useState(false);
  const [isBatchModalOpen, setIsBatchModalOpen] = useState(false);
  const [isManualInvoiceModalOpen, setIsManualInvoiceModalOpen] = useState(false);
  const [isElectronicInvoiceModalOpen, setIsElectronicInvoiceModalOpen] = useState(false);

  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [invoiceToEdit, setInvoiceToEdit] = useState<UnifiedInvoice | null>(null);

const fetchProjectData = async (id: string) => {
    try {
        setLoading(true);
        // se deberia tener como respuesta el projectData
        const [projectData, invoicesData]= await Promise.all([
          getProjectById(id),
          getInvoicesByProjectId(id)
        ]);
        setProject(projectData);
        setInvoicesResponse(invoicesData)
        const manuales = invoicesData.facturas_manuales.map((inv:ManualInvoiceAPI): UnifiedInvoice => ({
          id: `M-${inv.id}`,
          type: 'Manual',
          status: 'Complete',
          save_pdf:false,
          complete:true,
          date: new Date(inv.fecha).toLocaleDateString(),
          provider: inv.empresa?.nombre || 'N/A',
          total_amount: inv.monto_total,
          vat: inv.monto_total * 0.03,
          batch: inv.batch?.nombre || '-',
          batch_id: inv.batch?.id || undefined,
          categoria_id: inv.categoria?.id || undefined,
          category: inv.categoria?.nombre || '-',
          fecha_date:new Date(inv.fecha),
        }));

        const electronicas = invoicesData.facturas_electronicas.map((inv:ElectronicInvoiceAPI): UnifiedInvoice => ({
          id: `E-${inv.id}`,
          type: 'Electrónica',
          status: inv.status, 
          complete:inv.complete,
          save_pdf:inv.save_pdf,
          url:inv.url,
          date: new Date(inv.fecha).toLocaleDateString(),
          provider: inv.empresa?.nombre || 'N/A',
          total_amount: inv.monto_total,
          vat: inv.monto_total * 0.03,
          batch: inv.batch?.nombre || '-',
          batch_id: inv.batch?.id || undefined,
          category: inv.categoria?.nombre || '-',
          categoria_id: inv.categoria?.id || undefined,
          fecha_date:new Date(inv.fecha),
        }));

        setUnifiedInvoices([...manuales, ...electronicas]);
      } catch (err) {
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError('Ocurrió un error inesperado.');
        }
      } finally {
        setLoading(false);
      }
    };

  
useEffect(() => {
    if (projectId) {
      fetchProjectData(projectId);
    }
  }, [projectId]);
 const handleOpenEditModal = (invoice: UnifiedInvoice) => {
    // Solo permite editar facturas electrónicas

    
    setInvoiceToEdit(invoice);

    setIsEditModalOpen(true);
  };

    const handleCloseModals = () => {
    setIsEditModalOpen(false);
    setInvoiceToEdit(null);
  };
  const refreshProjectData = () => {
    // Esta lógica es para forzar el re-render y la recarga de datos.
    // Una solución más avanzada podría usar un gestor de estado como SWR o React Query.
    if (projectId) {
      // Simplemente volvemos a llamar a la función de carga
      fetchProjectData(projectId);
    }
  };
  if (loading) {
    return <div className="text-center p-8">Cargando proyecto...</div>;
  }

  if (error) {
    return <div className="text-center p-8 bg-red-100 text-red-700 rounded-md">{error}</div>;
  }



   if (!project || !invoicesResponse) {
    return <div className="text-center p-8">No se encontraron datos.</div>;
  }

  const handleDeleteInvoice = async (invoiceId: string, invoiceType: 'Manual' | 'Electrónica') => {
    // Pide confirmación al usuario antes de borrar
    const isConfirmed = window.confirm('¿Estás seguro de que deseas eliminar esta factura? Esta acción no se puede deshacer.');

    if (!isConfirmed) {
      return; // Si el usuario cancela, no hagas nada
    }

    try {
      // Extraemos el ID numérico (ej. de 'manual-9' obtenemos 9)
      const numericId = parseInt(invoiceId.split('-')[1], 10);

      if (invoiceType === 'Manual') {
        await deleteManualInvoice(numericId);
      } else {
        await deleteElectronicInvoice(numericId);
      }

      // Actualizamos la UI eliminando la factura del estado local
      setUnifiedInvoices(currentInvoices =>
        currentInvoices.filter(inv => inv.id !== invoiceId)
      );
      
      alert('Factura eliminada con éxito.');

    } catch (error) {
      if (error instanceof Error) {
        alert(`Error al eliminar la factura: ${error.message}`);
      } else {
        alert('Ocurrió un error inesperado.');
      }
    }
  };
   const getStatusColor = (complete:boolean,status: string) => {

    if (!complete){
        if (/error/i.test(status)) {
            
            return 'bg-red-200 text-red-800 hover:bg-red-100';
        }
        else{
            return 'bg-yellow-100 text-yellow-800 hover:bg-yellow-50 ';
        }
        
        
      
        
     
    }
    else
    {
       return 'bg-gray-100 text-gray-800 hover:bg-gray-50 ';
    }
      
    
  };
     const stats = {
    totalInvoices: unifiedInvoices.length,
    manualInvoices: invoicesResponse.facturas_manuales.length,
    electronicInvoices: invoicesResponse.facturas_electronicas.length,
    totalBatches: project.batches?.length || 0,
    totalSum: unifiedInvoices.reduce((acc, inv) => acc + inv.total_amount, 0),
    totalVat: unifiedInvoices.reduce((acc, inv) => acc + inv.vat, 0),
  };
  return (
    <>
    <div className="max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-4">{project.nombre}</h1>
            <div className="mt-4 ml-2 p-4 bg-gray-100 rounded-lg border border-gray-200">
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 text-sm">
            <div className="text-gray-700">
              <strong className="block">Facturas Totales:</strong>
              <span>{stats.totalInvoices}</span>
            </div>
            <div className="text-gray-700">
              <strong className="block">F. Electrónicas:</strong>
              <span>{stats.electronicInvoices}</span>
            </div>
            <div className="text-gray-700">
              <strong className="block">F. Manuales:</strong>
              <span>{stats.manualInvoices}</span>
            </div>
            <div className="text-gray-700">
              <strong className="block">Lotes Totales:</strong>
              <span>{stats.totalBatches}</span>
            </div>
            <div className="text-gray-700">
              <strong className="block">Suma Total:</strong>
              <span>{stats.totalSum.toLocaleString('es-BO', { style: 'currency', currency: 'BOB' })}</span>
            </div>
            <div className="text-gray-700">
              {/* Asumiendo que "ganancia" se refiere al crédito fiscal (IVA) */}
              <strong className="block">Ganancia (3%):</strong>
              <span>{stats.totalVat.toLocaleString('es-BO', { style: 'currency', currency: 'BOB' })}</span>
            </div>
          </div>
        </div>
         <div className="mb-6 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:flex lg:space-x-3 gap-3">
        <button 
            onClick={() => setIsElectronicInvoiceModalOpen(true)}
            className="px-6 py-3 font-bold text-white transition-colors bg-blue-600 rounded-md hover:bg-blue-700 shadow-lg w-full lg:w-auto">
          Agregar Factura Electronica
        </button>
        <button onClick={() => setIsBatchScanModalOpen(true)} className="px-6 py-3 font-bold text-white transition-colors bg-yellow-600 rounded-md hover:bg-green-700 shadow-lg w-full lg:w-auto">
            Escanear en Lote
          </button>
        <button
            onClick={() => setIsManualInvoiceModalOpen(true)} 
            className="px-6 py-3 font-bold text-white transition-colors bg-blue-600 rounded-md hover:bg-blue-700 shadow-lg w-full lg:w-auto">
          Agregar Factura Manual
        </button>
        <button 
            onClick={() => setIsBatchModalOpen(true)}
            className="px-4 py-2 font-medium text-gray-700 transition-colors bg-white border border-gray-300 rounded-md hover:bg-gray-100 w-full lg:w-auto">
          Agregar Lote
        </button>
        {/* cuando tengas las clase  */}
        <button className="px-4 py-2 font-medium text-gray-700 transition-colors bg-white border border-gray-300 rounded-md hover:bg-gray-100 w-full lg:w-auto">
          agergar en la tabla categoria en codigo
        </button>
      </div>
      </div>

      {/* Tabla de Facturas (ahora usa la lista unificada) */}
      <div className="bg-white rounded-lg shadow overflow-x-auto">
        <table className="w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">id</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Empresa</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Lote</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider max-w-xs">
                Estado
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">% ganado</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Categoria</th>
              
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {unifiedInvoices.length > 0 ? (
              unifiedInvoices.map((invoice) => (
                <tr key={invoice.id} className={`${getStatusColor(invoice.complete,invoice.status)}`}>
                  <td className='px-6 py-4 whitespace-nowrap text-sm text-gray-700'>
                    <a href={invoice.url} target="_blank">{invoice.id}</a>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex justify-end space-x-2">
                        <button 
                          onClick={() => handleOpenEditModal(invoice)} 
                          className="px-1 py-1 bg-indigo-100 rounded-md text-indigo-600 hover:text-indigo-900">
                            Editar</button>
                        <button 
                          onClick={() => handleDeleteInvoice(invoice.id, invoice.type)}
                          className="px-1 py-1 bg-red-300 rounded-md text-red-600 hover:text-red-900">
                            Eliminar</button>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{invoice.date}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 ">{invoice.provider}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{invoice.batch}</td>
                  <td className="px-6 py-4 text-sm font-medium ">
                    <span
                    title={invoice.status} // ✨ Muestra el texto completo al pasar el ratón
                    className={`truncate inline-flex max-w-25 px-2 text-xs leading-5 font-semibold rounded-full `}
                    >
                    {invoice.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 text-right">{invoice.total_amount.toFixed(2)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 text-right">{invoice.vat.toFixed(2)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full `}>
                      {invoice.category}
                    </span>
                  </td>
                  
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={6} className="text-center py-8 text-gray-500">No hay facturas en este proyecto.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
    {projectId && (
        <AddBatchModal
          isOpen={isBatchModalOpen}
          onClose={() => setIsBatchModalOpen(false)}
          projectId={projectId}
          onBatchCreated={refreshProjectData}
        />
      )}
       <AddManualInvoiceModal
        isOpen={isManualInvoiceModalOpen}
        onClose={() => setIsManualInvoiceModalOpen(false)}
        projectId={project.id.toString()}
        nitBeneficiario={project.nit_beneficiario} // Asegúrate que este dato venga en `project`
        onInvoiceCreated={refreshProjectData}
      />
      <AddElectronicInvoiceModal
        isOpen={isElectronicInvoiceModalOpen}
        onClose={() => setIsElectronicInvoiceModalOpen(false)}
        projectId={project.id.toString()}
        onInvoiceCreated={refreshProjectData}
      />
      <AddBatchInvoicesModal
          isOpen={isBatchScanModalOpen}
          onClose={() => setIsBatchScanModalOpen(false)}
          projectId={project.id.toString()}
          onInvoiceCreated={refreshProjectData}
        />
        <EditInvoiceModal
        isOpen={isEditModalOpen}
        onClose={handleCloseModals}
        invoice={invoiceToEdit}
        batches={project.batches || []}
        onInvoiceUpdated={() => {
          handleCloseModals();
          refreshProjectData(); // Reutiliza tu función para refrescar datos
        }}
      />
  </>
  );
};