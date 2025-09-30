// src/components/modals/AddBatchModal.tsx
import { useState, useRef, useEffect } from 'react';
import type { FormEvent } from 'react';
import { createBatch } from '../../api/projectService';

// Definimos las props que recibirá el componente
interface AddBatchModalProps {
  isOpen: boolean;
  onClose: () => void;
  projectId: string;
  onBatchCreated: () => void; // Función para refrescar los datos en la página principal
}

export const AddBatchModal = ({ isOpen, onClose, projectId, onBatchCreated }: AddBatchModalProps) => {
  const [nombre, setNombre] = useState('');
  const [descripcion, setDescripcion] = useState('');
  const [error, setError] = useState<string | null>(null);

  const modalRef = useRef<HTMLDivElement>(null);

  // Cierra el modal si se hace clic fuera de él
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (modalRef.current && !modalRef.current.contains(event.target as Node)) {
        onClose();
      }
    };
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen, onClose]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    try {
      await createBatch(projectId, nombre, descripcion);
      onBatchCreated(); // Llama a la función para refrescar los datos
      onClose(); // Cierra el modal
    } catch (err) {
      if (err instanceof Error) setError(err.message);
      else setError('Ocurrió un error inesperado.');
    }
  };

  if (!isOpen) {
    return null;
  }

  return (
    // Fondo oscuro semi-transparente (overlay)
    <div className="fixed inset-0 bg-black/40  z-40 flex justify-center items-center">
      {/* Contenedor del Modal */}
      <div ref={modalRef} className="bg-white p-6 rounded-lg shadow-xl w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">Agregar Nuevo Lote</h2>
        <form onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label htmlFor="nombre" className="block text-sm font-medium text-gray-700">Nombre del Lote</label>
              <input
                id="nombre" type="text" required value={nombre} onChange={(e) => setNombre(e.target.value)}
                className="w-full mt-1 px-3 py-2 border rounded-md shadow-sm border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label htmlFor="descripcion" className="block text-sm font-medium text-gray-700">Descripción</label>
              <textarea
                id="descripcion" required value={descripcion} onChange={(e) => setDescripcion(e.target.value)}
                className="w-full mt-1 px-3 py-2 border rounded-md shadow-sm border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={3}
              />
            </div>
          </div>
          {error && <div className="mt-4 text-sm text-center text-red-700">{error}</div>}
          {/* Botones de Acción */}
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
              Agregar Lote
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};