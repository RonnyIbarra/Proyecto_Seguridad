# DOCUMENTACIÓN TÉCNICA - CryptoVault

## Índice
1. Arquitectura del Sistema
2. Módulo de Criptografía
3. Base de Datos
4. API REST
5. Frontend
6. Seguridad
7. Deployment

---

## 1. ARQUITECTURA DEL SISTEMA

### Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                             │
│                    (HTML/CSS/JavaScript)                     │
│                        index.html                            │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/CORS
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                      API REST (FastAPI)                      │
│                       main.py                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  /api/users     /api/data      /api/info             │   │
│  │  - register     - encrypt      - técnicas            │   │
│  │  - login        - decrypt                            │   │
│  │                 - list                               │   │
│  │                 - delete                             │   │
│  └──────────────────────────────────────────────────────┘   │
│                         │                                    │
│                         ↓                                    │
│              ┌────────────────────────┐                      │
│              │ MÓDULO CRIPTOGRAFÍA    │                      │
│              │  crypto_module.py      │                      │
│              │ ┌──────────────────┐   │                      │
│              │ │ AES-256          │   │                      │
│              │ │ RSA-2048         │   │                      │
│              │ │ SHA-256 + Salt   │   │                      │
│              │ │ Cifrado César    │   │                      │
│              │ └──────────────────┘   │                      │
│              └────────────────────────┘                      │
└────────────────┬──────────────────────────────────────────────┘
                 │ SQL
                 ↓
         ┌───────────────┐
         │   SQLite BD   │
         │ crypto_app.db │
         └───────────────┘
```

### Flujo de Datos

1. **Registro:**
   - Usuario envía: username, email, password
   - Backend hasea password con PBKDF2-SHA256 + salt
   - Almacena en BD

2. **Cifrado:**
   - Usuario selecciona método (AES/RSA/César)
   - Datos se cifran con técnica seleccionada
   - Se almacenan cifrados en BD

3. **Descifrado:**
   - Usuario solicita descifrar datos
   - Backend recupera clave correspondiente
   - Descifra y devuelve plaintext

---

## 2. MÓDULO DE CRIPTOGRAFÍA

### Arquitectura del Módulo

```python
CryptoManager (Clase Principal)
├── Hash Seguro (SHA-256 + Salt)
│   ├── hash_password(password, salt=None)
│   └── verify_password(password, stored_hash, salt)
│
├── Cifrado Simétrico (AES-256)
│   ├── generate_symmetric_key()
│   ├── encrypt_aes(plaintext, key)
│   └── decrypt_aes(ciphertext, key)
│
├── Cifrado Asimétrico (RSA-2048)
│   ├── generate_rsa_keypair(key_size=2048)
│   ├── encrypt_rsa(plaintext, public_key_pem)
│   └── decrypt_rsa(ciphertext_b64, private_key_pem)
│
├── Cifrado Clásico (César)
│   ├── caesar_encrypt(plaintext, shift=3)
│   └── caesar_decrypt(ciphertext, shift=3)
│
└── Utilidades
    └── generate_secure_token(length=32)
```

### Algoritmos Implementados

#### 2.1 SHA-256 con Salt (PBKDF2)

**Especificación:**
- Algoritmo: PBKDF2
- Hash: SHA-256
- Iterations: 100,000
- Salt size: 256 bits (32 bytes)

**Implementación:**

```python
def hash_password(password: str, salt: bytes = None) -> tuple:
    if salt is None:
        salt = secrets.token_bytes(32)  # Random 256-bit salt
    
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        iterations=100000  # OWASP recommendation
    )
    
    return (pwd_hash.hex(), salt.hex())
```

**Seguridad:**
- PBKDF2 estándar NIST
- 100,000 iteraciones = resistencia a fuerza bruta
- Salt impide ataques rainbow table
- Hash de 256 bits

**Ejemplo:**

```
Entrada: password="MiContraseña123"
Salt: a7b3c9e1f4d6b8a2c5e7f9d1b3a5c7e9...
Hash: 8f9a3c2d5b7e1f4a6c8d9e0b1c3d5f7a...
```

#### 2.2 AES-256 (Fernet)

**Especificación:**
- Algoritmo: AES en modo CBC
- Key size: 256 bits
- IV: Generado aleatoriamente
- Autenticación: HMAC-SHA256
- Encoding: Base64

**Implementación:**

```python
def encrypt_aes(plaintext: str, key: str) -> str:
    f = Fernet(key.encode())
    ciphertext = f.encrypt(plaintext.encode())
    return ciphertext.decode()

def decrypt_aes(ciphertext: str, key: str) -> str:
    f = Fernet(key.encode())
    plaintext = f.decrypt(ciphertext.encode())
    return plaintext.decode()
