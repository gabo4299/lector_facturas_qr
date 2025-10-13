// src/components/forms/AddCategoryModal.tsx
import { useState, useEffect, useRef } from 'react';
import type { FormEvent } from 'react';
import { createCategory } from '../../api/categoryService';

interface AddCategoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCategoryCreated: () => void; // Para notificar que se creó una categoría
}

export const AddCategoryModal = ({ isOpen, onClose, onCategoryCreated }: AddCategoryModalProps) => {
  const [nombre, setNombre] = useState('');
  const [descripcion, setDescripcion] = useState('');
  const [error, setError] = useState<string | null>(null);
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      setNombre('');
      setDescripcion('');
      setError(null);
    }
  }, [isOpen]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    if (!nombre || !descripcion) {
      setError('Ambos campos son obligatorios.');
      return;
    }
    try {
      await createCategory({ nombre, descripcion });
      onCategoryCreated();
      onClose();
    } catch (err) {
      if (err instanceof Error) setError(err.message);
      else setError('Ocurrió un error inesperado');
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
    <div className="fixed inset-0 bg-black/50 z-40 flex justify-center items-center">
      <div ref={modalRef} className="bg-white p-6 rounded-lg shadow-xl w-full max-w-lg">
        <h2 className="text-xl font-bold mb-4">Agregar Nueva Categoría</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="nombre_categoria" className="block text-sm font-medium text-gray-700">Nombre de la Categoría</label>
            <input
              id="nombre_categoria"
              type="text"
              value={nombre}
              onChange={e => setNombre(e.target.value)}
              className="w-full mt-1 px-3 py-2 border rounded-md shadow-sm border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label htmlFor="detalle_categoria" className="block text-sm font-medium text-gray-700">Detalle (Descripción)</label>
            <textarea
              id="detalle_categoria"
              value={descripcion}
              onChange={e => setDescripcion(e.target.value)}
              className="w-full mt-1 px-3 py-2 border rounded-md shadow-sm border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
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
              Crear Categoría
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};