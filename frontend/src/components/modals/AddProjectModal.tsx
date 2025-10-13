// src/components/forms/AddProjectModal.tsx
import { useState, useEffect, useRef } from 'react';
import type { FormEvent } from 'react';
import { createProject } from '../../api/projectService';

interface AddProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onProjectCreated: () => void; // Para refrescar la lista de proyectos
}

export const AddProjectModal = ({ isOpen, onClose, onProjectCreated }: AddProjectModalProps) => {
  const [nombre, setNombre] = useState('');
  const [fechaInicio, setFechaInicio] = useState('');
  const [fechaFin, setFechaFin] = useState('');
  const [nitBeneficiario, setNitBeneficiario] = useState('');
  const [error, setError] = useState<string | null>(null);

  const modalRef = useRef<HTMLDivElement>(null);

  // Limpia el formulario cada vez que se abre el modal
  useEffect(() => {
    if (isOpen) {
        const today = new Date();
      const todayString = today.toISOString().split('T')[0];

      // 2. Calculamos la fecha de mañana
      const tomorrow = new Date(today);
      tomorrow.setDate(today.getDate() + 1);
      const tomorrowString = tomorrow.toISOString().split('T')[0];
      setNombre('');
      setFechaInicio(todayString);
      setFechaFin(tomorrowString);
      setNitBeneficiario('');
      setError(null);
    }
  }, [isOpen]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);

    // --- Validación de Datos ---
    if (!nombre || !fechaInicio || !fechaFin || !nitBeneficiario) {
      setError('Todos los campos son obligatorios.');
      return;
    }
    if (new Date(fechaInicio) >= new Date(fechaFin)) {
      setError('La fecha de inicio debe ser anterior a la fecha de fin.');
      return;
    }
    // --- Fin de Validación ---

    try {
      await createProject({
        nombre,
        fecha_inicio: new Date(fechaInicio).toISOString(),
        fecha_fin: new Date(fechaFin).toISOString(),
        nit_beneficiario: nitBeneficiario,
      });
      onProjectCreated(); // Llama a la función para refrescar los datos
      onClose(); // Cierra el modal
    } catch (err) {
      if (err instanceof Error) setError(err.message);
      else setError('Ocurrió un error inesperado');
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

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-40 flex justify-center items-center">
      <div ref={modalRef} className="bg-white p-6 rounded-lg shadow-xl w-full max-w-lg">
        <h2 className="text-xl font-bold mb-4">Agregar Nuevo Proyecto</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="nombre_proyecto" className="block text-sm font-medium text-gray-700">Nombre del Proyecto</label>
            <input id="nombre_proyecto" type="text" value={nombre} onChange={e => setNombre(e.target.value)} className="w-full mt-1 px-3 py-2 border rounded-md shadow-sm border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="fecha_inicio" className="block text-sm font-medium text-gray-700">Fecha de Inicio</label>
              <input id="fecha_inicio" type="date" value={fechaInicio} onChange={e => setFechaInicio(e.target.value)} className="w-full mt-1 px-3 py-2 border rounded-md shadow-sm border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label htmlFor="fecha_fin" className="block text-sm font-medium text-gray-700">Fecha de Fin</label>
              <input id="fecha_fin" type="date" value={fechaFin} onChange={e => setFechaFin(e.target.value)} className="w-full mt-1 px-3 py-2 border rounded-md shadow-sm border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
          </div>
          
          <div>
            <label htmlFor="nit_beneficiario" className="block text-sm font-medium text-gray-700">NIT Beneficiario</label>
            <input id="nit_beneficiario" type="text" value={nitBeneficiario} onChange={e => setNitBeneficiario(e.target.value)} className="w-full mt-1 px-3 py-2 border rounded-md shadow-sm border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>

          {error && <div className="p-3 text-sm text-center text-red-100 text-red-800 rounded-md">{error}</div>}

          <div className="mt-6 flex justify-end space-x-3">
            <button type="button" onClick={onClose} className="px-4 py-2 font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200">Cancelar</button>
            <button type="submit" className="px-4 py-2 font-bold text-white bg-blue-600 rounded-md hover:bg-blue-700">Crear Proyecto</button>
          </div>
        </form>
      </div>
    </div>
  );
};