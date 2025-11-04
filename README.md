# 🤖 A.R.C.A LLM - Voice Conversational Assistant

**Advanced Reasoning Cognitive Architecture with Language Model and Memory**

Sistema de asistente conversacional por voz que usa:
- **Speech-to-Text**: Whisper Tiny (local, offline, 5x más rápido)
- **LLM**: LM Studio con Qwen3-4B-2507 (rápido y optimizado)
- **Text-to-Speech**: pyttsx3 (local, offline, rápido)
- **Memoria Conversacional**: Contexto completo durante la sesión

---

## 📋 Características

✅ **100% Offline** - Sin dependencias cloud, todo local  
✅ **Memoria Conversacional** - Recuerda todo el contexto de la conversación  
✅ **Baja Latencia** - Optimizado para respuestas < 3 segundos  
✅ **Interfaz Intuitiva** - Un solo botón para hablar  
✅ **Domain-Driven Design** - Arquitectura limpia y mantenible  

---

## 🚀 Quick Start

### 🎨 Opción 1: Interfaz Tkinter con Orbe Jarvis (Desktop) ⭐ NUEVO

**Interfaz desktop futurista con orbe animado estilo Jarvis/Iron Man:**

```bash
# Ejecutar interfaz Tkinter
python -m src.frontend_tkinter.orbe_window

# O con el resto del sistema:
# (por implementar en TICKET-005)
```

**Características:**
- ✨ Orbe animado estilo Jarvis con efectos glow
- 🎤 Click en orbe para activar voz
- 🌈 Estados visuales (idle, listening, processing, speaking)
- 🖥️ Ventana siempre al frente
- ⌨️ Esc o Click derecho para salir

**Status:** 🔄 En desarrollo (Branch: `frontendTkinter`)

---

### 🐳 Opción 2: Docker (Web Interface)

**Más fácil y sin problemas de dependencias:**

```bash
# 1. Asegúrate de tener LM Studio corriendo con Qwen3-8B
# 2. Construir e iniciar
docker-compose up

# 3. Abrir http://localhost:8000
```

📖 **Ver [docs/docker/DOCKER_SETUP.md](docs/docker/DOCKER_SETUP.md) para documentación completa**

---

### 💻 Opción 3: Instalación Local (Web Interface)

**Prerequisitos:**
- **Python 3.11+**
- **LM Studio** instalado y corriendo en `http://192.168.1.38:1234`
- **Modelo cargado** en LM Studio: `qwen/qwen3-4b-2507`

### 2. Instalación

```bash
# Clonar repositorio
cd A.R.C.A-LLM

# Crear virtual environment
python -m venv arca-venv
source arca-venv/bin/activate  # En Windows: arca-venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configuración

**El sistema funciona inmediatamente con defaults optimizados:**
- LM Studio: `http://192.168.1.38:1234/v1`
- Modelo LLM: `qwen/qwen3-4b-2507`
- Whisper: modelo `tiny`, CPU, int8
- TTS: rate 175, volume 0.9
- API: puerto 8000

**Para cambiar configuración (opcional):**

Crear archivo `.env` en la raíz del proyecto:
```bash
# .env
LM_STUDIO_URL=http://otra-ip:1234/v1
LM_STUDIO_MODEL=otro-modelo
WHISPER_MODEL=base
```

Ver todas las variables disponibles en `src/config.py`

### 4. Iniciar LM Studio

1. Abrir LM Studio
2. Cargar modelo: `qwen/qwen3-4b-2507` (o cualquier modelo compatible)
3. Iniciar servidor local en el puerto 1234
4. Verificar que la URL del servidor sea accesible: `http://192.168.1.38:1234`

**Los defaults ya están configurados correctamente en `src/config.py`**

Si necesitas cambiar la configuración, crea un archivo `.env`:
```bash
# .env (opcional)
LM_STUDIO_URL=http://192.168.1.38:1234/v1
LM_STUDIO_MODEL=qwen/qwen3-4b-2507
WHISPER_MODEL=tiny
```

### 5. Ejecutar A.R.C.A

```bash
# Desde la raíz del proyecto
python -m src.api.main

# O con uvicorn directamente
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 6. Usar la Aplicación

Abrir navegador en: **http://localhost:8000**

1. Presionar el botón del micrófono 🎤
2. Hablar (el botón se pone rojo)
3. Click de nuevo para enviar
4. Esperar respuesta (automáticamente se reproduce)
5. ¡Repetir!

---

## 🔌 API para Integración Frontend

📖 **Documentación completa**: [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)

### Endpoint Principal

```http
POST /api/voice/process
Content-Type: multipart/form-data

Body:
- audio: File (audio blob)
- conversation_id: String (optional)

Response:
- Body: audio/wav (respuesta en audio)
- Headers:
  - X-Conversation-Id (Base64)
  - X-Transcribed-Text (Base64)
  - X-Response-Text (Base64)
```

### Ejemplo de Integración

```javascript
const formData = new FormData();
formData.append('audio', audioBlob, 'voice.webm');

const response = await fetch('http://localhost:8000/api/voice/process', {
  method: 'POST',
  body: formData
});

// Decodificar headers
const conversationId = atob(response.headers.get('X-Conversation-Id'));
const transcribedText = atob(response.headers.get('X-Transcribed-Text'));
const llmResponse = atob(response.headers.get('X-Response-Text'));

