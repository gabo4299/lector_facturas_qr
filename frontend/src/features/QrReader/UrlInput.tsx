// src/components/QrReader/UrlInput.tsx

import { useState } from 'react';

const UrlInput = ({ onUrlSubmit }: { onUrlSubmit: (url: string) => void }) => {
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newUrl = e.target.value;
    setUrl(newUrl);

    try {
      const parsedUrl = new URL(newUrl);
      if (parsedUrl.hostname.endsWith('siat.impuestos.gob.bo')) {
        setError('');
      } else {
        setError('La URL debe pertenecer al dominio https://siat.impuestos.gob.bo/');
      }
    } catch (err) {
      setError('Por favor, introduce una URL válida.');
      console.log(err)
    }
  };

  const handleSubmit = () => {
    if (!error && url) {
      onUrlSubmit(url);
      setUrl(''); // Limpiar input
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    // Si la tecla presionada es 'Enter', llama a la función de envío
    if (e.key === 'Enter') {
      handleSubmit();
    }
  };

  return (
    <div>
      <input 
      className='w-full px-3 py-2 border rounded-md shadow-sm border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500' 
      type="text" 
      value={url} 
      onChange={handleUrlChange}
      onKeyDown={handleKeyDown}
      placeholder="https://siat.impuestos.gob.bo/..."/>
      <button onClick={handleSubmit} disabled={!!error || !url} className='mt-4 px-4 py-2 font-bold text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-blue-300'>Añadir URL</button>
      {error && <p style={{color: 'red'}}>{error}</p>}
    </div>
  );
};

export default UrlInput;