```

**Ventajas Fernet:**
- Autenticación incluida (HMAC)
- Timestamp incluido
- Resistencia a ataques de fuerza bruta
- Proof: Biblioteca cryptography recomendada

**Ejemplo:**

```
Plaintext: "Información bancaria confidencial"
Ciphertext: "gAAAAABlc8q2_hY3k8m9j7q2p1o0n8m7..."
```

#### 2.3 RSA-2048 (OAEP)

**Especificación:**
- Algoritmo: RSA
- Key size: 2048 bits
- Padding: OAEP con SHA-256
- Formato: PEM

**Implementación:**

```python
def generate_rsa_keypair(key_size: int = 2048) -> tuple:
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )
    
    public_key = private_key.public_key()
    # Serializar a PEM...
    return (private_pem, public_pem)

def encrypt_rsa(plaintext: str, public_key_pem: str) -> str:
    public_key = serialization.load_pem_public_key(
        public_key_pem.encode(),
        backend=default_backend()
    )
    
    ciphertext = public_key.encrypt(
        plaintext.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    return base64.b64encode(ciphertext).decode()
```

**Características:**
- Cifrado asimétrico profesional
- OAEP padding resiste ataques conocidos
- Distribución segura de claves
- 2048 bits seguro hasta 2030+ (NIST)

#### 2.4 Cifrado César

**Especificación:**
- Desplazamiento: 3-5 caracteres
- Propósito: Educativo/Demostrativo
- Rango: A-Z, a-z

**Implementación:**

```python
def caesar_encrypt(plaintext: str, shift: int = 3) -> str:
    result = []
    for char in plaintext:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            shifted = (ord(char) - base + shift) % 26
            result.append(chr(base + shifted))
        else:
            result.append(char)
    return ''.join(result)
```

---

## 3. BASE DE DATOS

### Modelo de Entidades

```
┌─────────────┐           ┌──────────────┐
│    User     │◄──────┐   │  SecureData  │
├─────────────┤       │   ├──────────────┤
│ id (PK)     │       │   │ id (PK)      │
│ username    │───────┼───│ user_id (FK) │
│ email       │       │   │ title        │
│ password... │       │   │ data_encrpt  │
│ salt        │       │   │ rsa_encrpt   │
│ created_at  │       │   │ method       │
└─────────────┘       │   │ created_at   │
                      │   └──────────────┘
                      └─ Relación 1-N
```

### Tabla: User

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    password_salt VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Tabla: SecureData

```sql
CREATE TABLE secure_data (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title VARCHAR NOT NULL,
    data_encrypted VARCHAR NOT NULL,
    rsa_encrypted VARCHAR,
    method VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
```

---

## 4. API REST

### Endpoints Documentados

#### 4.1 Autenticación

**POST /api/users/register**
```json
Request:
{
  "username": "usuario123",
  "email": "usuario@ejemplo.com",
  "password": "ContraseñaSegura123"
}

Response (200):
{
  "id": 1,
  "username": "usuario123",
  "email": "usuario@ejemplo.com",
  "created_at": "2024-02-03T10:30:00"
}

Errores:
- 400: Usuario ya existe
- 422: Validación fallida
```

**POST /api/users/login**
```json
Request:
{
  "username": "usuario123",
  "password": "ContraseñaSegura123"
}

Response (200):
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "username": "usuario123",
    "email": "usuario@ejemplo.com"
  },
  "message": "Login exitoso"
}

Errores:
- 401: Credenciales inválidas
```

#### 4.2 Cifrado/Descifrado

**POST /api/data/encrypt**
```json
Request:
{
  "title": "Datos Bancarios",
  "data": "CC: 1234-5678-9012-3456",
  "method": "AES"  // o "RSA", "CAESAR"
}

Response (200):
{
  "id": 1,
  "title": "Datos Bancarios",
  "method": "AES",
  "message": "Datos cifrados exitosamente"
}
```

**POST /api/data/decrypt**
```json
Request:
{
  "data_id": 1
}

Response (200):
{
  "title": "Datos Bancarios",
  "data": "CC: 1234-5678-9012-3456",
  "method": "AES",
  "message": "Descifrado exitoso"
}
```

**GET /api/data/list**
```json
Response (200):
{
  "count": 3,
  "data": [
    {
      "id": 1,
      "title": "Datos Bancarios",
      "method": "AES",
      "created_at": "2024-02-03T10:30:00"
    },
    ...
  ]
}
```

**DELETE /api/data/{data_id}**
```json
Response (200):
{
  "message": "Datos eliminados"
}