// Reproducir audio
const audio = new Audio(URL.createObjectURL(await response.blob()));
audio.play();
```

**Otros Endpoints**:
- `GET /api/health` - Health check
- `GET /api/voice/conversation/{id}` - Obtener historial
- `DELETE /api/voice/conversation/{id}` - Eliminar conversación
- `WS /ws/voice` - WebSocket para streaming real-time

---

## 📂 Arquitectura

### Estructura del Proyecto

```
A.R.C.A-LLM/
├── src/
│   ├── domain/                 # Rich Domain Models (DDD)
│   │   ├── conversation.py    # Aggregate Root
│   │   └── message.py         # Value Object
│   │
│   ├── application/            # Application Services
│   │   ├── conversation_service.py
│   │   └── voice_assistant_service.py
│   │
│   ├── infrastructure/         # Technical Implementations
│   │   ├── llm/
│   │   │   └── lm_studio_client.py
│   │   ├── stt/
│   │   │   └── whisper_client.py
│   │   └── tts/
│   │       └── pyttsx3_client.py
│   │
│   ├── api/                    # Presentation Layer (FastAPI)
│   │   ├── main.py
│   │   ├── models.py
│   │   └── routes/
│   │       └── voice_routes.py
│   │
│   ├── frontend/               # Web Interface
│   │   ├── templates/
│   │   │   └── index.html
│   │   └── static/
│   │       ├── css/
│   │       │   └── style.css
│   │       └── js/
│   │           └── voice-interface.js
│   │
│   └── config.py               # Configuration Management
│
├── tests/                      # Unit & Integration Tests
├── docs/                       # Documentation
├── diagrams/                   # Architecture Diagrams
├── requirements.txt
└── README.md
```

### Pipeline de Procesamiento

```
[Usuario habla] 
    ↓
[MediaRecorder captura audio]
    ↓
[POST /api/voice/process]
    ↓
[Whisper STT] → Texto transcrito
    ↓
[Conversation + LLM] → Respuesta con memoria
    ↓
[pyttsx3 TTS] → Audio sintético
    ↓
[Response con audio bytes]
    ↓
[Auto-reproducción en navegador]
```

---

## 🎯 API Endpoints

### `POST /api/voice/process`
Procesar audio de voz y retornar respuesta.

**Request:**
- `audio`: File (WAV, WEBM, MP3)
- `session_id`: String (optional, UUID)
- `language`: String (default: "es")

**Response:**
- Audio WAV (binary)
- Headers con transcripción, respuesta, latencias

### `POST /api/text/process`
Procesar texto sin audio (para testing).

**Request:**
```json
{
  "text": "Hola, cómo estás?",
  "session_id": "optional-uuid"
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "response_text": "Hola! Muy bien...",
  "latency": {"llm": 1.2, "tts": 0.4, "total": 1.6}
}
```

### `GET /api/conversation/{session_id}`
Obtener historial completo de conversación.

### `DELETE /api/conversation/{session_id}`
Limpiar historial de conversación.

### `GET /health`
Health check de todos los componentes.

---

## ⚙️ Configuración Avanzada

### Optimizar Latencia

**Whisper más rápido:**
```env
WHISPER_MODEL=tiny  # Menos preciso pero 3x más rápido
```

**LLM respuestas más cortas:**
```env
LLM_MAX_TOKENS=100  # Respuestas más concisas
LLM_TEMPERATURE=0.5  # Menos creativo, más directo
```

### Usar GPU (si disponible)

```env
WHISPER_DEVICE=cuda
WHISPER_COMPUTE_TYPE=float16
```

---

## 🧪 Testing

```bash
# Ejecutar tests
pytest tests/ -v

# Con coverage
pytest tests/ --cov=src --cov-report=html

# Test específico
pytest tests/test_conversation_memory.py -v
```

---

## 📊 Ejemplo de Conversación

```
Usuario: "Hola, cómo estás? Me llamo Adrian"
A.R.C.A: "Hola Adrian! Muy bien, gracias. ¿En qué puedo ayudarte hoy?"

Usuario: "Qué día es hoy?"
A.R.C.A: "Hoy es viernes 31 de octubre de 2025."

Usuario: "Recuerdas mi nombre?"
A.R.C.A: "Sí, claro! Te llamas Adrian. ¿Hay algo más en lo que pueda ayudarte?"
```

---

## 🔧 Troubleshooting

### Error: "LM Studio connection refused"
- Verificar que LM Studio está corriendo
- Verificar puerto 1234 está libre
- Verificar modelo está cargado

### Error: "Microphone access denied"
- Dar permisos de micrófono al navegador
- HTTPS requerido (o localhost)

### Audio muy robótico
- Ajustar `TTS_RATE` (150-200)
- Considerar upgrade a Coqui TTS (futuro)

### Latencia alta
- Usar `WHISPER_MODEL=tiny`
- Reducir `LLM_MAX_TOKENS`
- Verificar CPU/GPU disponible

---

## 🚧 Roadmap

- [ ] WebSocket streaming para latencia ultra-baja
- [ ] Persistencia de conversaciones (SQLite)
- [ ] Múltiples voces TTS
- [ ] Upgrade a Coqui TTS para mejor calidad
- [ ] Multi-idioma UI
- [ ] Docker deployment
- [ ] Análisis de sentimiento

---

## 📄 Licencia

MIT License - Ver LICENSE file

---

## 👨‍💻 Autor

Proyecto A.R.C.A LLM - Advanced Voice Conversational Assistant

---

## 🙏 Agradecimientos

- **Whisper** (OpenAI) - Speech-to-Text
- **LM Studio** - Local LLM serving
- **FastAPI** - Modern web framework
- **pyttsx3** - Text-to-Speech

---

**¿Listo para hablar con A.R.C.A? 🎤🤖**

