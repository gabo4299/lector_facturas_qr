// src/hooks/useAuth.ts
import { useContext } from 'react';

import {AuthContext} from '../context/AuthContext'; // 👈 Importa el contexto

// Creamos el hook personalizado para usar el contexto fácilmente
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider');
  }
  return context;
};