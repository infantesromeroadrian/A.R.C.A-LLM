# 🔌 A.R.C.A LLM - API Documentation

Documentación completa de la API para integración con frontend.

---

## 🌐 Base URL

- **Local Development**: `http://localhost:8000`
- **Docker**: `http://localhost:8000`

---

## 📡 Endpoints

### 1. Health Check

**Endpoint**: `GET /api/health`

**Description**: Verificar que el servidor está funcionando correctamente.

**Response**:
```json
{
  "status": "healthy",
  "service": "A.R.C.A LLM Voice Assistant",
  "version": "1.0.0"
}
```

**Ejemplo**:
```bash
curl http://localhost:8000/api/health
```

---

### 2. Process Voice (Main Endpoint)

**Endpoint**: `POST /api/voice/process`

**Description**: Procesa audio del usuario y retorna respuesta del LLM en audio.

**Request**:
- **Content-Type**: `multipart/form-data`
- **Body**:
  - `audio`: Audio file (WAV, MP3, WEBM, etc.)
  - `conversation_id`: (Optional) UUID de conversación existente

**Request Example**:
```javascript
const formData = new FormData();
formData.append('audio', audioBlob, 'voice.webm');
formData.append('conversation_id', conversationId); // Optional

fetch('http://localhost:8000/api/voice/process', {
  method: 'POST',
  body: formData
})
```

**Response**:
- **Content-Type**: `audio/wav`
- **Headers**:
  - `X-Conversation-Id`: UUID de la conversación (Base64 encoded)
  - `X-Transcribed-Text`: Texto transcrito del audio del usuario (Base64 encoded)
  - `X-Response-Text`: Respuesta del LLM en texto (Base64 encoded)

**Headers Decoding**:
```javascript
// Decodificar headers Base64
const conversationId = atob(response.headers.get('X-Conversation-Id'));
const transcribedText = atob(response.headers.get('X-Transcribed-Text'));
const responseText = atob(response.headers.get('X-Response-Text'));
```

**Response Body**: Binary audio (WAV format) listo para reproducir.

**Response Example**:
```javascript
const response = await fetch('http://localhost:8000/api/voice/process', {
  method: 'POST',
  body: formData
});

// Obtener metadata de headers
const conversationId = atob(response.headers.get('X-Conversation-Id'));
const transcribedText = atob(response.headers.get('X-Transcribed-Text'));
const llmResponse = atob(response.headers.get('X-Response-Text'));

// Obtener audio
const audioBlob = await response.blob();
const audioUrl = URL.createObjectURL(audioBlob);

// Reproducir audio
const audio = new Audio(audioUrl);
audio.play();
```

**Error Responses**:
```json
// 400 Bad Request
{
  "detail": "No audio file provided"
}

// 500 Internal Server Error
{
  "detail": "Error processing voice: <error message>"
}
```

---

### 3. Get Conversation History

**Endpoint**: `GET /api/voice/conversation/{conversation_id}`

**Description**: Obtener historial completo de una conversación.

**Parameters**:
- `conversation_id`: UUID de la conversación

**Response**:
```json
{
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "messages": [
    {
      "role": "user",
      "content": "Hola, ¿cómo estás?",
      "timestamp": "2025-11-01T12:00:00"
    },
    {
      "role": "assistant",
      "content": "Hola, estoy bien. ¿En qué puedo ayudarte?",
      "timestamp": "2025-11-01T12:00:02"
    }
  ],
  "message_count": 2,
  "created_at": "2025-11-01T12:00:00"
}
```

---

### 4. Delete Conversation

**Endpoint**: `DELETE /api/voice/conversation/{conversation_id}`

**Description**: Eliminar una conversación y su historial.

**Parameters**:
- `conversation_id`: UUID de la conversación

**Response**:
```json
{
  "message": "Conversation deleted successfully",
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

---

## 🔄 WebSocket (Streaming Real-Time)

**Endpoint**: `WS /ws/voice`

**Description**: Conexión WebSocket para streaming de audio en tiempo real.

**Connection**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/voice');

ws.onopen = () => {
  console.log('WebSocket connected');
};

ws.onmessage = (event) => {
  // event.data contiene audio chunks o metadata JSON
  const data = JSON.parse(event.data);
  
  if (data.type === 'transcription') {
    console.log('Transcripción:', data.text);
  } else if (data.type === 'llm_response') {
    console.log('Respuesta LLM:', data.text);
  } else if (data.type === 'audio_chunk') {
    // Reproducir chunk de audio
    playAudioChunk(data.audio);
  }
};

// Enviar audio
ws.send(audioBlob);
```

---

## 🎤 Audio Format Specifications

### Supported Input Formats
- **WAV**: PCM 16-bit, mono/stereo
- **MP3**: Any bitrate
- **WEBM**: Opus codec (browser recording)
- **OGG**: Vorbis codec

