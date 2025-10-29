// src/App.tsx
import { AppRouter } from './routes/AppRouter';
import { AuthProvider } from './context/AuthContext'; // 👈
import { BrowserRouter } from 'react-router-dom';
import { GoogleOAuthProvider } from '@react-oauth/google';

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

function App() {

  // El componente App ahora solo se encarga de montar el enrutador.
  // Más adelante podría contener Providers de Context.
 return (
    <GoogleOAuthProvider clientId={googleClientId}>
      <BrowserRouter>
        <AuthProvider>
          <AppRouter />
        </AuthProvider>
      </BrowserRouter>
    </GoogleOAuthProvider>
  );
}

export default App;