// src/components/forms/EditCompanyModal.tsx
import { useState, useEffect, useRef } from 'react';
import type { FormEvent } from 'react';
import { updateUser } from '../../api/userService';
import type { UserProject } from '../../types';
import { useAuth } from '../../hooks/useAuth';


interface EditUserModalProps {
  isOpen: boolean;
  onClose: () => void;
  user: UserProject | null;
  onUserUpdated: () => void;
}
interface User_Model {
  sub: string; // "subject", generalmente el email
  fullName: string; // Asumimos que podrías añadir el nombre al token
  email?:string;
  is_su?:boolean;
}

export const EditUserModal = ({ isOpen, onClose, user, onUserUpdated }: EditUserModalProps) => {
  const [nombre, setNombre] = useState('');
  const { user: currentUser, updateUser: updateAuthContext } = useAuth(); 
  const [error, setError] = useState<string | null>(null);
  const modalRef = useRef<HTMLDivElement>(null);

  // Pre-llena el formulario cuando se selecciona una empresa
  useEffect(() => {
    if (user) {
      setNombre(user.name);
      setError(null);
    }
  }, [user]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!user) return;

    try {
      const response= await updateUser(user.id, { name:nombre });
      if (currentUser?.sub === user.email) {
        console.log(response)
        const newuser:User_Model={
            is_su:response?.is_superuser||currentUser?.is_su,
            email:response?.email||currentUser?.email,
            sub:response?.email||currentUser?.sub,
            fullName:response?.name||currentUser?.fullName,
        }
        updateAuthContext(newuser); // 👈 4. ACTUALIZA EL ESTADO GLOBAL
      }
      onUserUpdated();
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


  if (!isOpen || !user) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-40 flex justify-center items-center">
      <div ref={modalRef} className="bg-white p-6 rounded-lg shadow-xl w-full max-w-lg">
        <h2 className="text-xl font-bold mb-4">Editar Usuario: {user.name}</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700">Nombre</label>
            <input
              id="name"
              type="text"
              value={nombre}
              onChange={e => setNombre(e.target.value)}
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