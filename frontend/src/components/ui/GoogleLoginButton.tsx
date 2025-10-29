// src/components/auth/GoogleLoginButton.tsx
import { useGoogleLogin } from '@react-oauth/google';

interface GoogleLoginButtonProps {
  onSuccess: (code: string) => void;
  onError?: () => void;
}

export const GoogleLoginButton = ({ onSuccess, onError }: GoogleLoginButtonProps) => {
  const login = useGoogleLogin({
    flow: 'auth-code',
    onSuccess: codeResponse => onSuccess(codeResponse.code),
    onError: error => {
      console.error('Login de Google fallido:', error);
      if (onError) onError();
    },
  });

  return (
    <button
      onClick={() => login()}
      type="button"
      className="w-full flex items-center justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50"
    >
      {/* Icono de Google SVG */}
      <svg className="w-5 h-5 mr-2" viewBox="0 0 48 48">
        <path fill="#4285F4" d="M24 9.5c3.9 0 6.9 1.6 9.1 3.7l6.9-6.9C35.2 2.5 30.1 0 24 0 14.9 0 7.3 5.4 3 13l8.4 6.5C13.2 13.2 18.2 9.5 24 9.5z"></path>
        <path fill="#34A853" d="M46.2 25.4c0-1.7-.2-3.4-.5-5H24v9.5h12.5c-.5 3.1-2.1 5.7-4.6 7.5l7.8 6c4.6-4.2 7.3-10.4 7.3-18z"></path>
        <path fill="#FBBC05" d="M11.4 28.5c-.4-1.2-.6-2.5-.6-3.8s.2-2.6.6-3.8L3 13C1.1 16.5 0 20.6 0 24.8c0 4.2 1.1 8.3 3 11.8l8.4-6.3z"></path>
        <path fill="#EA4335" d="M24 48c6.1 0 11.2-2 14.9-5.4l-7.8-6c-2.5 1.7-5.7 2.7-9.1 2.7-6 0-11-3.7-12.8-8.8L3 36.6C7.3 44.4 14.9 48 24 48z"></path>
        <path fill="none" d="M0 0h48v48H0z"></path>
      </svg>
      Continuar con Google
    </button>
  );
};