// src/components/QrReader/ImageUploadReader.tsx

import React, { useState, useCallback, useRef } from 'react';
import { Html5Qrcode } from 'html5-qrcode';

interface ImageUploadReaderProps {
  onQrDetected: (qrData: string) => void;
  // Opcional: para mostrar si hay errores de lectura en la UI del padre
  onScanFailure?: (error: string) => void; 
}

const ImageUploadReader: React.FC<ImageUploadReaderProps> = ({ onQrDetected, onScanFailure }) => {
  const [highlight, setHighlight] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setHighlight(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setHighlight(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setHighlight(true);
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setHighlight(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processImageFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      processImageFile(e.target.files[0]);
    }
  }, []);

  const processImageFile = async (file: File) => {
    if (!file.type.startsWith('image/')) {
      alert('Por favor, sube un archivo de imagen válido.');
      return;
    }

    // Usamos un ID dummy porque html5-qrcode necesita uno, pero no renderizará nada
    // ya que estamos usando scanFile.
    const readerId = "html5-qr-code-image-reader";
    const html5QrCode = new Html5Qrcode(readerId);
    
    try {
      const decodedText = await html5QrCode.scanFile(file, false);
      onQrDetected(decodedText);
      // Limpiar el input para permitir subir la misma imagen de nuevo si es necesario
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      const errorMessage = (err as Error).message || 'No se pudo leer el código QR de la imagen.';
      alert(`Error al leer QR: ${errorMessage}`);
      if (onScanFailure) {
        onScanFailure(errorMessage);
      }
    } finally {
      // Importante: Limpiar la instancia para evitar posibles conflictos o fugas de memoria
      if (html5QrCode.isScanning) { // Comprobar si está escaneando antes de intentar detener
        try {
          await html5QrCode.stop();
        } catch (e) {
          console.warn("No se pudo detener la instancia de html5QrCode, posiblemente ya no estaba activa.", e);
        }
      }
      html5QrCode.clear()
    }
  };

  const openFilePicker = () => {
    fileInputRef.current?.click();
  };

  return (
    <div 
      className="image-upload-area"
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      onClick={openFilePicker} // Abre el selector de archivos al hacer clic
      style={{
        border: `2px dashed ${highlight ? '#007bff' : '#ccc'}`,
        borderRadius: '8px',
        padding: '20px',
        textAlign: 'center',
        cursor: 'pointer',
        minHeight: '250px', // Tamaño similar al qrbox
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: highlight ? '#f0f8ff' : 'white',
        transition: 'all 0.2s ease-in-out',
        width: '100%',
        maxWidth: '350px', // Puedes ajustar esto para que se parezca más al QRScanner
        margin: '0 auto'
      }}
    >
      <input
        type="file"
        accept="image/*"
        onChange={handleFileSelect}
        ref={fileInputRef}
        style={{ display: 'none' }}
      />
      <p style={{ margin: '0 0 10px 0', fontSize: '1.1em', fontWeight: 'bold' }}>
        Arrastra tu imagen aquí
      </p>
      <p style={{ margin: '0', color: '#666' }}>o haz clic para seleccionarla</p>
      <small style={{ marginTop: '10px', color: '#888' }}>(Solo archivos de imagen)</small>
      {/* Este div es necesario para Html5Qrcode, aunque estará oculto */}
      <div id="html5-qr-code-image-reader" style={{ display: 'none' }}></div>
    </div>
  );
};

export default ImageUploadReader;