Errores:
- 404: Datos no encontrados
```

#### 4.3 Información

**GET /api/info**
```json
Response (200):
{
  "app": "Sistema Seguro de Criptografía",
  "version": "1.0.0",
  "techniques": {
    "AES": {
      "name": "Advanced Encryption Standard",
      "type": "Simétrico",
      "bits": 256
    },
    ...
  }
}
```

### Códigos HTTP

| Código | Significado | Ejemplo |
|--------|-------------|---------|
| 200 | OK | Operación exitosa |
| 400 | Bad Request | Datos inválidos |
| 401 | Unauthorized | Credenciales inválidas |
| 404 | Not Found | Recurso no existe |
| 422 | Unprocessable Entity | Validación fallo |
| 500 | Server Error | Error interno |

---

## 5. FRONTEND

### Estructura HTML

```html
┌─────────────────────────────────┐
│           HEADER                │
│  Logo | Nav Links               │
├─────────────────────────────────┤
│      TAB NAVIGATION             │
│  Login | Register | Encrypt ... │
├─────────────────────────────────┤
│     TAB CONTENT                 │
│  ┌─────────────────────────┐    │
│  │  Active Tab Content     │    │
│  │  (Forms, Data, etc)     │    │
│  └─────────────────────────┘    │
├─────────────────────────────────┤
│        ALERTS                   │
│  (Messages, Errors)             │
└─────────────────────────────────┘
```

### Paleta de Colores

```css
--primary: #1a237e       (Azul profundo)
--secondary: #0277bd     (Azul cian)
--accent: #00e676        (Verde neón)
--danger: #d32f2f        (Rojo)
--bg-dark: #0d1b2a       (Fondo oscuro)
--text-primary: #ffffff  (Texto blanco)
```

### Responsividad

- Desktop: Grid de 3 columnas
- Tablet: Grid de 2 columnas
- Mobile: Grid de 1 columna

---

## 6. SEGURIDAD

### Medidas de Seguridad Implementadas

#### 6.1 Almacenamiento de Contraseñas

```
Flujo:
Password → PBKDF2-SHA256 → Hash + Salt → BD

Verificación:
Password → PBKDF2-SHA256 (mismo salt) → Comparar con BD
```

**Garantías:**
- ✓ No se almacenan contraseñas en plaintext
- ✓ Salt impide rainbow tables
- ✓ 100k iteraciones resisten fuerza bruta
- ✓ PBKDF2 estándar OWASP

#### 6.2 Cifrado de Datos

**Opción AES:**
- ✓ Cifrado simétrico robusto
- ✓ Autenticación HMAC incluida
- ✓ IV aleatorio cada cifrado
- ✓ 256 bits de seguridad

**Opción RSA:**
- ✓ Asimétrico (clave pública/privada)
- ✓ OAEP padding seguro
- ✓ 2048 bits (seguro hasta 2030+)

#### 6.3 Claves de Sesión

```python
token = secrets.token_urlsafe(32)  # 32 bytes aleatorios
```

- ✓ Generación criptográficamente segura
- ✓ No predecible
- ✓ Único por sesión

#### 6.4 CORS

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: lista específica
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Producción:**
```python
allow_origins=["https://dominio.com"]
```

#### 6.5 Validación de Entrada

```python
class EncryptDataRequest(BaseModel):
    title: str              # Tipo validado
    data: str
    method: str             # Enum en producción

# Pydantic valida automáticamente
```

### Vulnerabilidades Mitigadas

| Vulnerabilidad | Mitigación |
|---|---|
| SQL Injection | SQLAlchemy ORM |
| XSS | No eval() en frontend |
| CSRF | JSON body en POST |
| Weak passwords | Requerimientos en frontend |
| Leaky secrets | Variables de entorno |
| Insecure deserialization | Pydantic validation |

---

## 7. DEPLOYMENT

### Deployment Local (Desarrollo)

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py

# Frontend (en otra terminal)
cd frontend
python -m http.server 8080
```

### Deployment en Producción

#### Opción 1: Heroku

```bash
pip install gunicorn
# Crear Procfile
echo "web: gunicorn -w 4 -b 0.0.0.0:\$PORT main:app" > Procfile
heroku create
git push heroku main
```

#### Opción 2: Azure App Service

```bash
# Crear recurso
az appservice plan create --name CryptoVault --sku F1 -g rg
az webapp create -n cryptovault -g rg --plan CryptoVault

# Deploy
az webapp deployment source config-zip -g rg -n cryptovault --src archive.zip
```

#### Opción 3: Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .
EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "main:app"]
```

```bash
docker build -t cryptovault .
docker run -p 8000:8000 cryptovault
```

### Variables de Entorno

Crear `.env`:

```env
DATABASE_URL=sqlite:///./crypto_app.db
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
```

En `main.py`:

```python
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
```

---

## 📊 Estadísticas del Proyecto

```
Archivo               | Líneas | Complejidad
─────────────────────────────────────────
crypto_module.py      | 350+   | Alta
main.py              | 400+   | Alta
index.html           | 600+   | Media
README.md            | 350+   | -
TECNICA.md (este)    | 500+   | -
─────────────────────────────────────────
TOTAL                | 2200+  | -
```

## 🎯 Conclusiones

CryptoVault implementa de forma profesional:

✅ **3 técnicas criptográficas principales:**
1. AES-256 (Simétrico)
2. RSA-2048 (Asimétrico)
3. SHA-256 + Salt (Hash)

✅ **Buenas prácticas:**
- Gestión segura de claves
- Validación de entrada
- Manejo de errores
- Documentación

✅ **Sistema completo:**
- Backend robusto
- Frontend intuitivo
- BD relacional
- API profesional

---

**Documento Técnico v1.0**  
**Proyecto: Ingeniería de Seguridad de Software**  
**Fecha: Febrero 2024**
