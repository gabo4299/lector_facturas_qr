// src/App.tsx
import { AppRouter } from './routes/AppRouter';
import { AuthProvider } from './context/AuthContext'; // 👈
function App() {
  // El componente App ahora solo se encarga de montar el enrutador.
  // Más adelante podría contener Providers de Context.
  return (<AuthProvider>
      <AppRouter />
    </AuthProvider>)
}

export default App;