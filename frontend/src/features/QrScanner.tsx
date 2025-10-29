// src/components/QrScanner.tsx
import { Html5Qrcode, Html5QrcodeScannerState, Html5QrcodeSupportedFormats } from 'html5-qrcode';
import type {CameraDevice} from 'html5-qrcode';
import { useEffect, useRef, useState } from 'react';

// Tipos para las props del componente
interface Props {
  onScanSuccess: (decodedText: string) => void;
  onScanFailure?: (error: string) => void;
  onClose?:()=>void;
}

const QR_READER_ID = 'html5-qr-code-full-region';

const QrScanner = ({ onScanSuccess, onScanFailure }: Props) => {
  // Referencia para la instancia de Html5Qrcode
  const html5QrCodeRef = useRef<Html5Qrcode | null>(null);

  // Estado para las cámaras disponibles
  const [cameras, setCameras] = useState<CameraDevice[]>([]);
  // Estado para la cámara seleccionada
  const [selectedCameraId, setSelectedCameraId] = useState<string>('');
  // Estado para controlar el flash
  const [isFlashOn, setIsFlashOn] = useState(false);
  // Estado para almacenar el resultado del escaneo
  const [scanResult, setScanResult] = useState<string | null>(null);


   const [zoom, setZoom] = useState(1);
  const [isZoomSupported, setIsZoomSupported] = useState(true);
  // --- EFECTOS DE CICLO DE VIDA ---

  // 1. Obtener cámaras y seleccionar la trasera por defecto
  useEffect(() => {
    const fetchCameras = async () => {
      try {
        const devices = await Html5Qrcode.getCameras();
        if (devices && devices.length) {
          setCameras(devices);
          // Priorizar la cámara trasera ('environment')
          const rearCamera = devices.find(device => device.label.toLowerCase().includes('back') || device.label.toLowerCase().includes('trasera'));
          setSelectedCameraId(rearCamera ? rearCamera.id : devices[0].id);
        }
      } catch (error) {
        console.error('Error al obtener las cámaras:', error);
      }
    };
    fetchCameras();
  }, []);

  // 2. Iniciar y detener el escáner cuando cambia la cámara seleccionada
  useEffect(() => {
    if (!selectedCameraId) return;

    // Crear instancia de la librería
    const html5QrCode = new Html5Qrcode(QR_READER_ID, {
      formatsToSupport: [Html5QrcodeSupportedFormats.QR_CODE],
      verbose: false, // Desactiva los logs detallados
    });
    html5QrCodeRef.current = html5QrCode;

    // Función de éxito del escaneo
    const qrCodeSuccessCallback = (decodedText: string) => {
      if (decodedText !== scanResult) {
        setScanResult(decodedText);
        onScanSuccess(decodedText);
        // Opcional: detener el escáner después de un éxito
        // handleStop();
      }
    };

    // Función de error del escaneo (se llama en cada fotograma sin QR)
    const qrCodeErrorCallback = (errorMessage: string) => {
        // Ignoramos los errores comunes de "QR no encontrado"
        if (!errorMessage.includes("No QR code found")) {
            // console.error(errorMessage);
            if (onScanFailure) {
                onScanFailure(errorMessage);
            }
        }
    };

    // Opciones de configuración OPTIMIZADAS
    const config = {
      fps: 25, // Fotogramas por segundo. 10 es un buen balance.
      qrbox: { width: 300, height: 300 }, // ¡LA MEJORA MÁS IMPORTANTE!
      aspectRatio: 1.0, // Ratio de aspecto del video
      rememberLastUsedCamera: true, // Recordar la última cámara usada

    };

    // Iniciar el escáner
    html5QrCode.start(
      selectedCameraId,
      config,
      qrCodeSuccessCallback,
      qrCodeErrorCallback
    ).catch((err) => {
      console.error('No se pudo iniciar el escáner', err);
    });

    // Función de limpieza para detener el escáner al desmontar el componente
    return () => {
      handleStop();
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCameraId]);
  
  // 3. Efecto para controlar el flash
  useEffect(() => {
    if (html5QrCodeRef.current && html5QrCodeRef.current.getState() === Html5QrcodeScannerState.SCANNING) {
      
      const constraints = {
        advanced: [{ torch: isFlashOn }],
      };
       html5QrCodeRef.current.applyVideoConstraints(constraints)
        .then(() => {
          console.log(`Flash ${isFlashOn ? 'encendido' : 'apagado'}.`);
        })
        .catch((err) => {
            alert(err)
          console.error('No se pudo aplicar la restricción del flash.', err);
          // A menudo, el error indica que el dispositivo no es compatible con el flash.
        });
    }
  }, [isFlashOn]);

  const handleStop = async () => {
    if (html5QrCodeRef.current) {
      try {
        // Solo intentar detener si el escáner está realmente activo
        if (html5QrCodeRef.current.getState() === Html5QrcodeScannerState.SCANNING) {
          await html5QrCodeRef.current.stop();
        }
        await html5QrCodeRef.current.clear(); // Limpia la UI y los recursos
        console.log('Escáner detenido y limpiado correctamente.');
      } catch (err) {
        console.error('Error al detener o limpiar el escáner.', err);
      }
    }
  };
   useEffect(() => {
    if (html5QrCodeRef.current && html5QrCodeRef.current.getState() === Html5QrcodeScannerState.SCANNING && isZoomSupported) {
      html5QrCodeRef.current.applyVideoConstraints({ advanced: [{ zoom: zoom }] })
        .catch((err) => {
          console.error("Error al aplicar el zoom:", err);
          if (err.name === 'OverconstrainedError') {
            setIsZoomSupported(false);
          }
        });
    }
  }, [zoom, isZoomSupported]);



  const toggleFlash = () => {
    setIsFlashOn(prev => !prev);
  };
  
  return (
    <div className="qr-scanner-container">
      {/* El div donde se renderizará el video del escáner */}
      <div id={QR_READER_ID} style={{ width: '100%', maxWidth: '350px', margin: '0 auto' }}></div>

      {/* Controles del escáner */}
      <div className="qr-controls" style={{ marginTop: '5px', textAlign: 'center' }}>
        {cameras.length > 1 && (
          <select 
            onChange={(e) => setSelectedCameraId(e.target.value)} 
            value={selectedCameraId}
            style={{ padding: '8px', marginRight: '10px' }}
          >
            {cameras.map(camera => (
              <option key={camera.id} value={camera.id}>
                {camera.label}
              </option>
            ))}
          </select>
        )}

        {isZoomSupported && (
        <div className="zoom-slider-container" style={{ maxWidth: '300px', margin: '10px auto', textAlign: 'center' }}>
            <div className="flex items-center space-x-4">
                <button onClick={toggleFlash} className="p-1">
                    {isFlashOn ? 'Apagar Flash 🔦' : 'Encender Flash 💡'}
                </button>
                <label htmlFor="zoom" className="block mb-0">Zoom 🔎</label>
                </div>
          <input
            id="zoom"
            type="range"
            min="1" // Valor mínimo seguro
            max="5" // Valor máxi mo conservador
            step="0.1"
            value={zoom}
            onChange={(e) => setZoom(parseFloat(e.target.value))}
            style={{ width: '100%' }}
          />
          
        </div>
      )}
        
      </div>

      {scanResult && <p style={{ color: 'green', textAlign: 'center' }}>Último resultado: {scanResult}</p>}
    </div>
  );
};

export default QrScanner;