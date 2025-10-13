// src/components/forms/EditCompanyModal.tsx
import { useState, useEffect, useRef } from 'react';
import type { FormEvent } from 'react';
import { updateCompany } from '../../api/companyService';
import type { Company } from '../../types';

interface EditCompanyModalProps {
  isOpen: boolean;
  onClose: () => void;
  company: Company | null;
  onCompanyUpdated: () => void;
}

export const EditCompanyModal = ({ isOpen, onClose, company, onCompanyUpdated }: EditCompanyModalProps) => {
  const [nombre, setNombre] = useState('');
  const [rubro, setRubro] = useState('');
  const [error, setError] = useState<string | null>(null);
  const modalRef = useRef<HTMLDivElement>(null);

  // Pre-llena el formulario cuando se selecciona una empresa
  useEffect(() => {
    if (company) {
      setNombre(company.nombre);
      setRubro(company.rubro || "");
      setError(null);
    }
  }, [company]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!company) return;

    try {
      await updateCompany(company.id, { nombre, rubro });
      onCompanyUpdated();
      onClose();
    } catch (err) {
      if (err instanceof Error) setError(err.message);
    }
  };
  
  // Lógica para cerrar con clic afuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (modalRef.current && !modalRef.current.contains(event.target as Node)) {
        onClose();
      }
    };
    if (isOpen) document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen, onClose]);


  if (!isOpen || !company) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-40 flex justify-center items-center">
      <div ref={modalRef} className="bg-white p-6 rounded-lg shadow-xl w-full max-w-lg">
        <h2 className="text-xl font-bold mb-4">Editar Empresa: {company.nombre}</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="nombre_empresa" className="block text-sm font-medium text-gray-700">Nombre de la Empresa</label>
            <input
              id="nombre_empresa"
              type="text"
              value={nombre}
              onChange={e => setNombre(e.target.value)}
              className="w-full mt-1 px-3 py-2 border rounded-md shadow-sm border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label htmlFor="rubro_empresa" className="block text-sm font-medium text-gray-700">Rubro</label>
            <input
              id="rubro_empresa"
              type="text"
              value={rubro}
              onChange={e => setRubro(e.target.value)}
              className="w-full mt-1 px-3 py-2 border rounded-md shadow-sm border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          {error && <div className="p-3 text-sm text-center text-red-100 text-red-800 rounded-md">{error}</div>}
          <div className="mt-6 flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200"
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-4 py-2 font-bold text-white bg-blue-600 rounded-md hover:bg-blue-700"
            >
              Guardar Cambios
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};