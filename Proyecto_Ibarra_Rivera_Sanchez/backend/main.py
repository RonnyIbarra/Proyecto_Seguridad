"""
BACKEND - FastAPI
API REST con CRUD, autenticación y operaciones criptográficas
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, ConfigDict
from datetime import datetime
import os
from crypto_module import CryptoManager

# ============ CONFIGURACIÓN ============
DATABASE_URL = "sqlite:///./crypto_app.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI(
    title="API Segura de Criptografía",
    description="Sistema CRUD con técnicas criptográficas",
    version="1.0.0"
)

# ============ CORS ============
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ MODELOS DE BASE DE DATOS ============
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    password_salt = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class SecureData(Base):
    __tablename__ = "secure_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    title = Column(String)
    data_encrypted = Column(String)  # Cifrado con AES
    rsa_encrypted = Column(String)   # Copia con RSA (opcional)
    method = Column(String)  # 'AES', 'RSA', 'CAESAR'
    created_at = Column(DateTime, default=datetime.utcnow)


# Crear tablas
Base.metadata.create_all(bind=engine)

# ============ MODELOS PYDANTIC ============
class UserRegister(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    email: str
    created_at: datetime


class EncryptDataRequest(BaseModel):
    title: str
    data: str
    method: str  # 'AES', 'RSA', 'CAESAR'


class DecryptDataRequest(BaseModel):
    data_id: int


class SecureDataResponse(BaseModel):
    id: int
    title: str
    method: str
    created_at: datetime


# ============ DEPENDENCIAS ============
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============ FUNCIONES AUXILIARES ============
crypto = CryptoManager()

def get_or_create_aes_key(user_id: int, db: Session) -> str:
    """Obtiene o crea clave AES para el usuario"""
    key_file = f"keys/user_{user_id}_aes.key"
    os.makedirs("keys", exist_ok=True)
    
    if os.path.exists(key_file):
        with open(key_file, 'r') as f:
            return f.read()
    else:
        key = crypto.generate_symmetric_key()
        with open(key_file, 'w') as f:
            f.write(key)
        return key


def get_or_create_rsa_keys(user_id: int, db: Session) -> tuple:
    """Obtiene o crea par RSA para el usuario"""
    priv_file = f"keys/user_{user_id}_rsa_private.pem"
    pub_file = f"keys/user_{user_id}_rsa_public.pem"
    os.makedirs("keys", exist_ok=True)
    
    if os.path.exists(priv_file) and os.path.exists(pub_file):
        with open(priv_file, 'r') as f:
            private_key = f.read()
        with open(pub_file, 'r') as f:
            public_key = f.read()
        return private_key, public_key
    else:
        private_key, public_key = crypto.generate_rsa_keypair()
        with open(priv_file, 'w') as f:
            f.write(private_key)
        with open(pub_file, 'w') as f:
            f.write(public_key)
        return private_key, public_key


# ============ RUTAS: AUTENTICACIÓN ============
@app.post("/api/users/register")
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """Registra nuevo usuario con contraseña hasheada"""
    
    try:
        # Validar que no estén vacíos
        if not user_data.username or not user_data.email or not user_data.password:
            raise HTTPException(status_code=400, detail="Todos los campos son requeridos")
        
        # Validar longitud de contraseña
        if len(user_data.password) < 6:
            raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 6 caracteres")
        
        # Verificar si usuario ya existe
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Usuario ya existe")
        
        # Verificar si email ya existe
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="El email ya está registrado")
        
        # Hash seguro para contraseña
        pwd_hash, salt = crypto.hash_password(user_data.password)
        
        # Crear nuevo usuario
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=pwd_hash,
            password_salt=salt
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "created_at": new_user.created_at.isoformat() if new_user.created_at else None,
            "message": "Usuario registrado exitosamente"
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error en registro: {str(e)}")


@app.post("/api/users/login")
def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login y retorna token de sesión (simulado)"""
    
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    # Verificar contraseña
    if not crypto.verify_password(credentials.password, user.password_hash, user.password_salt):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    # Token simulado
    token = crypto.generate_secure_token(32)
    
    return {
        "token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None
        },
        "message": "Login exitoso"
    }


