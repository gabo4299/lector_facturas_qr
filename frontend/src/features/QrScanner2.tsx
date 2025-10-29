import { useEffect, useRef } from 'react';
import { BrowserMultiFormatReader, NotFoundException, DecodeHintType, BarcodeFormat, MultiFormatReader } from '@zxing/library';

interface CamScannerProps {
  onScanSuccess: (decodedText: string) => void;
  onScanError?: (errorMessage: string) => void;
}

export const QrScanner2 = ({ onScanSuccess, onScanError }: CamScannerProps) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const codeReader = useRef<MultiFormatReader | null>(null);

  useEffect(() => {
    // Solo se ejecuta si el videoRef está disponible
    if (videoRef.current) {
      // 1. Inicializa el lector de códigos
      codeReader.current = new MultiFormatReader();

      // Opcional: Especifica que solo buscas códigos QR para optimizar
      const hints = new Map();
      hints.set(DecodeHintType.POSSIBLE_FORMATS, [BarcodeFormat.QR_CODE]);
      

      // 2. Inicia el escaneo desde el dispositivo de video
      codeReader.current.decode(videoRef.curren)
        .then(result => {
          // 3. Cuando se detecta un código, llama a la función `onScanSuccess`
          onScanSuccess(result.getText());
        })
        .catch(err => {
          // Ignora los errores de "no se encontró QR", que son normales.
          if (!(err instanceof NotFoundException)) {
            console.error(err);
            if (onScanError) {
              onScanError('Error al iniciar la cámara. Asegúrate de dar los permisos.');
            }
          }
        });
    }

    // 4. Función de limpieza: se ejecuta cuando el componente se desmonta
    return () => {
      if (codeReader.current) {
        // Detiene el escaneo y libera la cámara
        codeReader.current.reset();
      }
    };
  }, [onScanSuccess, onScanError]); // Se vuelve a ejecutar si las funciones de callback cambian

  return (
    <div className="w-full h-full">
      {/* El elemento de video donde se mostrará el stream de la cámara */}
      <video ref={videoRef} className="w-full h-full object-cover" />
    </div>
  );
};