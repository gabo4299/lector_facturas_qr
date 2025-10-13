// src/pages/CompaniesPage.tsx
import { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import {  deleteCategory, getCategoriesPagination } from '../../api/categoryService';
import type { Category } from '../../types';

import { ReusableTable } from '../../components/ui/ReusableTable';
import { Pagination } from '../../components/ui/Pagination';
import { EditCategoryModal } from '../modals/EditCategoryModal';
// import { EditCategoryModal } from '../../components/modals/EditCategoryModal';
// Hook personalizado para "retrasar" la búsqueda mientras el usuario escribe

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

export const TableCategories = () => {
  const { user } = useAuth();
  const isSuperUser = user?.is_su=== true;

  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Estados para la tabla
  

  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [totalItems, setTotalItems] = useState(0);
  const [limit, setLimit] = useState(3); // Límite por página
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearchTerm = useDebounce(searchTerm, 500); // 500ms de retraso
  const [sortBy, setSortBy] = useState('id');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
//   const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [categoryToEdit, setCategoryToEdit] = useState<Category | null>(null);

  const fetchCompanies = async () => {
    setLoading(true);
    try {
      const response = await getCategoriesPagination(currentPage, 
        debouncedSearchTerm,limit,sortBy,sortOrder
      );
      setCategories(response.items);
      setTotalPages(response.pages);
      setTotalItems(response.total);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCompanies();
  }, [currentPage, debouncedSearchTerm, limit, sortBy, sortOrder]); // Se re-ejecuta al cambiar de página o al buscar
//   const handleOpenEditModal = (category: Category) => {
//     setCategoryToEdit(category);
//     setIsEditModalOpen(true);
//   };
  const handleOpenEditModal = (category:Category)=>{
    setCategoryToEdit(category)
    setIsEditModalOpen(true)
  }
  const handleDelete = async (categoryId: number) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar esta categoria?')) {
      await deleteCategory(categoryId);
      fetchCompanies(); // Recarga los datos
    }
  };
    const handleLimitChange = (newLimit: number) => {
    setCurrentPage(1);
    setLimit(newLimit);
  };
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
    { header: 'ID', accessor: 'id' as keyof Category },
    { header: 'Nombre', accessor: 'nombre' as keyof Category },
    { header: 'Descripcion', accessor: 'descripcion' as keyof Category },
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-2">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Categorias</h1>
        
      </div>

      <input
        type="text"
        placeholder="Buscar por Categoria o Descripcion   o id "
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="w-full p-2 border rounded-md"
      />

      {loading && <p>Cargando...</p>}
      {error && <p className="text-red-500">{error}</p>}
      
      {!loading && !error && (
        <>
          <ReusableTable
            columns={columns}
            data={categories}
            sortBy={sortBy as keyof Category}
            sortOrder={sortOrder}
            onSort={handleSort}
            renderActions={isSuperUser ? (category) => (
              <div className="space-x-2">

                { category.nombre !== "Invalidas" && <button onClick={()=>handleOpenEditModal(category)} className="text-indigo-600 hover:text-indigo-900">Editar</button>}
                {category.nombre !== "Invalidas" && <button onClick={() => handleDelete(category.id)} className="text-red-600 hover:text-red-900">Eliminar</button>}
              </div>
            ) : undefined}
          />
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
            limit={limit}
            onLimitChange={handleLimitChange}
            totalItems={totalItems}
            ranges={[3,5,10]}
          />
           {/* <EditCategoryModal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        category={categoryToEdit}
        onCategoryUpdated={() => {
          setIsEditModalOpen(false);
          fetchCompanies(); // Refresca la tabla
        }}
      /> */}
      <EditCategoryModal
              isOpen={isEditModalOpen}
              onClose={() => setIsEditModalOpen(false)}
              category={categoryToEdit}
              onCategoryUpdated={() => {
                setIsEditModalOpen(false);
                fetchCompanies(); // Refresca la tabla
              }}
            />
        </>
      )}
    </div>
  );
};