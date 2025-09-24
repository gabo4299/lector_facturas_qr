import asyncio
import argparse
import sys
import os
#run desde lector_facturas_Qr con python -m backend.services.create_superuser test@t.com
# Añadimos la raíz del proyecto al path para que encuentre el paquete 'backend'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Ahora podemos importar desde nuestro paquete
from backend.db.database import AsyncSessionLocal
from backend.crud import crud_users

async def set_superuser_status(email: str, status: bool):
    """
    Busca un usuario por email y establece su estado de superusuario.
    """
    print(f"Buscando al usuario con email: {email}...")
    db = AsyncSessionLocal()
    try:
        user = await crud_users.get_user_by_email(db, email=email)
        
        if not user:
            print(f"❌ Error: No se encontró ningún usuario con el email '{email}'.")
            return

        user.is_superuser = status
        await db.commit()
        
        status_text = "promovido a" if status else "revocado de"
        print(f"✅ Éxito: El usuario '{email}' ha sido {status_text} superusuario.")

    finally:
        await db.close()

if __name__ == "__main__":
    # Configuramos el parser para argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Gestionar estado de superusuario.")
    parser.add_argument("email", type=str, help="El email del usuario a modificar.")
    parser.add_argument("--revoke", action="store_true", help="Revocar permisos de superusuario en lugar de otorgarlos.")
    
    args = parser.parse_args()
    
    # Ejecutamos la lógica asíncrona
    is_promoting = not args.revoke
    asyncio.run(set_superuser_status(email=args.email, status=is_promoting))