# ============ RUTAS: CRUD DE DATOS SEGUROS ============
@app.post("/api/data/encrypt")
def encrypt_data(request: EncryptDataRequest, db: Session = Depends(get_db)):
    """Cifra datos usando el método especificado"""
    
    # Simulamos user_id = 1 (en producción viene del token)
    user_id = 1
    
    try:
        encrypted_data = None
        
        if request.method == "AES":
            aes_key = get_or_create_aes_key(user_id, db)
            encrypted_data = crypto.encrypt_aes(request.data, aes_key)
        
        elif request.method == "RSA":
            _, public_key = get_or_create_rsa_keys(user_id, db)
            encrypted_data = crypto.encrypt_rsa(request.data, public_key)
        
        elif request.method == "CAESAR":
            encrypted_data = crypto.caesar_encrypt(request.data, shift=5)
        
        else:
            raise ValueError("Método no soportado")
        
        # Guardar en BD
        secure_data = SecureData(
            user_id=user_id,
            title=request.title,
            data_encrypted=encrypted_data,
            method=request.method
        )
        
        db.add(secure_data)
        db.commit()
        db.refresh(secure_data)
        
        return {
            "id": secure_data.id,
            "title": secure_data.title,
            "method": secure_data.method,
            "message": "Datos cifrados exitosamente"
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en cifrado: {str(e)}")


@app.post("/api/data/decrypt")
def decrypt_data(request: DecryptDataRequest, db: Session = Depends(get_db)):
    """Descifra datos almacenados"""
    
    user_id = 1
    
    # Obtener registro
    record = db.query(SecureData).filter(
        SecureData.id == request.data_id,
        SecureData.user_id == user_id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Datos no encontrados")
    
    try:
        decrypted_data = None
        
        if record.method == "AES":
            aes_key = get_or_create_aes_key(user_id, db)
            decrypted_data = crypto.decrypt_aes(record.data_encrypted, aes_key)
        
        elif record.method == "RSA":
            private_key, _ = get_or_create_rsa_keys(user_id, db)
            decrypted_data = crypto.decrypt_rsa(record.data_encrypted, private_key)
        
        elif record.method == "CAESAR":
            decrypted_data = crypto.caesar_decrypt(record.data_encrypted, shift=5)
        
        return {
            "title": record.title,
            "data": decrypted_data,
            "method": record.method,
            "message": "Descifrado exitoso"
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en descifrado: {str(e)}")


@app.get("/api/data/list")
def list_user_data(db: Session = Depends(get_db)):
    """Lista todos los datos cifrados del usuario"""
    
    user_id = 1
    
    records = db.query(SecureData).filter(SecureData.user_id == user_id).all()
    
    return {
        "count": len(records),
        "data": [
            {
                "id": r.id,
                "title": r.title,
                "method": r.method,
                "created_at": r.created_at
            }
            for r in records
        ]
    }


@app.delete("/api/data/{data_id}")
def delete_data(data_id: int, db: Session = Depends(get_db)):
    """Elimina datos cifrados"""
    
    user_id = 1
    
    record = db.query(SecureData).filter(
        SecureData.id == data_id,
        SecureData.user_id == user_id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Datos no encontrados")
    
    db.delete(record)
    db.commit()
    
    return {"message": "Datos eliminados"}


# ============ RUTAS: INFORMACIÓN ============
@app.get("/api/info")
def get_info():
    """Información sobre las técnicas criptográficas implementadas"""
    
    return {
        "app": "Sistema Seguro de Criptografía",
        "version": "1.0.0",
        "techniques": {
            "AES": {
                "name": "Advanced Encryption Standard",
                "type": "Simétrico",
                "bits": 256,
                "description": "Cifrado simétrico robusto para datos sensibles"
            },
            "RSA": {
                "name": "Rivest-Shamir-Adleman",
                "type": "Asimétrico",
                "bits": 2048,
                "description": "Cifrado asimétrico con clave pública/privada"
            },
            "SHA-256": {
                "name": "Secure Hash Algorithm",
                "type": "Hash",
                "bits": 256,
                "description": "Hash seguro con salt para contraseñas"
            },
            "CAESAR": {
                "name": "Cifrado César",
                "type": "Clásico",
                "description": "Cifrado de sustitución simple educativo"
            }
        }
    }


@app.get("/")
def read_root():
    """Endpoint raíz"""
    return {
        "message": "Bienvenido a la API de Criptografía",
        "docs": "/docs",
        "endpoints": {
            "info": "/api/info",
            "register": "POST /api/users/register",
            "login": "POST /api/users/login",
            "encrypt": "POST /api/data/encrypt",
            "decrypt": "POST /api/data/decrypt",
            "list": "GET /api/data/list",
            "delete": "DELETE /api/data/{data_id}"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
