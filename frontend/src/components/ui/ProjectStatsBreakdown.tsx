// src/components/projects/ProjectStatsBreakdown.tsx
import { useState, useMemo, useEffect } from 'react';
import { SearchableSelect } from '../ui/SearchableSelect'; // Reutilizamos el selector con búsqueda
import type { ProjectResume, CompanyResume, BatchResume, CategoryResume, Company, Batch, Category } from '../../types'; // Importa tus tipos

interface ProjectStatsBreakdownProps {
  project: ProjectResume;
}

export const ProjectStatsBreakdown = ({ project }: ProjectStatsBreakdownProps) => {
  // Estados para mantener el item seleccionado de cada tipo
  const [selectedCompany, setSelectedCompany] = useState<CompanyResume | null>(null);
  const [selectedBatch, setSelectedBatch] = useState<BatchResume | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<CategoryResume | null>(null);

  // Calcula la empresa, lote y categoría con mayor gasto usando useMemo para eficiencia
  const topSpenders = useMemo(() => {
    const topCompany = [...(project.empresas || [])].sort((a, b) => b.monto_total_empresa! - a.monto_total_empresa!)[0] || null;
    const topBatch = [...(project.batches || [])].sort((a, b) => b.monto_total_batch! - a.monto_total_batch!)[0] || null;
    const topCategory = [...(project.categorias || [])].sort((a, b) => b.monto_total_categoria! - a.monto_total_categoria!)[0] || null;
    return { topCompany, topBatch, topCategory };
  }, [project]);

  // Establece los "top spenders" como la selección inicial
  useEffect(() => {
    setSelectedCompany(topSpenders.topCompany);
    setSelectedBatch(topSpenders.topBatch);
    setSelectedCategory(topSpenders.topCategory);
  }, [topSpenders]);

  // Transforma los datos para que sean compatibles con SearchableSelect
  const companyItems = project.empresas?.map(c => ({ id: c.empresa_info.id, nombre: c.empresa_info.nombre,extraData:c.monto_total_empresa?.toLocaleString('es-BO', { style: 'currency', currency: 'BOB' }) })) || [];
  const batchItems = project.batches?.map(b => ({ id: b.batch_info.id, nombre: b.batch_info.nombre,extraData:b.monto_total_batch?.toLocaleString('es-BO', { style: 'currency', currency: 'BOB' }) })) || [];
  const categoryItems = project.categorias?.map(c => ({ id: c.categoria_info.id, nombre: c.categoria_info.nombre ,extraData:c.monto_total_categoria?.toLocaleString('es-BO', { style: 'currency', currency: 'BOB' })})) || [];

  return (
    <div className="mt-8 p-4 bg-gray-100 rounded-lg border border-gray-200 shadow-sm animate-fade-in-down">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Sección de Empresas */}
        {companyItems.length > 0 &&<StatCard
          title="Análisis por Empresa"
          totalCount={companyItems.length}
          items={companyItems}
          selectedItem={selectedCompany?.empresa_info}
          onSelectChange={(item) => setSelectedCompany(project.empresas?.find(c => c.empresa_info.id === item?.id) || null)}
          stats={{
            'Monto Total': selectedCompany?.monto_total_empresa,
            'Ganancia': (selectedCompany?.monto_total_empresa||0) * 0.03,
            'F. Manuales': selectedCompany?.cantidad_manuales,
            'F. Electrónicas': selectedCompany?.cantidad_electronicas,
          }}
        />}

        {/* Sección de Lotes */}
        {batchItems.length > 0 &&<StatCard
          title="Análisis por Lote"
          totalCount={batchItems.length}
          items={batchItems}
          selectedItem={selectedBatch?.batch_info}
          onSelectChange={(item) => setSelectedBatch(project.batches?.find(b => b.batch_info.id === item?.id) || null)}
          stats={{
            'Monto Total': selectedBatch?.monto_total_batch,
            'Ganancia': (selectedBatch?.monto_total_batch||0) *0.03,
            'F. Manuales': selectedBatch?.cantidad_manuales,
            'F. Electrónicas': selectedBatch?.cantidad_electronicas,
          }}
        />}

        {/* Sección de Categorías */}
        {categoryItems.length > 0 && <StatCard
          title="Análisis por Categoría"
          totalCount={categoryItems.length}
          items={categoryItems}
          selectedItem={selectedCategory?.categoria_info}
          onSelectChange={(item) => setSelectedCategory(project.categorias?.find(c => c.categoria_info.id === item?.id) || null)}
          stats={{
            'Monto Total': selectedCategory?.monto_total_categoria,
            'Ganancia': (selectedCategory?.monto_total_categoria||0) * 0.03,
            'F. Manuales': selectedCategory?.cantidad_manuales,
            'F. Electrónicas': selectedCategory?.cantidad_electronicas,
          }}
        />}
      </div>
    </div>
  );
};

// Componente auxiliar para no repetir código

interface StatCardProps {
  title: string;
  totalCount: number;
  items: (Company[]| Batch[] | Category[]|{ id: number; nombre: string }[]);
  selectedItem: Company | Batch | Category | null | undefined;
  onSelectChange: (item: { id: number; nombre: string } | null) => void;
  stats: { [key: string]: number | undefined };
}
const StatCard = ({ title, totalCount, items, selectedItem, onSelectChange, stats }: StatCardProps) => (
  <div className="p-4 border rounded-md">
    <h3 className="font-semibold text-gray-700">{title}</h3>
    <p className="text-xs text-gray-500 mb-2">
  Total: <span className="font-bold text-gray-800">{totalCount}</span>
</p>
    <SearchableSelect
      items={items}
      selected={selectedItem||null}
      onChange={onSelectChange}
      placeholder={`Buscar ${title.split(' ')[2].toLowerCase()}...`}
    />
    {selectedItem && (
      <div className="mt-3 text-sm space-y-1">
        {Object.entries(stats).map(([key, value]) => (
          <div key={key} className="flex justify-between">
            <span className="text-gray-600">{key}:</span>
            <span className={`font-medium ${key.includes('Ganancia') ?'text-green-00' :'text-gray-800'}`}>
              {typeof value === 'number' && (key.includes('Monto')||key.includes('Ganancia')) ? value.toLocaleString('es-BO', { style: 'currency', currency: 'BOB' }) : value}
              
            </span>
          </div>
        ))}
      </div>
    )}
  </div>
);