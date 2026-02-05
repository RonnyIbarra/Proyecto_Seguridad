"""
Script para crear usuario demo y datos de prueba
Ejecutar una sola vez para inicializar la BD
"""

import sys
import os

# Agregar backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import User, SecureData, Base
from backend.crypto_module import CryptoManager
from datetime import datetime

def setup_demo():
    """Configura base de datos con usuario demo y datos de prueba"""
    
    print("\n" + "="*60)
    print("  CONFIGURACIÓN INICIAL DE CRYPTOVAULT")
    print("="*60 + "\n")
    
    # Crear conexión
    DATABASE_URL = "sqlite:///./backend/crypto_app.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    
    # Crear tablas
    print("[1/4] Creando tablas de base de datos...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tablas creadas\n")
    
    # Crear sesión
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Verificar si usuario demo existe
        demo_user = db.query(User).filter(User.username == "demo").first()
        if demo_user:
            print("[2/4] Usuario 'demo' ya existe")
            db.close()
            print("\n✓ Base de datos ya configurada\n")
            return
        
        # Crear usuario demo
        print("[2/4] Creando usuario demo...")
        crypto = CryptoManager()
        password = "demo123"
        pwd_hash, salt = crypto.hash_password(password)
        
        demo_user = User(
            username="demo",
            email="demo@cryptovault.local",
            password_hash=pwd_hash,
            password_salt=salt
        )
        
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
        print(f"✓ Usuario creado: demo / demo123")
        print(f"  ID: {demo_user.id}\n")
        
        # Crear datos de prueba cifrados
        print("[3/4] Agregando datos de prueba...")
        
        # Generar claves
        aes_key = crypto.generate_symmetric_key()
        private_key, public_key = crypto.generate_rsa_keypair()
        
        # Guardar claves
        os.makedirs("backend/keys", exist_ok=True)
        with open(f"backend/keys/user_{demo_user.id}_aes.key", 'w') as f:
            f.write(aes_key)
        with open(f"backend/keys/user_{demo_user.id}_rsa_private.pem", 'w') as f:
            f.write(private_key)
        with open(f"backend/keys/user_{demo_user.id}_rsa_public.pem", 'w') as f:
            f.write(public_key)
        
        # Datos de prueba
        test_data = [
            {
                "title": "Tarjeta de Crédito",
                "data": "VISA 1234-5678-9012-3456",
                "method": "AES"
            },
            {
                "title": "Número de Identidad",
                "data": "DNI: 1234567890 Expedición: 2020-01-15",
                "method": "AES"
            },
            {
                "title": "Información Bancaria",
                "data": "Banco: FinanzasAmerica\nCuenta: 98765432\nCBU: 0170065478903400000154",
                "method": "RSA"
            },
            {
                "title": "Coordenadas GPS",
                "data": "Latitud: -0.2317, Longitud: -78.5084",
                "method": "CAESAR"
            },
            {
                "title": "Token API",
                "data": "demo_api_token_12345",
                "method": "AES"
            }
        ]
        
        for idx, test in enumerate(test_data, 1):
            if test["method"] == "AES":
                encrypted = crypto.encrypt_aes(test["data"], aes_key)
            elif test["method"] == "RSA":
                encrypted = crypto.encrypt_rsa(test["data"], public_key)
            elif test["method"] == "CAESAR":
                encrypted = crypto.caesar_encrypt(test["data"], shift=5)
            
            secure_data = SecureData(
                user_id=demo_user.id,
                title=test["title"],
                data_encrypted=encrypted,
                method=test["method"]
            )
            db.add(secure_data)
            print(f"  ✓ {idx}. {test['title']} ({test['method']})")
        
        db.commit()
        print("\n")
        
        # Estadísticas
        print("[4/4] Estadísticas finales:")
        users_count = db.query(User).count()
        data_count = db.query(SecureData).count()
        
        print(f"  • Usuarios en BD: {users_count}")
        print(f"  • Datos cifrados: {data_count}")
        print(f"  • Directorio de claves: backend/keys/")
        
        db.close()
        
        print("\n" + "="*60)
        print("  ✓ CONFIGURACIÓN COMPLETADA")
        print("="*60)
        
        print("\nPara usar la aplicación:")
        print("  Usuario: demo")
        print("  Contraseña: demo123")
        
        print("\nPróximos pasos:")
        print("  1. cd backend")
        print("  2. python main.py")
        print("  3. Abrir frontend/index.html")
        print("\n")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    setup_demo()
