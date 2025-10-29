// src/components/projects/InvoiceFilters.tsx
import { useEffect, useState } from 'react';
import type { InvoiceFiltersType } from '../../api/invoiceService';

import type {Batch,Company, BatchResume,Category,CategoryResume,CompanyResume, ProjectAdmin, ProjectInfo} from '../../types'
import { SearchableSelect } from './SearchableSelect';
interface FiltersProps {
  filters: InvoiceFiltersType;
  setFilters: React.Dispatch<React.SetStateAction<InvoiceFiltersType>>;
  onApply: () => void; // Nueva prop para aplicar
  onReset: () => void;  // Nueva prop para limpiar
  batches?: BatchResume[];
  categories?: CategoryResume[];
  companies?:CompanyResume[]
  projects?:ProjectAdmin[]|ProjectInfo[]
}

export const InvoiceFilters = ({ filters, setFilters,onApply, onReset, batches, categories,companies,projects }: FiltersProps) => {
  const [categoriesList,setCategoriesList]=useState<Category[] | null>([]);
  const [companiesList,setCompaniesList]=useState<Company[] | null>([]);
  const [batchesList,setBatchesList]=useState<Batch[] | null>([]);
  
  useEffect(() => {
    if (categories && categories.length > 0) {
      const extractedCategories = categories.map(resume => resume.categoria_info);
      setCategoriesList(extractedCategories);
    }

  }, [categories])

    useEffect(() => {
    if (companies && companies.length > 0) {
      const extractedCategories = companies.map(resume => resume.empresa_info);
      setCompaniesList(extractedCategories);
    }

  }, [companies])

    useEffect(() => {
    if (batches && batches.length > 0) {
      const extractedCategories = batches.map(resume => resume.batch_info);
      setBatchesList(extractedCategories);
    }

  }, [batches])


  
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;

    let finalValue: unknown = value;
    if (value === 'true') {
      finalValue = true;
    } else if (value === 'false') {
      finalValue = false;
    }
    else if (value === '') {
      finalValue = undefined;
    }
    else if (type === 'number' || name === 'categoria_id' || name === 'empresa_id') {
      finalValue = Number(value);
    }else {
      finalValue = value; // Para inputs de texto normales
    }
    setFilters(prev => ({ ...prev, [name]: finalValue }));
  };

  const handleCategoryChange = (category: { id: number; nombre: string } | null) => {
    setFilters(prev => ({ ...prev, categoria_id: category?.id }));
  };

    const handleCompanieChange = (company: { id: number; nombre: string } | null) => {
    setFilters(prev => ({ ...prev, empresa_id: company?.id }));
  };

     const handleProjectChange = (project: { id: number; nombre: string } | null) => {
    setFilters(prev => ({ ...prev, proyecto_id: project?.id }));
  };

      const handleBatchChange = (batch: { id: number; nombre: string } | null) => {
    setFilters(prev => ({ ...prev, batch_id: batch?.id }));
  };

  return (
    <details className="bg-gray-50 border rounded-lg p-4 mb-4">
      <summary className="font-semibold cursor-pointer">Filtros de Búsqueda</summary>
      <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 text-sm">
        {/* Tipo de Factura */}
        <div>
          <label>Tipo</label>
          <select name="tipo_factura" value={filters.tipo_factura} onChange={handleInputChange} className="w-full mt-1 p-2 border rounded-md">
            <option value="todas">Todas</option>
            <option value="manual">Manual</option>
            <option value="electronica">Electrónica</option>
          </select>
        </div>
        {/* Rango de Fechas */}
        <div>
          <label>Fecha Inicio</label>
          <input type="date" name="fecha_inicio" value={filters.fecha_inicio} onChange={handleInputChange} className="w-full mt-1 p-2 border rounded-md" />
        </div>
        <div>
          <label>Fecha Fin</label>
          <input type="date" name="fecha_fin" value={filters.fecha_fin} onChange={handleInputChange} className="w-full mt-1 p-2 border rounded-md" />
        </div>
        {/* Rango de Montos */}
        <div>
          <label>Monto Mín.</label>
          <input type="number" name="monto_min" value={filters.monto_min} onChange={handleInputChange} className="w-full mt-1 p-2 border rounded-md" />
        </div>
        <div>
          <label>Monto Máx.</label>
          <input type="number" name="monto_max" value={filters.monto_max} onChange={handleInputChange} className="w-full mt-1 p-2 border rounded-md" />
        </div>
        {/* Categorías y Lotes */}
        {(categoriesList && categoriesList?.length > 0 )&& 
        <div>
          <label>Categoría</label>
          {/* <select name="categoria_id" value={filters.categoria_id} onChange={handleInputChange} className="w-full mt-1 p-2 border rounded-md">
            <option value="">Todas</option>
            {categories?.map(cat => <option key={cat.categoria_info.id} value={cat.categoria_info.id}>{cat.categoria_info.nombre}</option>)}
          </select> */}
          <SearchableSelect
            items={categoriesList||[]}
            placeholder="Buscar categoría..."
            selected={categoriesList?.find(c => c.id === filters.categoria_id) || null}
            onChange={handleCategoryChange}
          />
        </div>}

        {(batchesList && batchesList?.length > 0 )&& 
          <div>
          <label>Lote</label>
          <SearchableSelect
            items={batchesList||[]}
            placeholder="Buscar lotes..."
            selected={batchesList?.find(c => c.id === filters.batch_id) || null}
            onChange={handleBatchChange}
          />
          {/* <select name="batch_id" value={filters.batch_id} onChange={handleInputChange} className="w-full mt-1 p-2 border rounded-md">
            <option value="">Todos</option>
            {batches?.map(cat => <option key={cat.batch_info.id} value={cat.batch_info.id}>{cat.batch_info.nombre}</option>)}
          </select> */}
        </div>}


        {(companiesList && companiesList?.length > 0 )&& 
          <div>
          <label>Empresa</label>
          <SearchableSelect
            items={companiesList||[]}
            placeholder="Buscar empresas..."
            selected={companiesList?.find(c => c.id === filters.empresa_id) || null}
            onChange={handleCompanieChange}
          />
        </div>}

        {(projects && projects?.length > 0 )&& 
        <div>
          <label>Proyectos</label>
          {/* <select name="categoria_id" value={filters.categoria_id} onChange={handleInputChange} className="w-full mt-1 p-2 border rounded-md">
            <option value="">Todas</option>
            {categories?.map(cat => <option key={cat.categoria_info.id} value={cat.categoria_info.id}>{cat.categoria_info.nombre}</option>)}
          </select> */}
          <SearchableSelect
            items={projects||[]}
            placeholder="Buscar proyectos..."
            selected={projects?.find(c => c.id === filters.proyecto_id) || null}
            onChange={handleProjectChange}
          />
        </div>}

        {/* Aquí iría un selector para empresa_id si lo necesitas */}
        
        {/* Filtros para Electrónicas */}

        <div>
              <label htmlFor="factura_virtual" className="block text-sm font-medium text-gray-700">Facturas Virtuales</label>
              <select
                id="factura_virtual"
                name="factura_virtual"
                value={String(filters.factura_virtual ?? '')}
                onChange={handleInputChange}
                className="w-full mt-1 p-2 border rounded-md"
              >
                <option value="">Todas</option>
                <option value="true">Virtuales</option>
                <option value="false">Fisicas</option>
              </select>
            </div>    
        {filters.tipo_factura === 'electronica' && (
          <>
            {/* Selector para 'complete' */}
            <div>
              <label htmlFor="complete" className="block text-sm font-medium text-gray-700">Estado Completado</label>
              <select
                id="complete"
                name="complete"
                value={String(filters.complete ?? '')} // Convierte undefined a '', y booleans a "true"/"false"
                onChange={handleInputChange}
                className="w-full mt-1 p-2 border rounded-md"
              >
                <option value="">Todas</option>
                <option value="true">Completadas</option>
                <option value="false">Incompletas</option>
              </select>
            </div>

            {/* Selector para 'factura_especial' */}
            <div>
              <label htmlFor="factura_especial" className="block text-sm font-medium text-gray-700">Tipo Especial</label>
              <select
                id="factura_especial"
                name="factura_especial"
                value={String(filters.factura_especial ?? '')}
                onChange={handleInputChange}
                className="w-full mt-1 p-2 border rounded-md"
              >
                <option value="">Todas</option>
                <option value="true">Especiales</option>
                <option value="false">No especiales</option>
              </select>
            </div>

            
          </>
        )}
      </div>
      <div className="mt-4 pt-4 border-t flex justify-end space-x-3">
        <button
          onClick={onReset}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
        >
          Limpiar Filtros
        </button>
        <button
          onClick={onApply}
          className="px-4 py-2 text-sm font-bold text-white bg-blue-600 rounded-md hover:bg-blue-700"
        >
          Aplicar Filtros
        </button>
        </div>
    </details>
  );
};