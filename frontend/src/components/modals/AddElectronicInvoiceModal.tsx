// src/components/forms/AddElectronicInvoiceModal.tsx
import { useState, useEffect, useRef } from 'react';
import type { FormEvent } from 'react';
import { Html5Qrcode } from 'html5-qrcode';
import { getBatchesForProject, getCategoriesForProject } from '../../api/projectService';
import { createElectronicInvoice } from '../../api/invoiceService';
import beepSoundURL from '../../assets/beep.mp3';
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  projectId: string;
  onInvoiceCreated: () => void;
}

// Suponiendo que tus lotes/categorías tienen esta forma
interface BatchOrCategory {
  id: number;
  nombre: string;
}

export const AddElectronicInvoiceModal = ({ isOpen, onClose, projectId, onInvoiceCreated }: ModalProps) => {
  const [savePdf, setSavePdf] = useState(true);
  const [selectedBatch, setSelectedBatch] = useState<number | undefined>();
  const [selectedCategory, setSelectedCategory] = useState<number | undefined>();
  const [scannedUrl, setScannedUrl] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const [batches, setBatches] = useState<BatchOrCategory[]>([]);
  const [categories, setCategories] = useState<BatchOrCategory[]>([]);
  
  const scannerRef = useRef<Html5Qrcode | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Carga lotes y categorías cuando se abre el modal
  useEffect(() => {
    if (isOpen) {
      const fetchData = async () => {
        setBatches(await getBatchesForProject(projectId));
        setCategories(await getCategoriesForProject());
      };
      fetchData();
      
      // Inicia el escáner de cámara
      startCameraScanner();
    } else {
      stopCameraScanner(); // Asegúrate de detener la cámara al cerrar
    }

    // Función de limpieza para detener la cámara si el componente se desmonta
    return () => {
      stopCameraScanner();
    };
  }, [isOpen, projectId]);

  const startCameraScanner = () => {
    if (scannerRef.current) return;
    const qrCodeScanner = new Html5Qrcode("qr-reader");
    scannerRef.current = qrCodeScanner;

    const qrCodeSuccessCallback = (decodedText: string) => {
      playScanSound();
      setScannedUrl(decodedText);
      setErrorMessage('');
      stopCameraScanner();
    };

    qrCodeScanner.start(
      { facingMode: "environment" },
      { fps: 10, qrbox: { width: 250, height: 250 } },
      qrCodeSuccessCallback,
      undefined // qrCodeErrorCallback (opcional)
    ).catch(err => {
      setErrorMessage("No se pudo iniciar la cámara. Asegúrate de dar permisos.");
      console.error("Error al iniciar la cámara:", err);
    });
  };

   const playScanSound = () => {
    // URL de un sonido de notificación simple y gratuito. Puedes cambiarla por cualquier .mp3
    // const soundUrl = 'https://cdn.pixabay.com/download/audio/2021/08/04/audio_9c32e79aea.mp3';
    const audio = new Audio(beepSoundURL);
    audio.play();
  };
  const stopCameraScanner = () => {
    if (scannerRef.current && scannerRef.current.isScanning) {
      scannerRef.current.stop().catch(err => console.error("Error al detener el escáner:", err));
    }
    scannerRef.current = null;
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      const file = event.target.files[0];
      const qrCodeScanner = new Html5Qrcode("qr-reader"); // Usamos un escaner temporal
      try {
        const decodedText = await qrCodeScanner.scanFile(file, false);
        setScannedUrl(decodedText);
        setErrorMessage('');
        stopCameraScanner(); // Detiene la cámara si estaba activa
      } catch (err) {
        setErrorMessage("No se pudo encontrar un código QR en la imagen.");
        console.error("Error al escanear archivo:", err);
      }
    }
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!scannedUrl) {
      setErrorMessage("Debes escanear un código QR primero.");
      return;
    }
    try {
      await createElectronicInvoice({
        proyecto_id: projectId,
        url: scannedUrl,
        save_pdf: savePdf,
        batch_id: selectedBatch,
        category_id: selectedCategory
      });
      onInvoiceCreated();
      onClose();
    } catch (err) {
      if (err instanceof Error) setErrorMessage(err.message);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-40 flex justify-center items-center">
      <div className="bg-white p-6 rounded-lg shadow-xl w-full max-w-lg">
        <h2 className="text-xl font-bold mb-4">Agregar Factura Electrónica</h2>
        
        {/* Visor de la cámara y opción de subir archivo */}
        <div className="mb-4 p-4 border rounded-md text-center bg-gray-50">
          {!scannedUrl ? (
            <>
              <div id="qr-reader" className="w-full"></div>
              <p className="text-sm text-gray-500 my-2">o</p>
              <button 
                type="button" 
                onClick={() => fileInputRef.current?.click()} 
                className="px-4 py-2 font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-100 text-sm"
              >
                Subir Foto de QR
              </button>
              <input type="file" ref={fileInputRef} onChange={handleFileChange} accept="image/*" className="hidden" />
            </>
          ) : (
            <div className="p-4 text-center">
              <p className="text-green-600 font-bold">¡Código QR escaneado con éxito!</p>
              <p className="text-xs text-gray-600 break-all mt-2">{scannedUrl}</p>
              <button onClick={() => setScannedUrl('')} className="text-sm text-blue-500 mt-2">Escanear de nuevo</button>
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit}>
          {errorMessage && <div className="text-sm text-red-700 mb-4">{errorMessage}</div>}
          
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
          
          <div className="mb-6">
            <label className="flex items-center space-x-2 text-sm text-gray-700">
              <input type="checkbox" checked={savePdf} onChange={e => setSavePdf(e.target.checked)} className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
              <span>Guardar PDF de la factura</span>
            </label>
          </div>
          
          <div className="flex justify-end space-x-3">
            <button 
              type="button" 
              onClick={onClose} 
              className="px-4 py-2 font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200"
            >
              Cancelar
            </button>
            {/* 👇 Estilo primario aplicado */}
            <button 
              type="submit" 
              disabled={!scannedUrl} 
              className="px-4 py-2 font-bold text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed"
            >
              Crear Factura
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};