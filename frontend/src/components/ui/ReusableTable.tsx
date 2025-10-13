// src/components/ui/ReusableTable.tsx
import React from 'react';

interface Column<T> {
  header: string;
  accessor: keyof T;
}

interface ReusableTableProps<T> {
  columns: Column<T>[];
  data: T[];
  renderActions?: (item: T) => React.ReactNode;
  // Nuevas props para ordenamiento
  sortBy: keyof T;
  sortOrder: 'asc' | 'desc';
  onSort: (column: keyof T) => void;
}

export const ReusableTable = <T extends { id: number | string }>({ columns, data, renderActions,sortBy, sortOrder, onSort }: ReusableTableProps<T>) => {
  return (
    <div className="bg-white rounded-lg shadow overflow-x-auto">
      <table className="w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {columns.map((col) => (
              <th
                key={String(col.accessor)}
                onClick={() => onSort(col.accessor)}
                className="px-6 py-2  text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
              >
                <div className="flex items-center">
                  <span>{col.header}</span>
                  {/* Icono de ordenamiento */}
                  {sortBy === col.accessor && (
                    <span className="ml-1">{sortOrder === 'asc' ? '▲' : '▼'}</span>
                  )}
                </div>
              </th>
            ))}
            {renderActions && <th className="px-6 py-3 text-right"></th>}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {data.map((item) => (
            <tr key={item.id} className="hover:bg-gray-50">
              {columns.map((col) => (
                <td key={String(col.accessor)} className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">
                  {String(item[col.accessor])}
                </td>
              ))}
              {renderActions && (
                <td className="px-6 py-3 whitespace-nowrap text-right text-sm font-medium">
                  {renderActions(item)}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};