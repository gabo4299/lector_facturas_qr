import { useState, useEffect } from 'react';

import { ReusableTable } from '../../components/ui/ReusableTable';
import { Pagination } from '../../components/ui/Pagination';
import { deleteProject,getPaginatedProjects  } from '../../api/projectService'; // Importa tu servicio
import type { ProjectAdmin } from '../../types';
import { EditProjectModal } from '../../components/modals/editProjectModal';
import { useAuth } from '../../hooks/useAuth';
import { AddMemberModal } from '../../components/modals/AddMemberModal';

const useDebounce = (value: string, delay: number) => {
  const [debouncedValue, setDebouncedValue] = useState(value);
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);
    return () => clearTimeout(handler);
  }, [value, delay]);
  return debouncedValue;
};
export const ProjectManagementTab = () => {
  const { user } = useAuth();
  const isSuperUser = user?.is_su === true;

  // Lógica de estado y fetch (similar a CompaniesPage)
  
  const [data, setData] = useState<ProjectAdmin[]|null>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [totalItems, setTotalItems] = useState(0);
  const [limit, setLimit] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('id');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [isAddMemberModalOpen, setIsAddMemberModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [itemToEdit, setItemToEdit] = useState<ProjectAdmin | null>(null);

  const debouncedSearchTerm = useDebounce(searchTerm, 500);
  const fetchData = async () => {
      setLoading(true);
      const response = await getPaginatedProjects(currentPage,   limit,debouncedSearchTerm,sortBy, sortOrder);
      setData(response.items);
      setTotalPages(response.pages);
      setTotalItems(response.total);
      setLoading(false);
    };
  useEffect(() => {
    
    fetchData();
  }, [currentPage, limit, debouncedSearchTerm, sortBy, sortOrder]);


  const handleSort = (column: keyof ProjectAdmin) => {
      if (sortBy === column) {
        // Si ya se está ordenando por esta columna, invierte el orden
        setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
      } else {
        // Si es una nueva columna, ordena por ella de forma ascendente
        setSortBy(column);
        setSortOrder('asc');
      }
    };
  
  const columns = [
    { header: 'ID', accessor: 'id' as keyof ProjectAdmin},
    { header: 'Nombre', accessor: 'nombre' as keyof ProjectAdmin },
    { header: 'Nit', accessor: 'nit_beneficiario' as keyof ProjectAdmin },
    { header: 'Fecha minima', 
      accessor: 'fecha_inicio' as keyof ProjectAdmin,
      render: (item: ProjectAdmin) => 
        new Date(item.fecha_inicio).toLocaleDateString('es-BO') },
    { header: 'Fecha Maxima', accessor: 'fecha_fin' as keyof ProjectAdmin,
        render: (item: ProjectAdmin) => 
        new Date(item.fecha_fin).toLocaleDateString('es-BO') 
     },
    { header: 'Cantidad Facturas', accessor: 'total_facturas' as keyof ProjectAdmin },
    

    {
      header: 'Monto Total',
      accessor: 'suma_total_facturas' as keyof ProjectAdmin,
      render: (item: ProjectAdmin) => 
        item.suma_total_facturas?.toLocaleString('es-BO', { style: 'currency', currency: 'BOB' })
    },
    {
      header: 'Propietario',
      accessor: 'propietario' as keyof ProjectAdmin,
      render: (item: ProjectAdmin) => 
        item.propietario?.email || 'N/A' // Usamos optional chaining por si no existe
    },
  ];

    const handleDelete = async (id: number) => {
      if (window.confirm('¿Estás seguro de que quieres eliminar esta categoria?')) {
        await deleteProject(String(id));
        fetchData(); // Recarga los datos
      }
    };

      const handleOpenEditModal = (item: ProjectAdmin) => {
        setItemToEdit(item);
        setIsEditModalOpen(true);
      };

      const handleOpenAddUserModal = (item:ProjectAdmin)=>{
        setItemToEdit(item);
        setIsAddMemberModalOpen(true);
      }

  if (!isSuperUser){
    return <div> No tienes permisos</div>
  }
  return (
    <div className="space-y-4">
      <input type="text" placeholder="Buscar por nit o nombre..." value={searchTerm} onChange={e => setSearchTerm(e.target.value)} className="w-full p-2 border rounded-md" />
      {loading ? <p>Cargando...</p> : (
        <>
          <ReusableTable columns={columns} 
                        data={data||[]} 
                        sortBy={sortBy as keyof ProjectAdmin} 
                        sortOrder={sortOrder} 
                        onSort={handleSort}
                        renderActions={isSuperUser ? (user) => (
                                        <div className="space-x-2">
                                            <button 
                                            onClick={() => handleOpenAddUserModal(user)}
                                            className="p-2 rounded-full hover:bg-gray-100 text-gray-500 hover:text-gray-700"
                                            title="Agregar colaborador"
                                            >
                                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                                <path d="M8 9a3 3 0 100-6 3 3 0 000 6zM8 11a6 6 0 016 6H2a6 6 0 016-6zM16 11a1 1 0 10-2 0v1h-1a1 1 0 100 2h1v1a1 1 0 102 0v-1h1a1 1 0 100-2h-1v-1z" />
                                            </svg>
                                            </button>
                                            <button onClick={() => handleOpenEditModal(user)} className="text-indigo-600 hover:text-indigo-900">Editar</button>
                                            <button onClick={() => handleDelete(user.id)} className="text-red-600 hover:text-red-900">Eliminar</button>
                                            
                                        </div>
                                        ) : undefined} />
          <Pagination currentPage={currentPage} totalPages={totalPages} onPageChange={setCurrentPage} limit={limit} onLimitChange={(l) => {setLimit(l); setCurrentPage(1);}} totalItems={totalItems} />
        </>
      )}
      <EditProjectModal
              isOpen={isEditModalOpen}
              onClose={() => setIsEditModalOpen(false)}
              project={itemToEdit}
              onProjectUpdated={() => {
                setIsEditModalOpen(false);
                fetchData(); // Refresca la tabla
              }}
            />
            <AddMemberModal
                        isOpen={isAddMemberModalOpen}
                        onClose={() => setIsAddMemberModalOpen(false)}
                        projectId={itemToEdit?.id||0}
                      />
    </div>
  );
};