// src/components/forms/EditInvoiceModal.tsx
import { useState, useEffect, useRef } from 'react';
import type { FormEvent } from 'react';
import { updateElectronicInvoice, updateManualInvoice } from '../../api/invoiceService';
import type { UnifiedInvoice, Batch, Category } from '../../pages/ProjectDetailPage';
import { getCategoriesForProject } from '../../api/projectService';

interface EditModalProps {
  isOpen: boolean;
  onClose: () => void;
  invoice: UnifiedInvoice | null;
  batches: Batch[];
  onInvoiceUpdated: () => void;
}

export const EditInvoiceModal = ({ isOpen, onClose, invoice, batches, onInvoiceUpdated }: EditModalProps) => {
  // Estados para todos los campos posibles
  const [savePdf, setSavePdf] = useState(false);
  const [montoTotal, setMontoTotal] = useState('');
  const [fecha, setFecha] = useState('');
  const [selectedBatchId, setSelectedBatchId] = useState<number | null>(null);
  const [selectedCategoryId, setSelectedCategoryId] = useState<number | null>(null);
    const [categories, setCategories] = useState<Category[]>([]);
  const [error, setError] = useState<string | null>(null);
  const modalRef = useRef<HTMLDivElement>(null);

  // Efecto para pre-llenar el formulario según el tipo de factura
  useEffect(() => {
    if (invoice) {
      // Campos comunes
      setSelectedBatchId(invoice.batch_id || null);
      setSelectedCategoryId(invoice.categoria_id || null);
      const fetchData = async () => {
                    setCategories(await getCategoriesForProject());
                  };
       fetchData();


      // Campos específicos
      if (invoice.type === 'Electrónica') {
        setSavePdf(invoice.save_pdf || false);
      } else if (invoice.type === 'Manual') {
        // Formatear la fecha para el input tipo 'date' (YYYY-MM-DD)
        const formattedDate = new Date(invoice.fecha_date || Date.now()).toISOString().split('T')[0];
        setFecha(formattedDate);
        setMontoTotal(invoice.total_amount.toString());
      }
    }
  }, [invoice]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!invoice) return;
    setError(null);

    try {
      const numericId = parseInt(invoice.id.split('-')[1], 10);

      // Llama a la API correcta según el tipo de factura
      if (invoice.type === 'Electrónica') {
        await updateElectronicInvoice(numericId, {
          save_pdf: savePdf,
          batch_id: selectedBatchId,
          categoria_id: selectedCategoryId,
        });
      } else if (invoice.type === 'Manual') {
        await updateManualInvoice(numericId, {
          monto_total: parseFloat(montoTotal),
          fecha: new Date(fecha).toISOString(), // Envía en formato ISO
          batch_id: selectedBatchId,
          categoria_id: selectedCategoryId,
        });
      }
      onInvoiceUpdated();
      onClose();
    } catch (err) {
      if (err instanceof Error) setError(err.message);
    }
  };
  
  // ... (useEffect para clic afuera no cambia)

  if (!isOpen || !invoice) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-40 flex justify-center items-center">
      <div ref={modalRef} className="bg-white p-6 rounded-lg shadow-xl w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">Editar Factura {invoice.type}</h2>
        <p className="text-sm text-gray-500 mb-4">ID: {invoice.id}</p>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          
          {/* CAMPOS CONDICIONALES PARA FACTURA MANUAL */}
          {invoice.type === 'Manual' && (
            <>
              <div>
                <label htmlFor="monto_total" className="block text-sm font-medium text-gray-700">Monto Total</label>
                <input id="monto_total" type="number" step="0.01" required value={montoTotal} onChange={e => setMontoTotal(e.target.value)} className="w-full mt-1 px-3 py-2 border rounded-md shadow-sm border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label htmlFor="fecha" className="block text-sm font-medium text-gray-700">Fecha</label>
                <input id="fecha" type="date" required value={fecha} onChange={e => setFecha(e.target.value)} className="w-full mt-1 px-3 py-2 border rounded-md shadow-sm border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
            </>
          )}

          {/* CAMPOS COMUNES */}
          <div>
            <label htmlFor="batch" className="block text-sm font-medium text-gray-700">Lote</label>
            <select id="batch" value={selectedBatchId || ''} onChange={e => setSelectedBatchId(e.target.value ? Number(e.target.value) : null)} className="w-full mt-1 px-3 py-2 border rounded-md shadow-sm border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="">Sin Lote</option>
              {batches.map(b => <option key={b.id} value={b.id}>{b.nombre}</option>)}
            </select>
          </div>
          <div>
            <label htmlFor="category" className="block text-sm font-medium text-gray-700">Categoría</label>
            <select id="category" value={selectedCategoryId || ''} onChange={e => setSelectedCategoryId(e.target.value ? Number(e.target.value) : null)} className="w-full mt-1 px-3 py-2 border rounded-md shadow-sm border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="">Sin Categoría</option>
              {categories.map(c => <option key={c.id} value={c.id}>{c.nombre}</option>)}
            </select>
          </div>

          {/* CAMPO CONDICIONAL PARA FACTURA ELECTRÓNICA */}
          {invoice.type === 'Electrónica' && (
            <div>
              <label className="flex items-center space-x-2 text-sm text-gray-700">
                <input type="checkbox" checked={savePdf} onChange={e => setSavePdf(e.target.checked)} className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                <span>Guardar PDF de la factura</span>
              </label>
            </div>
          )}

          {error && <div className="text-sm text-red-700">{error}</div>}
          <div className="mt-6 flex justify-end space-x-3">
            <button type="button" onClick={onClose} className="px-4 py-2 font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200">Cancelar</button>
            <button type="submit" className="px-4 py-2 font-bold text-white bg-blue-600 rounded-md hover:bg-blue-700">Guardar Cambios</button>
          </div>
        </form>
      </div>
    </div>
  );
};