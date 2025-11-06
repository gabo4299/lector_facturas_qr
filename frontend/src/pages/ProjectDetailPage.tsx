// src/pages/ProjectDetailPage.tsx
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import {checkAllInvoices, getReport,getResumeProject } from '../api/projectService';
import { Popover,PopoverButton,PopoverPanel } from '@headlessui/react';
// modales
import EditIcon from '../components/ui/icons/EditIcon';
// import DownloadIcon from '../components/ui/icons/DownloadIcon';
import DeleteIcon from '../components/ui/icons/Deleteicon';
// import RefreshIcon from '../components/ui/icons/RefreshIcon';

import { AddManualInvoiceModal } from '../components/modals/AddManualInvoiceModal';
import { AddBatchModal } from '../components/modals/AddBatchModal';
import { AddBatchInvoicesModal } from '../components/modals/AddBatchInvoicesModal';
import { AddElectronicInvoiceModal } from '../components/modals/AddElectronicInvoiceModal';
// Tipos básicos para el ejemplo, deberías refinarlos según tu API
import { deleteManualInvoice, deleteElectronicInvoice ,dowloadInvoicePdf,checkInvoice} from '../api/invoiceService';
// paginated 
import { getPaginatedInvoices } from '../api/invoiceService';
import type {InvoiceFiltersType} from '../api/invoiceService';
import { InvoiceFilters as InvoiceFiltersComponent } from '../components/ui/InvoiceFilters';
import { Pagination } from '../components/ui/Pagination'; // Asegúrate de tener este componente
// --------
import { EditInvoiceModal } from '../components/modals/EditInvoiceModal';
import type {ProjectResume,ElectronicInvoiceAPI,ManualInvoiceAPI, Category,Batch} from '../types'
import DownloadIcon from '../components/ui/icons/DownloadIcon';
import RefreshIcon from '../components/ui/icons/RefreshIcon';
import { ProjectStatsBreakdown } from '../components/ui/ProjectStatsBreakdown';
import { getCategories } from '../api/categoryService';








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
  total_fiscal?: number;
  special?:boolean;
  complete:boolean;
  vat: number;
  fecha_date?:Date;
}
// Tipos para los datos que vienen de la API






