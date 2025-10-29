// src/pages/admin/tabs/UserManagementTab.tsx
import { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';

import { ReusableTable } from '../../components/ui/ReusableTable';
import { Pagination } from '../../components/ui/Pagination';
import { deleteUser, getUsersPagination } from '../../api/userService'; // Importa tu servicio
import type { UserProject } from '../../types';
import { EditUserModal } from '../../components/modals/EditUserModal';

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
export const UserManagementTab = () => {
  const { user } = useAuth();
  const isSuperUser = user?.is_su === true;

  // Lógica de estado y fetch (similar a CompaniesPage)
  
  const [data, setData] = useState<UserProject[]|null>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [totalItems, setTotalItems] = useState(0);
  const [limit, setLimit] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('id');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [userToEdit, setUserToEdit] = useState<UserProject | null>(null);

  const debouncedSearchTerm = useDebounce(searchTerm, 500);
  const fetchData = async () => {
      setLoading(true);
      const response = await getUsersPagination(currentPage, limit, debouncedSearchTerm, sortBy, sortOrder);
      setData(response.items);
      setTotalPages(response.pages);
      setTotalItems(response.total);
      setLoading(false);
    };
  useEffect(() => {
    
    fetchData();
  }, [currentPage, limit, debouncedSearchTerm, sortBy, sortOrder]);


  const handleSort = (column: keyof UserProject) => {
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
    { header: 'ID', accessor: 'id' as keyof UserProject},
    { header: 'Email', accessor: 'email' as keyof UserProject },
    { header: 'Nombre', accessor: 'name' as keyof UserProject },
  ];

    const handleDelete = async (userid: number) => {
      if (window.confirm('¿Estás seguro de que quieres eliminar este usuari?')) {
        await deleteUser(userid);
        fetchData(); // Recarga los datos
      }
    };

      const handleOpenEditModal = (user: UserProject) => {
        setUserToEdit(user);
        setIsEditModalOpen(true);
      };

  if (!isSuperUser){
    return <div> No tienes permisos</div>
  }
  return (
    <div className="space-y-4">
      <input type="text" placeholder="Buscar usuarios..." value={searchTerm} onChange={e => setSearchTerm(e.target.value)} className="w-full p-2 border rounded-md" />
      {loading ? <p>Cargando...</p> : (
        <>
          <ReusableTable columns={columns} 
                        data={data||[]} 
                        sortBy={sortBy as keyof UserProject} 
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
      <EditUserModal
              isOpen={isEditModalOpen}
              onClose={() => setIsEditModalOpen(false)}
              user={userToEdit}
              onUserUpdated={() => {
                setIsEditModalOpen(false);
                fetchData(); // Refresca la tabla
              }}
            />
    </div>
  );
};