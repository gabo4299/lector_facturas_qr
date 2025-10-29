// src/components/QrReader/QrInputModal.tsx

import { useState } from 'react';
import QrScanner from '../QrScanner'; // El que ya tienes
import UrlInput from './UrlInput';
import ImageUploadReader from './ImageUploadReader';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onQrDetected: (qrData: string) => void;
}

const QrInputModal = ({ isOpen, onClose, onQrDetected }: Props) => {
  const [mode, setMode] = useState<'scan' | 'upload' | 'url'>('scan');

  const handleQrDetectionAndClose = (qrData: string) => {
    onQrDetected(qrData);
    onClose();
  };
  

  if (!isOpen) return null;

  return (
    <div className="modal-backdrop">
      <div className="modal-content">
        {/* <button onClick={onClose}>Cerrar</button> */}
        <div className="tabs">
          <button  className="px-4 py-2 font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-100 text-sm" onClick={() => setMode('scan')}>Escanear</button>
          <button  className="px-4 py-2 font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-100 text-sm" onClick={() => setMode('upload')}>Subir Imagen</button>
          <button  className="px-4 py-2 font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-100 text-sm" onClick={() => setMode('url')}>URL</button>
        </div>

        {mode === 'scan' && <QrScanner onScanSuccess={onQrDetected}  />}
        
    {mode === 'upload' && <ImageUploadReader onQrDetected={handleQrDetectionAndClose} />}

        {mode === 'url' && <UrlInput onUrlSubmit={onQrDetected} />}
      </div>
    </div>
  );
};

export default QrInputModal;