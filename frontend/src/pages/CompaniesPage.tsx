// src/pages/CompaniesPage.tsx
import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import {  deleteCompany, getCompaniesPagination } from '../api/companyService';
import type { Company } from '../types';

import { ReusableTable } from '../components/ui/ReusableTable';
import { Pagination } from '../components/ui/Pagination';
import { EditCompanyModal } from '../components/modals/EditCompanyModal';
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

export const CompaniesPage = () => {
  const { user } = useAuth();
  const isSuperUser = user?.is_su=== true;

  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Estados para la tabla
  

  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [totalItems, setTotalItems] = useState(0);
  const [limit, setLimit] = useState(10); // Límite por página
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearchTerm = useDebounce(searchTerm, 500); // 500ms de retraso
  const [sortBy, setSortBy] = useState('id');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [companyToEdit, setCompanyToEdit] = useState<Company | null>(null);

  const fetchCompanies = async () => {
    setLoading(true);
    try {
      const response = await getCompaniesPagination(currentPage, 
        debouncedSearchTerm,limit,sortBy,sortOrder
      );
      setCompanies(response.items);
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
  const handleOpenEditModal = (company: Company) => {
    setCompanyToEdit(company);
    setIsEditModalOpen(true);
  };
  const handleDelete = async (companyId: number) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar esta empresa?')) {
      await deleteCompany(companyId);
      fetchCompanies(); // Recarga los datos
    }
  };
    const handleLimitChange = (newLimit: number) => {
    setCurrentPage(1);
    setLimit(newLimit);
  };
  const handleSort = (column: keyof Company) => {
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
    { header: 'ID', accessor: 'id' as keyof Company },
    { header: 'Nombre', accessor: 'nombre' as keyof Company },
    { header: 'NIT', accessor: 'nit' as keyof Company },
    { header: 'Rubro', accessor: 'rubro' as keyof Company },
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-2">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Gestión de Empresas</h1>
        {isSuperUser && (
          <button className="px-4 py-1   font-bold text-white bg-blue-600 rounded-md hover:bg-blue-700">
            Agregar Empresa
          </button>
        )}
      </div>

      <input
        type="text"
        placeholder="Buscar por nombre o NIT..."
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
            data={companies}
            sortBy={sortBy as keyof Company}
            sortOrder={sortOrder}
            onSort={handleSort}
            renderActions={isSuperUser ? (company) => (
              <div className="space-x-2">
                <button onClick={() => handleOpenEditModal(company)} className="text-indigo-600 hover:text-indigo-900">Editar</button>
                <button onClick={() => handleDelete(company.id)} className="text-red-600 hover:text-red-900">Eliminar</button>
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
          />
           <EditCompanyModal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        company={companyToEdit}
        onCompanyUpdated={() => {
          setIsEditModalOpen(false);
          fetchCompanies(); // Refresca la tabla
        }}
      />
        </>
      )}
    </div>
  );
};