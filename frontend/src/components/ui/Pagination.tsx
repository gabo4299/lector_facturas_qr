// src/components/ui/Pagination.tsx
interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  limit: number;
  onLimitChange: (limit: number) => void;
  totalItems: number;
  ranges?:number[]
}

export const Pagination = ({ currentPage, totalPages, onPageChange,limit,onLimitChange,totalItems,ranges=[10,25,50] }: PaginationProps) => {
   if (totalItems === 0) {
    return null;
  }

  return (
    
    <div className="flex flex-col sm:flex-row justify-between items-center space-y-2 sm:space-y-0 mt-4 text-sm">
      {/* Selector de Límite */}
      <div className="flex items-center space-x-2">
        <span>Mostrar</span>
        <select
          value={limit}
          onChange={(e) => onLimitChange(Number(e.target.value))}
          className="p-1 border rounded-md"
        >
          {ranges.map((r)=>(
            <option key={r} value={r}>{r}</option>
          ))}
          
        </select>
        <span>resultados</span>
         {(limit >= totalItems )?  <span> {totalItems} de {totalItems} </span>:<span> {limit} de {totalItems}</span>}
      </div>
      
      {/* Controles de Paginación */}
      <div className="flex items-center space-x-2">
        <button onClick={() => onPageChange(currentPage - 1)} disabled={currentPage === 1} className="px-3 py-1 border rounded-md bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
          Anterior
        </button>
        <span className="font-medium">
          Página {currentPage} de {totalPages}
        </span>
        <button onClick={() => onPageChange(currentPage + 1)} disabled={currentPage === totalPages} className="px-3 py-1 border rounded-md bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
          Siguiente
        </button>
      </div>
    </div>
  );
};