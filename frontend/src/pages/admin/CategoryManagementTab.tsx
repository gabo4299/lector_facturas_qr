import { useState, useEffect } from 'react';

import { ReusableTable } from '../../components/ui/ReusableTable';
import { Pagination } from '../../components/ui/Pagination';
import { deleteCategory, getCategoriesPagination } from '../../api/categoryService'; // Importa tu servicio
import type { Category } from '../../types';
import { EditCategoryModal } from '../../components/modals/EditCategoryModal';
import { useAuth } from '../../hooks/useAuth';

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
export const CategoryManagementTab = () => {
  const { user } = useAuth();
  const isSuperUser = user?.is_su === true;

  // Lógica de estado y fetch (similar a CompaniesPage)
  
  const [data, setData] = useState<Category[]|null>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [totalItems, setTotalItems] = useState(0);
  const [limit, setLimit] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('id');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [itemToEdit, setItemToEdit] = useState<Category | null>(null);

  const debouncedSearchTerm = useDebounce(searchTerm, 500);
  const fetchData = async () => {
      setLoading(true);
      const response = await getCategoriesPagination(currentPage, debouncedSearchTerm,  limit,sortBy, sortOrder);
      setData(response.items);
      setTotalPages(response.pages);
      setTotalItems(response.total);
      setLoading(false);
    };
  useEffect(() => {
    
    fetchData();
  }, [currentPage, limit, debouncedSearchTerm, sortBy, sortOrder]);


  const handleSort = (column: keyof Category) => {
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
    { header: 'ID', accessor: 'id' as keyof Category},
    { header: 'Nombre', accessor: 'nombre' as keyof Category },
    { header: 'Descripcion', accessor: 'descripcion' as keyof Category },
  ];

    const handleDelete = async (id: number) => {
      if (window.confirm('¿Estás seguro de que quieres eliminar esta categoria?')) {
        await deleteCategory(id);
        fetchData(); // Recarga los datos
      }
    };

      const handleOpenEditModal = (item: Category) => {
        setItemToEdit(item);
        setIsEditModalOpen(true);
      };

  if (!isSuperUser){
    return <div> No tienes permisos</div>
  }
  return (
    <div className="space-y-4">
      <input type="text" placeholder="Buscar categorias..." value={searchTerm} onChange={e => setSearchTerm(e.target.value)} className="w-full p-2 border rounded-md" />
      {loading ? <p>Cargando...</p> : (
        <>
          <ReusableTable columns={columns} 
                        data={data||[]} 
                        sortBy={sortBy as keyof Category} 
                        sortOrder={sortOrder} 
                        onSort={handleSort}
                        renderActions={isSuperUser ? (user) => (
                                        <div className="space-x-2">
                                            <button onClick={() => handleOpenEditModal(user)} className="text-indigo-600 hover:text-indigo-900">Editar</button>
                                            <button onClick={() => handleDelete(user.id)} className="text-red-600 hover:text-red-900">Eliminar</button>
                                        </div>
                                        ) : undefined} />
          <Pagination currentPage={currentPage} totalPages={totalPages} onPageChange={setCurrentPage} limit={limit} onLimitChange={(l) => {setLimit(l); setCurrentPage(1);}} totalItems={totalItems} />
        </>
      )}
      <EditCategoryModal
              isOpen={isEditModalOpen}
              onClose={() => setIsEditModalOpen(false)}
              category={itemToEdit}
              onCategoryUpdated={() => {
                setIsEditModalOpen(false);
                fetchData(); // Refresca la tabla
              }}
            />
    </div>
  );
};