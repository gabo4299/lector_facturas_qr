// src/components/forms/EditProjectModal.tsx
import { useState, useEffect, useRef } from 'react';
import type { FormEvent, ChangeEvent } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { updateProject, updateCollaboratorRole,deleteCollaborator  } from '../../api/projectService';
import type { ProjectInfo,UserProject,ProjectAdmin } from '../../types'; // Importa tus tipos

interface EditProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  project: ProjectInfo|ProjectAdmin | null;
  onProjectUpdated: () => void;
}

export const EditProjectModal = ({ isOpen, onClose, project, onProjectUpdated }: EditProjectModalProps) => {
  const { user: currentUser } = useAuth(); // Obtiene el usuario logueado desde el contexto
  
  // Estados para el formulario de edición del proyecto
  const [nombre, setNombre] = useState('');
  const [fechaInicio, setFechaInicio] = useState('');
  const [fechaFin, setFechaFin] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const modalRef = useRef<HTMLDivElement>(null);
  const isOwner = currentUser?.sub === project?.propietario?.email;

  // Pre-llena el formulario cuando se abre el modal
  useEffect(() => {
    if (project) {
      setNombre(project.nombre);
      setFechaInicio(new Date(project.fecha_inicio).toISOString().split('T')[0]);
      setFechaFin(new Date(project.fecha_fin).toISOString().split('T')[0]);
      setError(null);
      setSuccess(null);
    }
  }, [project]);

  const handleProjectUpdate = async (event: FormEvent) => {
    event.preventDefault();
    if (!project) return;
    setError(null);

    if (new Date(fechaInicio) >= new Date(fechaFin)) {
      setError('La fecha de inicio debe ser anterior a la fecha de fin.');
      return;
    }

    try {
      await updateProject(project.id.toString(), {
        nombre,
        fecha_inicio: new Date(fechaInicio).toISOString(),
        fecha_fin: new Date(fechaFin).toISOString(),
      });
      setSuccess('Proyecto actualizado con éxito.');
      onProjectUpdated(); // Refresca la lista en el dashboard
    } catch (err) {
      if (err instanceof Error) setError(err.message);
    }
  };

const handleDeleteCollaborator = async (collaborator:UserProject ) => {
    if (!project) return;

    const confirmDelete = window.confirm(`¿Estás seguro de que quieres eliminar a ${collaborator.email} del proyecto?`);
    if (confirmDelete) {
      try {
        await deleteCollaborator(project.id.toString(), collaborator.id);
        setSuccess('Colaborador eliminado con éxito.');
        onProjectUpdated(); // Refresca los datos para que la tabla se actualice
      } catch (err) {
        alert((err as Error).message);
      }
    }
  };

  const handleRoleChange = async (e: ChangeEvent<HTMLSelectElement>, collaboratorId: number) => {
    if (!project) return;
    const newRole = e.target.value;
    try {
      await updateCollaboratorRole(project.id.toString(), collaboratorId, newRole);
      setSuccess(`Rol de usuario actualizado a '${newRole}'.`);
      onProjectUpdated(); // Refresca para asegurar consistencia
    } catch (err) {
      alert((err as Error).message);
    }
  };
  
  // ... (useEffect para clic afuera no cambia)

  if (!isOpen || !project) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-40 flex justify-center items-center">
      <div ref={modalRef} className="bg-white p-6 rounded-lg shadow-xl w-full max-w-2xl">
        <h2 className="text-xl font-bold mb-4">Editar Proyecto: {project.nombre}</h2>
        
        {/* Formulario para Detalles del Proyecto */}
        <form onSubmit={handleProjectUpdate} className="space-y-4 border-b pb-6 mb-6">
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
          <div className="flex justify-end">
            <button type="submit" className="px-4 py-2 font-bold text-white bg-blue-600 rounded-md hover:bg-blue-700">Guardar Cambios</button>
          </div>
        </form>

        {/* Tabla de Colaboradores */}
        <div>
          <h3 className="text-lg font-semibold mb-2">Colaboradores</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Usuario</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Rol</th>
                  {isOwner && <th className="px-4 py-2 w-10"></th>}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {project.asociaciones_usuario?.map(({ usuario, rol }) => (
                  <tr key={usuario.id}>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-800">{usuario.email}</td>
                    <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                      {isOwner && usuario.email !== currentUser?.sub ? (
                        // Si soy el dueño Y no es mi propia fila, muestro un dropdown
                        <select
                          defaultValue={rol}
                          onChange={(e) => handleRoleChange(e, usuario.id)}
                          className="w-full p-1 border rounded-md border-gray-300 focus:outline-none focus:ring-1 focus:ring-blue-500"
                        >
                          <option value="lector">Lector</option>
                          <option value="editor">Editor</option>
                        </select>
                      ) : (
                        // Si no, solo muestro el texto del rol
                        <span className="font-semibold">{rol}</span>
                      )}
                    </td>
                    {isOwner && (
                      <td className="px-4 py-2 whitespace-nowrap text-center text-sm">
                        {usuario.email !== currentUser?.sub && (
                          <button 
                            onClick={() => handleDeleteCollaborator(usuario)}
                            className="text-gray-400 hover:text-red-600"
                            title={`Eliminar a ${usuario.email}`}
                          >
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        )}
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        
        {error && <div className="mt-4 p-3 text-sm text-center text-red-100 text-red-800 rounded-md">{error}</div>}
        {success && <div className="mt-4 p-3 text-sm text-center text-green-100 text-green-800 rounded-md">{success}</div>}

        <div className="mt-6 flex justify-end">
          <button type="button" onClick={onClose} className="px-4 py-2 font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200">Cerrar</button>
        </div>
      </div>
    </div>
  );
};