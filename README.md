# 🎤 Frontend MSMK Voice Assistant - Integración con A.R.C.A-LLM

Frontend moderno y mejorado para el asistente de voz A.R.C.A-LLM con interfaz interactiva, animaciones avanzadas y integración completa con el backend.

## 📋 Características Principales

✅ **Integración Completa con A.R.C.A-LLM** - Conexión directa con el backend FastAPI  
✅ **Interfaz Moderna** - Diseño inspirado en Iron Man con efectos visuales avanzados  
✅ **Captura de Audio en Tiempo Real** - MediaRecorder API con conversión automática a WAV  
✅ **Animaciones Fluidas** - Orbes de energía, efectos HUD y transiciones suaves  
✅ **Detección Automática de Entorno** - Funciona en Docker y desarrollo local  
✅ **Testing Completo** - Suite de tests con Jest y cobertura de código  
✅ **Docker Ready** - Imagen optimizada con Nginx para producción  
✅ **CI/CD Automatizado** - Pipeline con GitHub Actions para tests y despliegue  

## 🚀 Inicio Rápido

### Opción 1: Docker (Recomendado)

```bash
# Construir y ejecutar
docker-compose up --build

# O en modo detached
docker-compose up -d
```

**Acceso:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Opción 2: Desarrollo Local

```bash
# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm start

# O con Python
cd frontend
python3 -m http.server 3000
```

## 🔗 Integración con Backend A.R.C.A-LLM

### Repositorio del Backend

- **URL**: https://github.com/infantesromeroadrian/A.R.C.A-LLM
- **Puerto**: 8000
- **Tecnología**: Python + FastAPI

### Endpoints Utilizados

#### `POST /api/voice/process`

Procesa audio de voz y retorna respuesta en audio.

**Request:**
```javascript
FormData {
  audio: File (WAV/WEBM),
  language: "es",
  session_id: String (opcional, UUID)
}
```

**Response:**
- Body: Audio WAV (binary)
- Headers:
  - `X-Conversation-Id`: ID de conversación (Base64)
  - `X-Transcribed-Text`: Texto transcrito (Base64)
  - `X-Response-Text`: Respuesta del LLM (Base64)

#### `GET /api/health`

Health check del backend.

**Response:**
```json
{
  "status": "healthy",
  "service": "A.R.C.A LLM Voice Assistant"
}
```

### Configuración de Conexión

El frontend detecta automáticamente el entorno:

```javascript
// js/backend-integration.js
const isDocker = window.location.hostname !== 'localhost' && 
                 window.location.hostname !== '127.0.0.1';

const CONFIG = {
    // En Docker: usa URL relativa (nginx hace proxy a /api)
    // En desarrollo: usa localhost:8000
    BACKEND_URL: isDocker ? '' : 'http://localhost:8000',
    AUDIO_FORMAT: 'audio/webm',
    MIN_RECORDING_TIME: 500,    // ms
    MAX_RECORDING_TIME: 30000,  // ms
    RETRY_ATTEMPTS: 3
};
```

## 📊 Flujo de Procesamiento

```
[Usuario hace click en el orbe]
    ↓
[MediaRecorder captura audio del micrófono]
    ↓
[Usuario hace click de nuevo para enviar]
    ↓
[Conversión automática: WEBM → WAV (16kHz)]
    ↓
[POST /api/voice/process con FormData]
    ↓
[Backend A.R.C.A-LLM procesa:]
    ├─ Whisper STT → Transcribe audio
    ├─ LLM (LM Studio) → Genera respuesta
    └─ pyttsx3 TTS → Sintetiza audio
    ↓
[Response: Audio WAV + Headers con texto]
    ↓
[Frontend reproduce audio automáticamente]
    ↓
[Animaciones del orbe durante reproducción]
    ↓
[Conversación guardada con session_id]
```

## 📁 Estructura del Proyecto

