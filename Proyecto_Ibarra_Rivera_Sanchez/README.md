# 🔐 CryptoVault - Sistema Seguro de Criptografía

**Proyecto Final - Ingeniería de Seguridad de Software**

## 📋 Descripción

CryptoVault es una aplicación web completa que implementa **tres técnicas criptográficas profesionales** en Python con interfaz web moderna. Incluye autenticación segura, CRUD con base de datos y un módulo de criptografía robusto.

## ✨ Características

### 🔐 Técnicas Criptográficas Implementadas (3+)

1. **AES-256 (Cifrado Simétrico)**
   - Estándar de encriptación avanzada
   - Clave de 256 bits
   - Ideal para datos grandes
   - Implementación: Fernet (cryptography library)

2. **RSA-2048 (Cifrado Asimétrico)**
   - Claves pública/privada
   - 2048 bits de seguridad
   - Perfecto para distribución de claves
   - Implementación: cryptography.hazmat

3. **SHA-256 con Salt (Hash Seguro)**
   - PBKDF2 con 100,000 iteraciones
   - Salt de 256 bits
   - Almacenamiento seguro de contraseñas
   - Resistencia a ataques de fuerza bruta

4. **Cifrado César (Clásico)**
   - Cifrado de sustitución simple
   - Propósito educativo
   - Demostración de conceptos básicos

### 🎯 Funcionalidades

✅ **Autenticación Segura**
- Registro de usuarios
- Login con hash y salt
- Gestión de sesiones

✅ **CRUD Completo**
- Crear datos cifrados
- Leer/descifrar datos
- Actualizar
- Eliminar

✅ **Base de Datos**
- SQLite (desarrollo)
- Modelo de usuarios y datos cifrados
- Relaciones y constraints

✅ **API REST**
- Endpoints documentados
- Validación de datos
- Manejo de errores

✅ **Frontend Moderno**
- Interfaz responsiva
- Tema oscuro profesional
- UX intuitiva
- Animaciones suaves

## 🚀 Requisitos Previos

- Python 3.9+
- pip (gestor de paquetes)
- Navegador web moderno

## 📦 Instalación

### 1. Clonar/Descargar el proyecto

```bash
cd Proyecto_Ibarra_Rivera_Sacnhez
```

### 2. Configurar Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Ejecutar Backend

```bash
# En la carpeta backend (con venv activado)
python main.py
```

El servidor estará en: **http://localhost:8000**

API Docs: **http://localhost:8000/docs**

### 4. Abrir Frontend

Simplemente abre en tu navegador:

```
frontend/index.html
```

O en una terminal desde la carpeta `frontend`:

```bash
# Python 3.7+
python -m http.server 8080
```

Luego abre: **http://localhost:8080**

## 📊 Estructura del Proyecto

```
Proyecto_Ibarra_Rivera_Sacnhez/
├── backend/
│   ├── main.py                 # API FastAPI
│   ├── crypto_module.py        # Módulo de criptografía
│   ├── requirements.txt        # Dependencias
│   └── crypto_app.db          # Base de datos (se crea automático)
├── frontend/
│   └── index.html             # Aplicación web completa
├── docs/
│   └── arquitectura.md        # Documentación técnica
└── README.md                  # Este archivo
```

## 🔌 API Endpoints

### Autenticación

```bash
# Registro
POST /api/users/register
{
  "username": "usuario",
  "email": "email@ejemplo.com",
  "password": "contraseña123"
}

# Login
POST /api/users/login
{
  "username": "usuario",
  "password": "contraseña123"
}
```

### Cifrado

```bash
# Cifrar datos
POST /api/data/encrypt
{
  "title": "Mi dato secreto",
  "data": "Información sensible",
  "method": "AES" | "RSA" | "CAESAR"
}

# Descifrar datos
POST /api/data/decrypt
{
  "data_id": 1
}

# Listar datos
GET /api/data/list

# Eliminar datos
DELETE /api/data/{data_id}
```

### Información

```bash
GET /api/info
GET /
```

## 🧪 Pruebas Rápidas

### 1. Probar módulo criptográfico