export const ProjectDetailPage = () => {
  const { projectId } = useParams<{ projectId: string }>(); // Obtiene el ID de la URL
  // const [project, setProject] = useState<ProjectData | null>(null);
  const [resumeProject,setResumeProject]=useState<ProjectResume | null>(null);
  const [unifiedInvoices, setUnifiedInvoices] = useState<UnifiedInvoice[]>([]);
  const [batchesProyecto, setBatchesProyecto] = useState<Batch[]>([]);
  const [categorias, setCategorias] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [isBatchScanModalOpen, setIsBatchScanModalOpen] = useState(false);
  const [isBatchModalOpen, setIsBatchModalOpen] = useState(false);
  const [isManualInvoiceModalOpen, setIsManualInvoiceModalOpen] = useState(false);
  const [isElectronicInvoiceModalOpen, setIsElectronicInvoiceModalOpen] = useState(false);
  const [virtualInvoices , setVirtualInvoices] = useState(false);
  const [unclompleteInvoices , setUnclompleteInvoices] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [invoiceToEdit, setInvoiceToEdit] = useState<UnifiedInvoice | null>(null);
  // states filtros 
   // Estado para filtros, paginación y orden
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [totalItems, setTotalItems] = useState(0);
  const [limit, setLimit] = useState(10);
  const [sortBy, setSortBy] = useState('fecha_creacion');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
const [isDetailsOpen, setIsDetailsOpen] = useState(false); // 👈 2. Nuevo estado para el colapso
  
  
  // --- 👇 LÓGICA DE FILTROS ACTUALIZADA 👇 ---
  // 1. Estado para los filtros que el usuario está editando (el borrador)
  const [draftFilters, setDraftFilters] = useState<InvoiceFiltersType>({ tipo_factura: 'todas' });
  // 2. Estado para los filtros que se han aplicado y se usan en la API
  const [activeFilters, setActiveFilters] = useState<InvoiceFiltersType>({ tipo_factura: 'todas' });


useEffect(() => {
    if (projectId) {
      getResumeProject(projectId)
        .then(data => {
          setResumeProject(data); // Guardas los datos completos del resumen

          // 👇 2. DENTRO DEL useEffect, DESPUÉS DE OBTENER LOS DATOS, HACEMOS LA TRANSFORMACIÓN
          if (data && data.batches) {
            // Usamos .map() para crear un nuevo array que contenga solo el objeto 'batch_info' de cada elemento.
            const extractedBatches = data.batches.map((resume: { batch_info: Batch; }) => resume.batch_info);
            setBatchesProyecto(extractedBatches); // Guardamos la nueva lista en su estado
          }
        })
        .catch(err => setError((err as Error).message));
      getCategories().then(
        data=>setCategorias(data)
      ).catch(err => setError((err as Error).message));
    }
  }, [projectId]);

  useEffect(() => {
    if (projectId) {
      setLoading(true);
      // La llamada a la API ahora usa los filtros activos
      getPaginatedInvoices(projectId, currentPage, limit, sortBy, sortOrder, activeFilters)
        .then(response => {
          const unified = response.items.map((inv: (ElectronicInvoiceAPI|ManualInvoiceAPI)): UnifiedInvoice => {
            // ... (tu lógica de mapeo para manual y electrónica)
            // ... (necesitarás una forma de saber si 'inv' es manual o electrónica)
            const isManual = !('status' in inv); // Asunción simple
            // console.log(isManual?"es manual ":inv.monto_fiscal!)
            
            return {
              id: `${isManual ? 'M' : 'E'}-${inv.id}`,
              type: isManual ? 'Manual' : 'Electrónica',
              status: isManual? 'Complete':inv.status, 
              complete: isManual? true:inv.complete,
              special:isManual? false :inv.factura_especial||false,
              save_pdf: isManual? false:inv.save_pdf,
              url: isManual? '':inv.url,
              date: new Date(inv.fecha).toLocaleDateString(),
              provider: inv.empresa?.nombre || 'N/A',
              total_amount: inv.monto_total,
              total_fiscal: isManual?inv.monto_total:inv.monto_fiscal||inv.monto_total,
              vat: inv.monto_total * 0.03,
              batch: inv.batch?.nombre || '-',
              batch_id: inv.batch?.id || undefined,
              category: inv.categoria?.nombre || '-',
              categoria_id: inv.categoria?.id || undefined,
              fecha_date:new Date(inv.fecha),
              // ... resto de los campos
            };
          });
          
           const hasPdfToSave = unified.some(i => i.save_pdf === true);
            if (hasPdfToSave) {
              setVirtualInvoices(true);
            }
            else{
              setVirtualInvoices(false);
            }

             const isInconplete = unified.some(i => i.complete === false);
            if (isInconplete) {
              setUnclompleteInvoices(true);
            }
            else{
              setUnclompleteInvoices(false);
            }
          setUnifiedInvoices(unified);
          setTotalPages(response.total_pages);
          setTotalItems(response.total);
        })
        .catch(err => setError((err as Error).message))
        .finally(() => setLoading(false));

        
    }
  }, [projectId, currentPage, limit, sortBy, sortOrder, activeFilters]); // 👈 La dependencia clave


  const fetchInvoices = async () => {
        setLoading(true);
        try {
          const response = await getPaginatedInvoices(projectId||"", currentPage, limit, sortBy, sortOrder, activeFilters);

          const unified = response.items.map((inv: (ElectronicInvoiceAPI|ManualInvoiceAPI)): UnifiedInvoice => {

            const isManual = !('status' in inv); // Asunción simple
            console.log(isManual?"es manual ":inv.monto_fiscal!)
            return {
              id: `${isManual ? 'M' : 'E'}-${inv.id}`,
              type: isManual ? 'Manual' : 'Electrónica',
              status: isManual? 'Complete':inv.status, 
              complete: isManual? true:inv.complete,
              special:isManual? false :inv.factura_especial||false,
              save_pdf: isManual? false:inv.save_pdf,
              url: isManual? '':inv.url,
              date: new Date(inv.fecha).toLocaleDateString(),
              provider: inv.empresa?.nombre || 'N/A',
              total_amount: inv.monto_total,
              total_fiscal: isManual?inv.monto_total:inv.monto_fiscal||inv.monto_total,
              vat: inv.monto_total * 0.03,
              batch: inv.batch?.nombre || '-',
              batch_id: inv.batch?.id || undefined,
              category: inv.categoria?.nombre || '-',
              categoria_id: inv.categoria?.id || undefined,
              fecha_date:new Date(inv.fecha),
              // ... resto de los campos
            };
          });
          const hasPdfToSave = unified.some(i => i.save_pdf === true);
            if (hasPdfToSave) {
              setVirtualInvoices(true);
            }
            else{
              setVirtualInvoices(false);
            }
          setUnifiedInvoices(unified);
          setTotalPages(response.total_pages);
          setTotalItems(response.total);
          
        } catch (err) {
          setError((err as Error).message);
        } finally {
          setLoading(false);
        }
      };

      const handleApplyFilters = () => {
    setCurrentPage(1); // Siempre resetea a la página 1 al aplicar nuevos filtros
    setActiveFilters(draftFilters);
  };

  const handleResetFilters = () => {
    const initialFilters = { tipo_factura: 'todas' as const };
    setDraftFilters(initialFilters);
    setActiveFilters(initialFilters); // Aplica el reseteo inmediatamente
    setCurrentPage(1);
  };

  
   const handleSort = (column: string) => {
    if (sortBy === column) {
      setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      if (column==="fecha_creacion"){
        setSortOrder('desc');
      }
      else{

        setSortOrder('asc');
      }
    }
  };

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
      // fetchProjectData(projectId);
      handleResetFilters();
      fetchInvoices();
    }
  };
  if (loading) {
    return <div className="text-center p-8">Cargando proyecto...</div>;
  }

  if (error) {
    return <div className="text-center p-8 bg-red-100 text-red-700 rounded-md">{error}</div>;
  }



   if (!resumeProject || !unifiedInvoices) {
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
   const getStatusColor = (complete:boolean,status: string,isSpecial:boolean) => {

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
      if (isSpecial === true){
          return 'bg-blue-100 text-gray-800 hover:bg-blue-50 ';
      }
      else
      {

        return 'bg-gray-100 text-gray-800 hover:bg-gray-50 ';
      }
    }
      
    
  };
  const totalElecInvoices =resumeProject?.cantidad_facturas_electronicas||0;
  const totalManualInvoices =resumeProject?.cantidad_facturas_manuales||0;

     const stats = {
    totalInvoices: totalElecInvoices+totalManualInvoices ,
    manualInvoices: resumeProject?.cantidad_facturas_manuales || 0,
    electronicInvoices: resumeProject?.cantidad_facturas_electronicas||0,
    totalBatches: resumeProject.batches?.length || 0,
    totalSum: resumeProject?.suma_total,
    totalFiscal: resumeProject?.suma_fiscal,
    totalVat: resumeProject?.porcentajeGanado,
    sumaElectronicas:resumeProject?.suma_facturas_electronicas,
    sumaManuales:resumeProject?.suma_facturas_manuales
  };

  const handleDowload=async (numericId:string)=>{
    const numero = numericId.split("-")[1];
    await dowloadInvoicePdf(numero);

      
    
  }

    const handleDowloadReporte=async ()=>{
    
    await getReport(projectId!);

      
    
  }

      const handleCheckFactuas=async ()=>{
    const data= await checkAllInvoices(projectId!);
    alert(data?.mensaje)
  }
  const handleCheckInvoice=async (numericId:string,status:string)=>{

    if (status === 'pendiente'){
      return alert ("factura procesandose")
    }
    const numero = numericId.split("-")[1];
    await checkInvoice(numero)

      
    
  }
  
  return (
    <>
    <div className="max-w-7xl mx-auto">
      <div className="mb-6">
        <div className='relative'>
        <h1 className="text-3xl font-bold text-gray-800 mb-4">{resumeProject.nombre}</h1>
        <p className="text-xs text-gray-800">
          del  {new Date(resumeProject.fecha_inicio).toLocaleDateString()} al  {new Date(resumeProject.fecha_fin).toLocaleDateString()}
        </p>
            <div className="mt-4 ml-2 p-4 bg-gray-100 rounded-lg border border-gray-200">
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 text-sm">
            <div className="text-gray-700">
              <strong className="block">Facturas Totales:</strong>
              <span>{stats.totalInvoices}</span>

            </div>
            <div className="text-gray-700">
              <strong className="block">F. Electrónicas:</strong>
              <span>{isDetailsOpen?"N°":""}{stats.electronicInvoices} {isDetailsOpen?("| Total: " + stats.sumaElectronicas?.toLocaleString('es-BO', { style: 'currency', currency: 'BOB' })):""}</span>
              {isDetailsOpen && <div>
                <span>Ganancia:</span> <span className='text-green-600'>{((stats.sumaElectronicas||0)*0.03).toLocaleString('es-BO', { style: 'currency', currency: 'BOB' })}</span></div>}
            </div>
            <div className="text-gray-700">
              <strong className="block">F. Manuales:</strong>
              <span>{stats.manualInvoices} {isDetailsOpen?("| Total: " + stats.sumaManuales?.toLocaleString('es-BO', { style: 'currency', currency: 'BOB' })):""}</span>
              {isDetailsOpen && <div>
                <span>Ganancia:</span> <span className='text-green-600'>{((stats.sumaManuales||0)*0.03).toLocaleString('es-BO', { style: 'currency', currency: 'BOB' })}</span></div>}
            </div>
            <div className="text-gray-700">
              <strong className="block">Suma Total | Fiscal:</strong>
              <span>{stats.totalSum?.toLocaleString('es-BO', { style: 'currency', currency: 'BOB' })} | {stats.totalFiscal?.toLocaleString('es-BO', { style: 'currency', currency: 'BOB' })} </span>
            </div>
            
            <div className="text-gray-700">
              {/* Asumiendo que "ganancia" se refiere al crédito fiscal (IVA) */}
              <strong className="block">Ganancia (3%):</strong>
              <span>{stats.totalVat?.toLocaleString('es-BO', { style: 'currency', currency: 'BOB' })}</span>

            </div>
            <button
              onClick={() => setIsDetailsOpen(prev => !prev)}
              className="absolute -bottom-4 left-1/2 -translate-x-1/2 p-2 bg-gray-100 border rounded-full hover:bg-gray-200 transition-transform"
              title={isDetailsOpen ? "Ocultar detalles" : "Mostrar detalles"}
            >
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                className={`h-3 w-3 text-gray-600 transition-transform duration-300 ${isDetailsOpen ? 'rotate-180' : ''}`} 
                viewBox="0 0 20 20" 
                fill="currentColor"
              >
                <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
            </div>
          

          {/* 👇 5. RENDERIZADO CONDICIONAL DEL DESGLOSE 👇 */}
          {isDetailsOpen &&resumeProject && <ProjectStatsBreakdown project={resumeProject} />}
          </div>
        </div>
         <div className="mt-6 mb-6 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:flex lg:space-x-3 gap-3">
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
          Agregar Batch
        </button>
    
    
        

      </div>
      </div>
       

      {/* Tabla de Facturas (ahora usa la lista unificada) */}
      <InvoiceFiltersComponent
          filters={draftFilters}
          setFilters={setDraftFilters}
          onApply={handleApplyFilters} // Pasa la función para aplicar
          onReset={handleResetFilters} // Pasa la función para limpiar
          batches={resumeProject?.batches || []}
          categories={resumeProject?.categorias || []}
          companies={resumeProject?.empresas||[]}
        />
        
        <div className="mt-6 mb-6 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:flex lg:space-x-3 gap-3">
                      {virtualInvoices &&<button
            onClick={handleDowloadReporte } 
            className="px-2 py-2 font-bold text-white transition-colors bg-green-600 rounded-md hover:bg-blue-green shadow-lg w-full lg:w-auto">
          Descargar Reporte
        </button> }
          { unclompleteInvoices && <button
            onClick={handleCheckFactuas } 
            className="px-2 py-2 font-bold text-white transition-colors bg-yellow-600 rounded-md hover:bg-blue-green shadow-lg w-full lg:w-auto">
          Rehacer Incompletas
        </button> }

        </div>
      <div className="bg-white rounded-lg shadow overflow-x-auto">
        <table className="w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th onClick={() => handleSort('fecha_creacion')} className="cursor-pointer px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"> {sortBy === 'fecha_creacion' && (sortOrder === 'asc' ? '▲' : '▼')}id</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
              <th onClick={() => handleSort('fecha')} className="cursor-pointer px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha {sortBy === 'fecha' && (sortOrder === 'asc' ? '▲' : '▼')}</th>
              <th onClick={() => handleSort('empresa')} className="cursor-pointer px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Empresa {sortBy === 'empresa' && (sortOrder === 'asc' ? '▲' : '▼')}</th>
              <th onClick={() => handleSort('batch')} className=" cursor-pointer px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Lote {sortBy === 'batch' && (sortOrder === 'asc' ? '▲' : '▼')}</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider max-w-xs">
                Estado
              </th>
              <th onClick={() => handleSort('monto_total')} className="cursor-pointer px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Total {sortBy === 'monto_total' && (sortOrder === 'asc' ? '▲' : '▼')}</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">% ganado</th>
              <th onClick={() => handleSort('categoria')} className="cursor-pointer px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Categoria {sortBy === 'categoria' && (sortOrder === 'asc' ? '▲' : '▼')}</th>
              
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {unifiedInvoices.length > 0 ? (
              unifiedInvoices.map((invoice) => (
                <tr key={invoice.id} className={`${getStatusColor(invoice.complete,invoice.status,invoice.special||false)}`}>
                  <td className='px-6 py-4 whitespace-nowrap text-sm text-gray-700'>
                    <a href={invoice.url} target="_blank">{invoice.id}</a>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex justify-end space-x-2">
                        {(invoice.save_pdf === true) ? <button
                            onClick={()=>handleDowload(invoice.id)} 
                          title='descargar factura'
                          className="px-1 py-1 bg-green-100 rounded-md text-green-600 hover:text-green-900">
                            <DownloadIcon/>
                        </button> : <></>}
                        {(invoice.complete !== true) ? <button
                            onClick={()=>handleCheckInvoice(invoice.id,invoice.status)}  
                          title='rehacer factura'
                          className="px-1 py-1 bg-blue-100 rounded-md text-blue-600 hover:text-blue-900">
                            <RefreshIcon/>
                        </button> : <></>}

                        <button 
                          onClick={() => handleOpenEditModal(invoice)} 
                          title='editar factura'
                          className="px-1 py-1 bg-indigo-100 rounded-md text-indigo-600 hover:text-indigo-900">
                            <EditIcon/></button>
                        <button 
                          onClick={() => handleDeleteInvoice(invoice.id, invoice.type)}
                          title='Borrar factura'
                          className="px-1 py-1 bg-red-300 rounded-md text-red-600 hover:text-red-900">
                            <DeleteIcon/></button>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{invoice.date}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 ">{invoice.provider}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{invoice.batch}</td>
                  {/* <td className="px-6 py-4 text-sm font-medium ">
                    <span
                    title={invoice.status} // ✨ Muestra el texto completo al pasar el ratón
                    className={`truncate inline-flex max-w-25 px-2 text-xs leading-5 font-semibold rounded-full `}
                    >
                    {invoice.status}
                    </span>
                  </td> */}

                  <td className="px-6 py-4 text-sm font-medium">
                        {/* Popover se encargará de la lógica de mostrar/ocultar */}
                        <Popover className="relative flex">
                          <PopoverButton
                            as="span" // Lo renderizamos como un span para que no parezca un botón
                            className={`truncate inline-flex max-w-25 px-2 text-xs leading-5 font-semibold rounded-full cursor-pointer focus:outline-none`}
                            // Mantenemos el title para que los usuarios de escritorio sigan teniendo la funcionalidad de hover
                            title={invoice.status}
                          >
                            {invoice.status}
                          </PopoverButton>

                          {/* Este es el panel que aparece al tocar el texto */}
                          <PopoverPanel className="absolute z-10 w-max max-w-xs transform -translate-y-full -top-2 p-2 text-sm font-normal text-white bg-gray-900 rounded-lg shadow-sm">
                            <div className="whitespace-normal break-words">
                              {invoice.status}
                            </div>
                          </PopoverPanel>
                        </Popover>
                      </td>

                  {invoice.special!== true && <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 text-right">{invoice.total_amount.toFixed(2)}</td>}
                  {invoice.special=== true && 
                  <td className="px-6 py-4 text-sm font-medium">
                        {/* Popover se encargará de la lógica de mostrar/ocultar */}
                        <Popover className="relative flex">
                          <PopoverButton
                            as="span" // Lo renderizamos como un span para que no parezca un botón
                            className={`truncate inline-flex max-w-25 px-2 text-xs leading-5 font-semibold rounded-full text-yellow-700 cursor-pointer focus:outline-none`}
                            // Mantenemos el title para que los usuarios de escritorio sigan teniendo la funcionalidad de hover
                            title={`Total: ${invoice.total_amount.toFixed(2)} Fiscal: ${invoice.total_fiscal?.toFixed(2)}`}
                          >
                            {invoice.total_amount.toFixed(2)}
                          </PopoverButton>

                          {/* Este es el panel que aparece al tocar el texto */}
                          <PopoverPanel className="absolute z-10 w-max max-w-xs transform -translate-y-full -top-2 p-2 text-sm font-normal text-white bg-gray-900 rounded-lg shadow-sm">
                            <div className="whitespace-normal break-words">
                              Monto Total : {invoice.total_amount.toFixed(2)}  Monto Fiscal: {invoice.total_fiscal?.toFixed(2)}
                            </div>
                          </PopoverPanel>
                        </Popover>
                      </td>
                  }
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
       <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={setCurrentPage}
          limit={limit}
          onLimitChange={(l) => { setLimit(l); setCurrentPage(1); }}
          totalItems={totalItems}
        />
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
        projectId={resumeProject.id.toString()}
        nitBeneficiario={resumeProject.nit_beneficiario} // Asegúrate que este dato venga en `project`
        onInvoiceCreated={refreshProjectData}
        baches={batchesProyecto}
        categorias={categorias}
      />
      <AddElectronicInvoiceModal
        isOpen={isElectronicInvoiceModalOpen}
        onClose={() => setIsElectronicInvoiceModalOpen(false)}
        projectId={resumeProject.id.toString()}
        onInvoiceCreated={refreshProjectData}
        baches={batchesProyecto}
        categorias={categorias}
      />
      <AddBatchInvoicesModal
          isOpen={isBatchScanModalOpen}
          onClose={() => setIsBatchScanModalOpen(false)}
          projectId={resumeProject.id.toString()}
          onInvoiceCreated={refreshProjectData}
          baches={batchesProyecto}
        categorias={categorias}
        />
        <EditInvoiceModal
        isOpen={isEditModalOpen}
        onClose={handleCloseModals}
        invoice={invoiceToEdit}
        batches={batchesProyecto || []}
        onInvoiceUpdated={() => {
          handleCloseModals();
          refreshProjectData(); // Reutiliza tu función para refrescar datos
        }}
      />
  </>
  );
};

