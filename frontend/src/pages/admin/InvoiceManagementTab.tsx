import { deleteManualInvoice, deleteElectronicInvoice ,dowloadInvoicePdf,checkInvoice} from '../../api/invoiceService';
import { getPaginatedInvoicesAdmin } from '../../api/invoiceService';
import type {InvoiceFiltersType} from '../../api/invoiceService';
import { InvoiceFilters as InvoiceFiltersComponent } from '../../components/ui/InvoiceFilters';
import { Pagination } from '../../components/ui/Pagination'; // Asegúrate de tener este componente

import { getCategories } from '../../api/categoryService';
import { EditInvoiceModal } from '../../components/modals/EditInvoiceModal';

import type { BatchResume, Category, CategoryResume, Company, CompanyResume, ElectronicInvoiceAPI, ManualInvoiceAPI, ProjectAdmin, ProjectInfo,Batch } from '../../types';
import { useEffect, useState } from 'react';
import EditIcon from '../../components/ui/icons/EditIcon';
import DeleteIcon from '../../components/ui/icons/Deleteicon';
import RefreshIcon from '../../components/ui/icons/RefreshIcon';
import DownloadIcon from '../../components/ui/icons/DownloadIcon';
import { getCompanies } from '../../api/companyService';
import { getProjectsall } from '../../api/projectService';
import { Popover, PopoverButton, PopoverPanel } from '@headlessui/react';




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
  project?:ProjectInfo| ProjectAdmin
}
export const InvoiceManagementTab = () => {
  const [unifiedInvoices, setUnifiedInvoices] = useState<UnifiedInvoice[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isEditModalOpen, setIsEditModalOpen] = useState(false);
    const [invoiceToEdit, setInvoiceToEdit] = useState<UnifiedInvoice | null>(null);
    const [batchesToEdit, setBatchesToEdit] = useState<Batch[]| null>([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(0);
    const [totalItems, setTotalItems] = useState(0);
    const [categorias, setCategorias] = useState<CategoryResume[]|null>([]);
    const [empresas, setEmpresas] = useState<CompanyResume[]|null>([]);
    const [proyectos, setProyectos] = useState<ProjectAdmin[]|null>([]);
    const [limit, setLimit] = useState(10);
    const [sortBy, setSortBy] = useState('fecha');
    const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

    const [draftFilters, setDraftFilters] = useState<InvoiceFiltersType>({ tipo_factura: 'todas' });
      // 2. Estado para los filtros que se han aplicado y se usan en la API
      const [activeFilters, setActiveFilters] = useState<InvoiceFiltersType>({ tipo_factura: 'todas' });


      useEffect(()=>{
            getCategories().then(
                response=>{
                    const categoria: Category[] = response
                    const resumenCategorias: CategoryResume[] = categoria.map(categoria => ({
                            categoria_info: categoria
                            }));
                    setCategorias(resumenCategorias)
                }
            ).catch(err => setError((err as Error).message))

            getCompanies().then(
                response=>{
                    const companys: Company[] = response
                    const resumeEmpresas: CompanyResume[] = companys.map(empresa => ({
                            empresa_info: empresa
                            }));
                    setEmpresas(resumeEmpresas)
                }
            ).catch(err => setError((err as Error).message))

            getProjectsall().then(
              response=>{
                setProyectos(response)
              }
            ).catch(err => setError((err as Error).message))

      },[]);
      useEffect(() => {
          
            setLoading(true);
            // La llamada a la API ahora usa los filtros activos
            

            getPaginatedInvoicesAdmin( currentPage, limit, sortBy, sortOrder, activeFilters)
              .then(response => {
                
                const unified = response.items.map((inv: (ElectronicInvoiceAPI|ManualInvoiceAPI)): UnifiedInvoice => {
                  // ... (tu lógica de mapeo para manual y electrónica)
                  // ... (necesitarás una forma de saber si 'inv' es manual o electrónica)
                  const isManual = !('status' in inv); // Asunción simple
                  
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
                    project:inv.proyecto
                    // ... resto de los campos
                  };
                });
                
                setUnifiedInvoices(unified);
                setTotalPages(response.total_pages);
                setTotalItems(response.total);
              })
              .catch(err => setError((err as Error).message))
              .finally(() => setLoading(false));

            
             
          
        }, [ currentPage, limit, sortBy, sortOrder, activeFilters]); // 👈 La dependencia clave



    const fetchInvoices = async () => {
            setLoading(true);
            try {
              const response = await getPaginatedInvoicesAdmin( currentPage, limit, sortBy, sortOrder, activeFilters);
              
              console.log("filtros son ",activeFilters)
              // setInvoicesResponse(response.items)
              const unified = response.items.map((inv: (ElectronicInvoiceAPI|ManualInvoiceAPI)): UnifiedInvoice => {
                // ... (tu lógica de mapeo para manual y electrónica)
                // ... (necesitarás una forma de saber si 'inv' es manual o electrónica)
                const isManual = !('status' in inv); // Asunción simple
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
                  project:inv.proyecto
                  // ... resto de los campos
                };
              });
              
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
        setSortOrder('asc');
      }
    };
  function isBatch(batch: Batch | BatchResume): batch is Batch {
  return (batch as Batch).id !== undefined;
}
   const handleOpenEditModal = (invoice: UnifiedInvoice) => {
      // Solo permite editar facturas electrónicas
  
      
      setInvoiceToEdit(invoice);
        console.log(invoice.project?.batches)
    //   setBatchesToEdit();  


    const batchesAsBatch: Batch[] = (invoice.project?.batches||[])
    .map((batch) => {
      if (isBatch(batch)) {
        // Si es un Batch, asignamos directamente
        return {
          id: batch.id,
          nombre: batch.nombre,
          descripcion: batch.descripcion , // Valor predeterminado si falta
        };
      } 
      else{
        return{
          id: 0,
          nombre: "",
          descripcion: "" , // Valor predeterminado si falta
        };
      }
    
});
      setBatchesToEdit(batchesAsBatch)
      setIsEditModalOpen(true);
    };
  
      const handleCloseModals = () => {
      setIsEditModalOpen(false);
      setInvoiceToEdit(null);
    };
    const refreshProjectData = () => {
      // Esta lógica es para forzar el re-render y la recarga de datos.
      // Una solución más avanzada podría usar un gestor de estado como SWR o React Query.
     
        // Simplemente volvemos a llamar a la función de carga
        // fetchProjectData(projectId);
        fetchInvoices();
     
    };
    if (loading) {
      return <div className="text-center p-8">Cargando proyecto...</div>;
    }
    if (error) {
    return <div className="text-center p-8 bg-red-100 text-red-700 rounded-md">{error}</div>;
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
  const handleDowload=async (numericId:string)=>{
      const numero = numericId.split("-")[1];
      await dowloadInvoicePdf(numero);
  
        
      
    }
    const handleCheckInvoice=async (numericId:string,status:string)=>{
  
      if (status === 'pendiente'){
        return alert ("factura procesandose")
      }
      const numero = numericId.split("-")[1];
      await checkInvoice(numero)
  
        
      
    }
  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Gestión Global de Facturas</h2>
      <InvoiceFiltersComponent
          filters={draftFilters}
          setFilters={setDraftFilters}
          onApply={handleApplyFilters} // Pasa la función para aplicar
          onReset={handleResetFilters} // Pasa la función para limpiar
          batches={[]}
          categories={categorias || []}
          companies={empresas||[]}
          projects={proyectos||[]}

        />
         <div className="bg-white rounded-lg shadow overflow-x-auto">
        <table className="w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th onClick={() => handleSort('fecha_creacion')} className="cursor-pointer px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"> {sortBy === 'fecha_creacion' && (sortOrder === 'asc' ? '▲' : '▼')}id</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
              <th onClick={() => handleSort('fecha')} className="cursor-pointer px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha {sortBy === 'fecha' && (sortOrder === 'asc' ? '▲' : '▼')}</th>
              <th onClick={() => handleSort('empresa')} className="cursor-pointer px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Empresa {sortBy === 'empresa' && (sortOrder === 'asc' ? '▲' : '▼')}</th>
              <th onClick={() => handleSort('batch')} className=" cursor-pointer px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Lote {sortBy === 'batch' && (sortOrder === 'asc' ? '▲' : '▼')}</th>
              <th className="cursor-pointer px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Proyecto </th>
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
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 text-right">    {invoice.project?.nombre}     </td>
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
<EditInvoiceModal
        isOpen={isEditModalOpen}
        onClose={handleCloseModals}
        invoice={invoiceToEdit}
        batches={batchesToEdit||[]}
        onInvoiceUpdated={() => {
          handleCloseModals();
          refreshProjectData(); // Reutiliza tu función para refrescar datos
        }}
      />

      <p className="text-gray-500">Área de trabajo para la tabla de facturas personalizadas.</p>
    </div>
  );
};