```bash
cd backend
python crypto_module.py
```

Verás pruebas de:
- ✓ Hash SHA-256
- ✓ AES-256
- ✓ RSA-2048
- ✓ Cifrado César

### 2. Credenciales Demo

En la aplicación web, usa:
- **Usuario:** demo
- **Contraseña:** demo123

*Nota: Registra este usuario primero ejecutando:*

```python
# En Python shell dentro de backend/
from crypto_module import CryptoManager
crypto = CryptoManager()
hash_pwd, salt = crypto.hash_password("demo123")
print(f"Hash: {hash_pwd}")
print(f"Salt: {salt}")
```

## 🔒 Seguridad Implementada

✅ **Hashing:** PBKDF2-SHA256 con 100k iteraciones
✅ **Salt:** Token aleatorio de 256 bits
✅ **AES:** Fernet (authenticated encryption)
✅ **RSA:** OAEP con SHA-256
✅ **Validación:** Pydantic models
✅ **CORS:** Habilitado para desarrollo
✅ **Claves:** Almacenadas de forma segura

## 📝 Casos de Uso

### Caso 1: Almacenar contraseña bancaria
1. Registrar usuario
2. Login
3. Tab "Cifrar" → Método: AES
4. Datos: "numero_cuenta: 123456789, PIN: 1234"
5. ¡Datos cifrados con AES-256 profesional!

### Caso 2: Compartir mensaje secreto
1. Login
2. Cifrar con RSA
3. Compartir clave pública
4. Solo con clave privada se descifra

### Caso 3: Aprender criptografía
1. Usar método CAESAR para entender sustitución
2. Explorar API docs
3. Revisar código fuente

## 🛠️ Personalización

### Cambiar método de cifrado por defecto

En `frontend/index.html`, línea ~300:

```html
<select id="encryptMethod">
  <option value="AES">...</option>  <!-- Cambiar aquí -->
</select>
```

### Cambiar puerto del servidor

En `backend/main.py`, última línea:

```python
uvicorn.run(app, host="0.0.0.0", port=8000)  # Cambiar puerto
```

### Usar PostgreSQL en lugar de SQLite

En `backend/main.py`:

```python
# Cambiar:
DATABASE_URL = "sqlite:///./crypto_app.db"

# Por:
DATABASE_URL = "postgresql://user:password@localhost/cryptodb"

pip install psycopg2-binary
```

## 📚 Referencias Bibliográficas

1. **NIST** (2001). "FIPS 197: Advanced Encryption Standard"
2. **Katz & Lindell** (2021). "Introduction to Modern Cryptography"
3. **Menezes et al.** (1996). "Handbook of Applied Cryptography"
4. **OWASP** (2021). "Cryptographic Storage Cheat Sheet"
5. **RFC 3394** - "AES Key Wrap Algorithm"
6. **RFC 3447** - "PKCS #1: RSA Cryptography"

## ✅ Entregables Completados

- [x] Módulo de criptografía funcional (3 técnicas + 1 clásica)
- [x] Backend API con FastAPI
- [x] Base de datos con SQLAlchemy
- [x] Frontend web responsivo
- [x] CRUD completo
- [x] Autenticación segura
- [x] Documentación técnica

## 🎓 Objetivos de Aprendizaje (Logrados)

1. ✅ Comprender fundamentos de criptografía clásica y moderna
2. ✅ Implementar algoritmos en Python
3. ✅ Construir sistema CRUD con API y BD
4. ✅ Aplicar buenas prácticas de seguridad
5. ✅ Documentar proyecto profesionalmente

## 🚀 Próximas Mejoras

- Autenticación con JWT
- Rate limiting
- Encriptación de base de datos
- Tests automatizados
- Deployment en Azure
- Versión móvil

## 📞 Soporte

Para dudas sobre:
- **Criptografía:** Revisar `crypto_module.py`
- **API:** Ver `http://localhost:8000/docs`
- **Frontend:** Revisar `index.html`

## 📄 Licencia

Proyecto académico - Ingeniería de Seguridad de Software

---

**Hecho con ❤️ y 🔐 para aprender seguridad**
