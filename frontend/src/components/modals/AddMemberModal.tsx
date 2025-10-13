// src/components/modals/AddBatchModal.tsx
import { useState, useRef, useEffect } from 'react';
import type { FormEvent } from 'react';
import { addUserToProject } from '../../api/projectService';

// Definimos las props que recibirá el componente
interface AddMemberModalProps {
  isOpen: boolean;
  onClose: () => void;
  projectId: number;
}

export const AddMemberModal = ({ isOpen, onClose, projectId }: AddMemberModalProps) => {
  const [email, setEmail] = useState('');
  const [rol, setRol] = useState('lector');
  const [error, setError] = useState<string | null>(null);
  const modalRef = useRef<HTMLDivElement>(null);

  // Cierra el modal si se hace clic fuera de él
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (modalRef.current && !modalRef.current.contains(event.target as Node)) {
        onClose();
        setError("");
        setEmail("");
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
      
      await addUserToProject(String(projectId), {email:email,rol:rol});
      onClose(); // Cierra el modal
      setEmail("");

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
        <h2 className="text-xl font-bold mb-4">Agregar Miembro</h2>
        <form onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">Email de usuario</label>
              <input
                id="email" type="text" required value={email} onChange={(e) => setEmail(e.target.value)}
                className="w-full mt-1 px-3 py-2 border rounded-md shadow-sm border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label htmlFor="rol" className="block text-sm font-medium text-gray-700">Rol</label>
              <select id="rol" value={rol || 'lector'} onChange={e => setRol(e.target.value)} className="w-full mt-1 px-3 py-2 border rounded-md shadow-sm border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="lector">Lector</option>
                <option  value="editor">Editor</option>
              </select>

            </div>
          </div>
          {error && <div className="mt-4 text-sm text-center text-red-700">{error}</div>}
          {/* Botones de Acción */}
          <div className="mt-6 flex justify-end space-x-3">
            <button
              type="button"
              onClick={()=>{setError(""); setEmail(""); onClose(); }}
              className="px-4 py-2 font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200"
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-4 py-2 font-bold text-white bg-blue-600 rounded-md hover:bg-blue-700"
            >
              Agregar miembro
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};