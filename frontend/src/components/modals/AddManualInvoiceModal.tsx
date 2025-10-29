// src/components/forms/AddManualInvoiceModal.tsx
import { useState, useEffect, useRef } from 'react';
import type { FormEvent, KeyboardEvent } from 'react';
import { getCompanies } from '../../api/companyService';
import type {Company}from '../../types';
import { createManualInvoice } from '../../api/invoiceService';
import { getBatchesForProject, getCategoriesForProject } from '../../api/projectService';
interface AddManualInvoiceModalProps {
  isOpen: boolean;
  onClose: () => void;
  projectId: string;
  nitBeneficiario: string;
  onInvoiceCreated: () => void;
}
interface BatchOrCategory {
  id: number;
  nombre: string;
}

export const AddManualInvoiceModal = ({ isOpen, onClose, projectId, nitBeneficiario, onInvoiceCreated }: AddManualInvoiceModalProps) => {
  const [montoTotal, setMontoTotal] = useState('');
  const [fecha, setFecha] = useState(new Date().toISOString().split('T')[0]);
  const [nombreEmpresa, setNombreEmpresa] = useState('');
  const [nitEmisor, setNitEmisor] = useState('');
  
  const [empresas, setEmpresas] = useState<Company[]>([]);
  const [sugerencias, setSugerencias] = useState<Company[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
  const [activeIndex, setActiveIndex] = useState(-1); // Para navegación con teclado
  const [error, setError] = useState<string | null>(null);

  const modalRef = useRef<HTMLDivElement>(null);

  const [selectedBatch, setSelectedBatch] = useState<number | undefined>();
  const [selectedCategory, setSelectedCategory] = useState<number | undefined>();

  const [batches, setBatches] = useState<BatchOrCategory[]>([]);
    const [categories, setCategories] = useState<BatchOrCategory[]>([]);
    
  useEffect(() => {
    if (isOpen) {
      const fetchData = async () => {
              setBatches(await getBatchesForProject(projectId));
              setCategories(await getCategoriesForProject());
            };
            fetchData();
      const fetchEmpresas = async () => setEmpresas(await getCompanies());
      fetchEmpresas();
      // Resetear formulario al abrir
      setMontoTotal('');
      setFecha(new Date().toISOString().split('T')[0]);
      setNombreEmpresa('');
      setNitEmisor('');
      setSelectedCompany(null);
      setError(null);
      setSugerencias([]);
    }
  }, [isOpen]);
  
  const handleNombreChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setNombreEmpresa(value);
    setSelectedCompany(null); // Deseleccionar si el usuario escribe
    setNitEmisor(''); // Limpiar NIT si el usuario escribe

    if (value.length > 1) {
      setSugerencias(empresas.filter(emp => emp.nombre.toLowerCase().includes(value.toLowerCase())));
    } else {
      setSugerencias([]);
    }
  };

  const handleSugerenciaClick = (empresa: Company) => {
    setNombreEmpresa(empresa.nombre);
    setNitEmisor(empresa.nit!);
    setSelectedCompany(empresa); // Guarda la empresa seleccionada
    setSugerencias([]);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (sugerencias.length === 0) return;

    if (e.key === 'ArrowDown') {
      setActiveIndex(prev => (prev + 1) % sugerencias.length);
    } else if (e.key === 'ArrowUp') {
      setActiveIndex(prev => (prev - 1 + sugerencias.length) % sugerencias.length);
    } else if (e.key === 'Enter') {
      e.preventDefault(); // Previene el submit del formulario
      if (activeIndex >= 0) {
        handleSugerenciaClick(sugerencias[activeIndex]);
      }
    } else if (e.key === 'Escape') {
      setSugerencias([]);
    }
  };
  
  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    try {
      await createManualInvoice({
        proyecto_id: projectId,
        Nit_Beneficiario: nitBeneficiario,
        monto_total: parseFloat(montoTotal),
        fecha,
        nit_emisor: nitEmisor,
        // Solo envía el nombre si es una empresa nueva (no seleccionada de la lista)
        nombre_empresa: selectedCompany ? undefined : nombreEmpresa,
        batch_id: selectedBatch,
        category_id: selectedCategory
      });
      onInvoiceCreated();
      onClose();
    } catch (err) {
      if (err instanceof Error) setError(err.message);
    }
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (modalRef.current && !modalRef.current.contains(event.target as Node)) {
        onClose();
      }
    };
    if (isOpen) document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen, onClose]);


  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/30 z-40 flex justify-center items-center">
      <div ref={modalRef} className="bg-white p-6 rounded-lg shadow-xl w-full max-w-lg">
        <h2 className="text-xl font-bold mb-4">Agregar Factura Manual</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
             <div>
              <label htmlFor="monto_total" className="block text-sm font-medium text-gray-700">Monto Total</label>
              <input id="monto_total" type="number" step="0.01" required value={montoTotal} onChange={e => setMontoTotal(e.target.value)} className="w-full mt-1 px-3 py-2 border rounded-md shadow-sm border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label htmlFor="fecha" className="block text-sm font-medium text-gray-700">Fecha</label>
              <input id="fecha" type="date" required value={fecha} onChange={e => setFecha(e.target.value)} className="w-full mt-1 px-3 py-2 border rounded-md shadow-sm border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
          </div>

          <div className="relative">
            <label htmlFor="nombre_empresa" className="block text-sm font-medium text-gray-700">Nombre de Empresa</label>
            <input
              id="nombre_empresa" type="text" required autoComplete="off"
              value={nombreEmpresa}
              onChange={handleNombreChange}
              onKeyDown={handleKeyDown}
              className="w-full mt-1 px-3 py-2 border rounded-md shadow-sm border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {sugerencias.length > 0 && (
              <ul className="absolute z-10 w-full bg-white border border-gray-300 rounded-md mt-1 max-h-40 overflow-y-auto shadow-lg">
                {sugerencias.map((sug, index) => (
                  <li
                    key={sug.id}
                    onClick={() => handleSugerenciaClick(sug)}
                    className={`p-2 cursor-pointer ${index === activeIndex ? 'bg-gray-200' : 'hover:bg-gray-100'}`}
                  >
                    {sug.nombre} <span className="text-gray-500">({sug.nit})</span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* El input de NIT ahora es condicional y puede estar deshabilitado */}
          
            <div>
              <label htmlFor="nit_emisor" className="block text-sm font-medium text-gray-700">NIT Emisor</label>
              <input
                id="nit_emisor" type="text" required
                value={nitEmisor}
                onChange={e => setNitEmisor(e.target.value)}
                disabled={!!selectedCompany} // Deshabilitado si se seleccionó una empresa
                className="w-full mt-1 px-3 py-2 border rounded-md shadow-sm border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
              />
            </div>
            <div className="grid grid-cols-2 gap-4 mb-4">
            <select 
              value={selectedBatch || ''} 
              onChange={e => setSelectedBatch(Number(e.target.value))} 
              className="w-full px-3 py-2 border rounded-md shadow-sm border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Seleccionar Lote</option>
              {batches.map(b => <option key={b.id} value={b.id}>{b.nombre}</option>)}
            </select>
            <select 
              value={selectedCategory || ''} 
              onChange={e => setSelectedCategory(Number(e.target.value))} 
              className="w-full px-3 py-2 border rounded-md shadow-sm border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Seleccionar Categoría</option>
              {categories.map(c => <option key={c.id} value={c.id}>{c.nombre}</option>)}
            </select>
          </div>

          {error && <div className="mt-4 text-sm text-center text-red-700">{error}</div>}
          <div className="mt-6 flex justify-end space-x-3">
            <button type="button" onClick={onClose} className="px-4 py-2 font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200">Cancelar</button>
            <button type="submit" className="px-4 py-2 font-bold text-white bg-blue-600 rounded-md hover:bg-blue-700">Agregar Factura</button>
          </div>
        </form>
      </div>
    </div>
  );
};