### Output Format
- **Format**: WAV
- **Sample Rate**: 22050 Hz
- **Channels**: Mono
- **Bit Depth**: 16-bit PCM

---

## 🔐 CORS Configuration

El backend está configurado para aceptar requests desde:

```python
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:5173",  # Vite
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:5173"
]
```

Si el frontend usa otro puerto, agregar a `docker-compose.yml`:

```yaml
environment:
  - CORS_ORIGINS=["http://localhost:TU_PUERTO"]
```

---

## 🐳 Docker Integration

### Backend (A.R.C.A-LLM)

```yaml
# docker-compose.yml
services:
  arca-llm:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LM_STUDIO_URL=http://host.docker.internal:1234/v1
```

**Acceso desde frontend**:
```javascript
const API_URL = 'http://localhost:8000';
```

### Full Stack con Docker Compose

Si quieren integrar backend + frontend en un solo docker-compose:

```yaml
version: '3.8'

services:
  # Backend - A.R.C.A LLM
  backend:
    build: ./A.R.C.A-LLM
    ports:
      - "8000:8000"
    environment:
      - LM_STUDIO_URL=http://host.docker.internal:1234/v1
  
  # Frontend - msmk-voice-assistant
  frontend:
    build: ./msmk-voice-assistant
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://backend:8000
    depends_on:
      - backend
```

---

## 📊 Request/Response Flow

```
User Audio (Browser)
    ↓
POST /api/voice/process (FormData with audio blob)
    ↓
Backend STT (Faster-Whisper)
    ↓
Backend LLM (LM Studio - Qwen3-4B)
    ↓
Backend TTS (pyttsx3 + espeak)
    ↓
Audio Response (WAV) + Headers (transcription, response text, conversation_id)
    ↓
Frontend (Play audio, display text, update UI)
```

---

## 🧪 Testing the API

### Test Health Endpoint
```bash
curl http://localhost:8000/api/health
```

### Test Voice Processing (con archivo de audio)
```bash
curl -X POST http://localhost:8000/api/voice/process \
  -F "audio=@test_audio.wav" \
  -o response.wav
```

### Test desde Frontend
```javascript
// Grabador de audio simple
navigator.mediaDevices.getUserMedia({ audio: true })
  .then(stream => {
    const mediaRecorder = new MediaRecorder(stream);
    const chunks = [];
    
    mediaRecorder.ondataavailable = e => chunks.push(e.data);
    
    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(chunks, { type: 'audio/webm' });
      
      const formData = new FormData();
      formData.append('audio', audioBlob, 'voice.webm');
      
      const response = await fetch('http://localhost:8000/api/voice/process', {
        method: 'POST',
        body: formData
      });
      
      const responseAudio = await response.blob();
      const audio = new Audio(URL.createObjectURL(responseAudio));
      audio.play();
    };
    
    mediaRecorder.start();
    setTimeout(() => mediaRecorder.stop(), 3000); // Grabar 3 segundos
  });
```

---

## ⚡ Performance Expectations

- **STT (Whisper Tiny)**: ~500ms para 3 segundos de audio
- **LLM (Qwen3-4B)**: ~1-2s para respuesta corta
- **TTS (pyttsx3)**: ~300ms para frase corta
- **Total Latency**: ~2-3 segundos (objetivo <3s)

---

## 🔧 Environment Variables

Variables que el frontend puede necesitar configurar:

```bash
# .env en frontend
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

---

## 📝 Notas para Integración

### Para nacho995 (Frontend Developer)

1. **URL Base**: `http://localhost:8000`
2. **Endpoint Principal**: `POST /api/voice/process`
3. **Headers Importantes**: Decodificar Base64 para `X-Transcribed-Text` y `X-Response-Text`
4. **Audio Format**: Enviar cualquier formato, recibir WAV
5. **Conversación**: Guardar `conversation_id` para mantener memoria
6. **CORS**: Ya configurado para puertos comunes de desarrollo

### Ejemplo de Integración Completa

Ver `src/frontend/static/js/voice-interface.js` para referencia de implementación funcional.

---

## 🚨 Troubleshooting

### "CORS Error"
- Verificar que el puerto del frontend esté en `CORS_ORIGINS`
- Agregar puerto a `docker-compose.yml` si es necesario

### "Connection Refused"
- Verificar que backend esté corriendo: `docker compose ps`
- Verificar puerto 8000 esté accesible

### "Audio no se reproduce"
- Verificar que el browser soporte `audio/wav`
- Verificar que el Blob se crea correctamente
- Check console para errores JavaScript

---

**Actualizado**: 2025-11-01  
**Versión**: 1.0.0  
**Contacto**: Para dudas sobre la API, coordinar con el equipo backend