```
msmk-voice-assistant/
├── frontend/                    # Frontend principal
│   ├── css/                    # Estilos modulares
│   │   ├── main.css           # Estilos base
│   │   ├── artistic-effects.css # Efectos visuales
│   │   ├── arc-reactor.css    # Efectos del orbe
│   │   ├── gold-chat.css      # Estilos del chat
│   │   ├── hud-effects.css    # Efectos HUD
│   │   └── responsive.css     # Diseño responsive
│   │
│   ├── js/                     # JavaScript modular
│   │   ├── backend-integration.js  # Integración con A.R.C.A-LLM
│   │   ├── config.js          # Configuración global
│   │   ├── state.js           # Gestión de estado
│   │   ├── events.js          # Manejo de eventos
│   │   ├── animation.js       # Animaciones
│   │   ├── drawing.js         # Canvas y dibujos
│   │   ├── orb.js             # Lógica del orbe
│   │   ├── gold-chat.js       # Sistema de chat
│   │   └── __tests__/         # Tests unitarios
│   │
│   ├── index.html             # Página principal
│   └── Dockerfile             # Imagen Docker del frontend
│
├── Dockerfile                  # Dockerfile principal (multi-stage)
├── docker-compose.yml         # Orquestación completa
├── package.json               # Dependencias Node.js
├── .github/workflows/         # CI/CD con GitHub Actions
│   └── ci-cd.yml             # Pipeline automatizado
└── README.md                  # Este archivo
```

## 🎨 Características de la Interfaz

### Diseño Visual

- **Paleta de Colores**: Inspirada en Iron Man (Rojo y Dorado)
- **Orbe Interactivo**: Animación central con efectos de energía
- **Efectos de Fondo**: Circuitos s, rayos de energía, orbes flotantes
- **HUD Moderno**: Indicadores de estado, animaciones fluidas
- **Chat Dorado**: Sistema de mensajes con estilo premium

### Funcionalidades

- **Captura de Audio**: MediaRecorder API con soporte para múltiples formatos
- **Conversión Automática**: WEBM → WAV (16kHz) para compatibilidad con Whisper
- **Reproducción Automática**: Audio de respuesta se reproduce automáticamente
- **Gestión de Conversaciones**: Mantiene contexto con `session_id`
- **Feedback Visual**: Estados visuales durante grabación, procesamiento y reproducción
- **Responsive Design**: Adaptado para móviles, tablets y desktop

## 🐳 Docker

### Dockerfile

El proyecto incluye un Dockerfile multi-stage optimizado:

```dockerfile
# Etapa 1: Base con Node.js
FROM node:20-alpine AS base
WORKDIR /app
COPY package*.json ./
RUN npm install

# Etapa 2: Tests
FROM base AS test
COPY frontend ./frontend
ENV CI=true
RUN npm test -- --runInBand

# Etapa 3: Producción con Nginx
FROM nginx:1.27-alpine
COPY --from=test /app/frontend /usr/share/nginx/html
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1/ || exit 1
```

### Docker Compose

El `docker-compose.yml` incluye:

- **Frontend**: Servido con Nginx (puerto 3000)
- **Backend**: API A.R.C.A-LLM (puerto 8000)
- **Networking**: Red interna para comunicación entre servicios
- **Volúmenes**: Persistencia de modelos y logs

## 🧪 Testing

### Ejecutar Tests

```bash
# Tests básicos
npm test

# Con cobertura
npm run test:coverage

# Modo watch (desarrollo)
npm run test:watch
```

### Estructura de Tests

Los tests están organizados en `frontend/js/__tests__/`:

- `backend-integration.test.js` - Tests de integración con el backend
- `config.test.js` - Tests de configuración
- `gold-chat.test.js` - Tests del sistema de chat
- `state.test.js` - Tests de gestión de estado

### Cobertura

El proyecto mantiene una cobertura de código alta con Jest:

```bash
npm run test:coverage
```

Los reportes se generan en `coverage/` con formato HTML, LCOV y texto.

## 🔄 CI/CD

### GitHub Actions Workflow

El pipeline automatizado (`.github/workflows/ci-cd.yml`) incluye:

1. **Tests del Frontend**
   - Instalación de dependencias con `npm ci`
   - Ejecución de tests con Jest
   - Generación de reportes de cobertura

2. **Build de Docker**
   - Construcción de imagen multi-stage
   - Validación de la imagen
   - Cache de layers para builds rápidos

3. **Publicación** (solo en `main`)
   - Push a GitHub Container Registry (GHCR)
   - Tags automáticos basados en SHA, branch y tags
   - Metadata completa de la imagen

### Triggers

El workflow se ejecuta en:
- Push a `main` o `frontend-mejorado`
- Pull requests a `main` o `frontend-mejorado`
- Tags (para releases)

## 🔧 Configuración Avanzada

### Variables de Entorno

El frontend puede configurarse mediante variables de entorno en el Dockerfile o docker-compose.yml:

```yaml
environment:
  BACKEND_URL: "http://backend:8000"  # Para Docker
  # O dejar que se detecte automáticamente
```

### Proxy Nginx (Docker)

En producción con Docker, Nginx puede configurarse para hacer proxy al backend:

```nginx
location /api {
    proxy_pass http://backend:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## 📡 API Integration Details

### Manejo de Errores

El frontend incluye manejo robusto de errores:

- **Reintentos automáticos**: Hasta 3 intentos en caso de fallo de red
- **Validación de audio**: Verifica que el audio no esté vacío antes de enviar
- **Feedback al usuario**: Mensajes de estado claros durante el proceso
- **Recuperación de errores**: Manejo graceful de errores del backend

### Optimizaciones

- **Conversión de audio**: Solo se convierte a WAV si es necesario
- **Compresión**: Audio optimizado para Whisper (16kHz, mono)
- **Caché de conversaciones**: Mantiene `session_id` para contexto
- **Lazy loading**: Carga de recursos bajo demanda

## 🐛 Troubleshooting

### Frontend no conecta con backend

1. Verifica que el backend esté corriendo:
   ```bash
   curl http://localhost:8000/api/health
   ```

2. Revisa la consola del navegador (F12) para errores de CORS

3. Verifica la configuración en `js/backend-integration.js`

### Micrófono no funciona

1. Permite acceso al micrófono en la configuración del navegador
2. Usa `localhost` (no `127.0.0.1` o IP)
3. Verifica permisos del sistema operativo
4. HTTPS puede ser requerido en algunos navegadores

### Audio no se reproduce

1. Verifica que el backend retorne audio válido
2. Revisa la consola para errores de decodificación
3. Verifica que el navegador soporte el formato WAV

### Docker build falla

1. Verifica que Docker tenga suficiente memoria (4GB+)
2. Limpia cache: `docker system prune -a`
3. Reconstruye sin cache: `docker-compose build --no-cache`

## 📚 Documentación Adicional

- [Backend Integration Guide](BACKEND_INTEGRATION.md) - Guía detallada de integración
- [Frontend Testing Guide](frontend/TESTING.md) - Documentación de tests
- [Deployment Guide](DEPLOYMENT.md) - Guía de despliegue
- [Backend API Docs](http://localhost:8000/docs) - Documentación interactiva del backend

## 🚀 Despliegue

### Producción con Docker

```bash
# Build de imágenes
docker-compose build

# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f frontend

# Detener servicios
docker-compose down
```

### Variables de Entorno para Producción

Asegúrate de configurar:

- `BACKEND_URL`: URL del backend en producción
- `CORS_ORIGINS`: Orígenes permitidos para CORS
- Variables del backend (LM Studio, Whisper, etc.)

## 📄 Licencia

MIT License

## 👨‍💻 Autor

Frontend desarrollado para integración con A.R.C.A-LLM  
Backend: https://github.com/infantesromeroadrian/A.R.C.A-LLM

## 🙏 Agradecimientos

- **A.R.C.A-LLM** - Backend completo con STT, LLM y TTS
- **FastAPI** - Framework web moderno
- **Jest** - Framework de testing
- **Nginx** - Servidor web de alto rendimiento

---

**¿Listo para hablar con A.R.C.A? 🎤🤖**
