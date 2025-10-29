// src/components/forms/addBatchInvoicesModal.tsx
import { useState, useEffect, useRef } from 'react';
import type { FormEvent } from 'react';
import { getBatchesForProject, getCategoriesForProject } from '../../api/projectService';
import { createElectronicInvoice } from '../../api/invoiceService';
import beepSoundURL from '../../assets/beep.mp3';
import QrInputModal from '../../features/QrReader/QrInputModal';
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  projectId: string;
  onInvoiceCreated: () => void;
}

interface BatchOrCategory { id: number; nombre: string; }
interface Status { type: 'idle' | 'success' | 'error'; message: string; }

export const AddBatchInvoicesModal = ({ isOpen, onClose, projectId, onInvoiceCreated }: ModalProps) => {
  const [scannedUrls, setScannedUrls] = useState<string[]>([]);
  const [status, setStatus] = useState<Status>({ type: 'idle', message: 'Listo para escanear.' });
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const [selectedBatch, setSelectedBatch] = useState<number | undefined>();
  const [selectedCategory, setSelectedCategory] = useState<number | undefined>();
  const [batches, setBatches] = useState<BatchOrCategory[]>([]);
  const [categories, setCategories] = useState<BatchOrCategory[]>([]);

  const modalRef = useRef<HTMLDivElement>(null);
  
  const [savePdf, setSavePdf] = useState(false); // <-- Checkbox state
  const playScanSound = () => new Audio(beepSoundURL).play();
  
  const isPaused = useRef(false);
  // Función para procesar un QR detectado
  const processDecodedText = (decodedText: string) => {
    
    if (isPaused.current) return;

    if (scannedUrls.includes(decodedText)) {
      setStatus({ type: 'error', message: 'Este QR ya está en la lista.' });
      return;
    }
    isPaused.current = true;
    playScanSound();
    setScannedUrls(prev => [...prev, decodedText]);
    setStatus({ type: 'success', message: `Factura #${scannedUrls.length + 1} añadida a la lista.` });
    setTimeout(() => {
      setStatus({ type: 'idle', message: 'Listo para escanear.' });
      isPaused.current = false;
    }, 3000);
  };
  
  // Efecto para manejar el ciclo de vida del escáner
  useEffect(() => {
    if (!isOpen) return;

    // Resetear estados al abrir
    setStatus({ type: 'idle', message: 'Apunte la cámara a un código QR.' });
    setScannedUrls([]);
    setSavePdf(false);
    const fetchData = async () => {
      setBatches(await getBatchesForProject(projectId));
      setCategories(await getCategoriesForProject());
    };
    fetchData();

   

    
  }, [isOpen, projectId]);

  
  
  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (scannedUrls.length === 0) return;
    
    setIsSubmitting(true);
    setStatus({ type: 'idle', message: `Enviando ${scannedUrls.length} facturas...` });
    
    const results = await Promise.allSettled(
      scannedUrls.map(url => createElectronicInvoice({
        proyecto_id: projectId,
        url,
        save_pdf: savePdf,
        batch_id: selectedBatch,
        categoria_id: selectedCategory
      }))
    );
    
    const successCount = results.filter(r => r.status === 'fulfilled').length;
    const failedCount = results.length - successCount;

    setIsSubmitting(false);
    alert(`Proceso completado: ${successCount} facturas creadas, ${failedCount} fallaron.`);
    
    if (failedCount === 0) {
      onInvoiceCreated();
      onClose();
    }
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (modalRef.current && !modalRef.current.contains(event.target as Node)) onClose();
    };
    if (isOpen) document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen, onClose]);

  const handleRemoveUrl = (indexToRemove: number) => {
    setScannedUrls(prevUrls => prevUrls.filter((_, index) => index !== indexToRemove));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-40 flex justify-center items-center">
      <div ref={modalRef} className="bg-white p-6 rounded-lg shadow-xl w-full max-w-2xl">
        <h2 className="text-xl font-bold mb-4">Agregar Facturas en Lote</h2>
        
        <div className="grid grid-cols-2 gap-4">
          {/* Columna Izquierda: Cámara y Controles */}
          <div className="flex flex-col">
             <QrInputModal
             isOpen={isOpen}
             onQrDetected={processDecodedText}
             onClose={()=>console.log("cerrando")}
             />
          </div>

          {/* Columna Derecha: Lista y Formulario */}
          <div className="flex flex-col">
            <p className="text-sm font-medium text-gray-700">Facturas en cola: {scannedUrls.length}</p>
            <div className="border rounded-md mt-1 h-48 overflow-y-auto p-2 bg-gray-50 text-xs">
              {scannedUrls.length > 0 ? (
                <ul>
                  {scannedUrls.map((url, index) => 
                  <li key={index} 
                  className="flex justify-between items-center p-1 hover:bg-gray-200 rounded"
                  >
                    <span className="truncate flex-grow pr-2">{index + 1}. {url}</span>
                    <button 
                        onClick={() => handleRemoveUrl(index)}
                        className="p-1 text-gray-400 hover:text-red-600 rounded-full flex-shrink-0"
                        title="Eliminar de la lista"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                      </li>)}
                </ul>
              ) : (
                <div className="flex items-center justify-center h-full text-gray-400">La lista de facturas escaneadas aparecerá aquí.</div>
              )}
            </div>

            <form onSubmit={handleSubmit} className="mt-4 flex-grow flex flex-col justify-between">
              <div>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <select onChange={e => setSelectedBatch(Number(e.target.value))} className="w-full px-3 py-2 border rounded-md shadow-sm border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <option value="">Asignar a Lote</option>
                    {batches.map(b => <option key={b.id} value={b.id}>{b.nombre}</option>)}
                  </select>
                  <select onChange={e => setSelectedCategory(Number(e.target.value))} className="w-full px-3 py-2 border rounded-md shadow-sm border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <option value="">Asignar a Categoría</option>
                    {categories.map(c => <option key={c.id} value={c.id}>{c.nombre}</option>)}
                  </select>
                </div>

                <div className="mb-4">
                  <label className="flex items-center space-x-2 text-sm text-gray-700">
                    <input type="checkbox" checked={savePdf} onChange={e => setSavePdf(e.target.checked)} className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                    <span>Guardar PDFs de las facturas</span>
                  </label>
                </div>
                {status.message && <div className={`p-2 rounded-md text-center text-sm font-medium mb-4 ${status.type === 'success' ? 'bg-green-100 text-green-800' : ''} ${status.type === 'error' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-600'}`}>{status.message}</div>}
              </div>

              <div className="flex justify-end space-x-3">
                <button type="button" onClick={onClose} className="px-4 py-2 font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200">Cancelar</button>
                <button type="submit" disabled={scannedUrls.length === 0 || isSubmitting} className="px-4 py-2 font-bold text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-blue-300">
                  {isSubmitting ? 'Procesando...' : `Crear ${scannedUrls.length} Factura(s)`}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};