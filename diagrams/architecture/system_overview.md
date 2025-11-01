# System Overview - A.R.C.A LLM Architecture

**Documento:** Arquitectura de alto nivel del sistema  
**Fecha:** 2025-10-31  
**Versión:** 1.0

---

## 🏗️ Arquitectura General

A.R.C.A LLM está diseñado siguiendo principios de **Domain-Driven Design** con separación clara de capas.

```
┌──────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                         │
│                          (FastAPI + Web UI)                        │
├────────────────────────────────┬─────────────────────────────────┤
│        Frontend (Web)          │         API (FastAPI)           │
│  • HTML/CSS/JS                 │  • REST Endpoints               │
│  • MediaRecorder               │  • Request Validation           │
│  • Voice Interface             │  • Response Formatting          │
└────────────────────────────────┴─────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER                           │
│                    (Business Logic Services)                       │
├────────────────────────────────┬─────────────────────────────────┤
│    ConversationService         │   VoiceAssistantService         │
│  • Session Management          │  • STT → LLM → TTS Pipeline     │
│  • Memory Management           │  • Orchestration                │
│  • CRUD Operations             │  • Latency Metrics              │
└────────────────────────────────┴─────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│                          DOMAIN LAYER                              │
│                      (Rich Domain Models)                          │
├────────────────────────────────┬─────────────────────────────────┤
│    Conversation                │         Message                 │
│  • Aggregate Root              │  • Value Object                 │
│  • Business Rules              │  • Immutable                    │
│  • Invariants                  │  • Factory Methods              │
└────────────────────────────────┴─────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│                      INFRASTRUCTURE LAYER                          │
│                  (Technical Implementations)                       │
├───────────────────┬───────────────────┬─────────────────────────┤
│  WhisperSTT       │   LMStudioClient  │   Pyttsx3TTS           │
│  • faster-whisper │   • OpenAI SDK    │   • pyttsx3            │
│  • Async wrapper  │   • Local LLM     │   • Threading          │
│  • VAD filtering  │   • Health check  │   • File output        │
└───────────────────┴───────────────────┴─────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│                        EXTERNAL SERVICES                           │
│                       (Local Services)                             │
├────────────────────────────────────────────────────────────────────┤
│  • LM Studio (localhost:1234)                                     │
│  • Whisper Models (downloaded locally)                            │
│  • System TTS Voices                                              │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow: Voice Conversation Pipeline

```
[Usuario]
   │
   │ 1. Presiona botón micrófono
   ▼
[Browser: MediaRecorder]
   │
   │ 2. Graba audio → Blob (WEBM)
   ▼
[POST /api/voice/process]
   │
   │ 3. FormData con audio bytes
   ▼
[VoiceAssistantService]
   │
   ├──► 4a. STT: WhisperClient
   │         └─► faster-whisper model
   │              └─► Transcribed Text
   │
   ├──► 4b. Memory: ConversationService
   │         └─► Add user message
   │              └─► Get full history (context)
   │
   ├──► 4c. LLM: LMStudioClient
   │         └─► OpenAI SDK → LM Studio (local)
   │              └─► Generate response with context
   │
   ├──► 4d. Memory: ConversationService
   │         └─► Add assistant message
   │
   └──► 4e. TTS: Pyttsx3Client
             └─► pyttsx3 engine
                  └─► Audio WAV bytes
   │
   │ 5. Return Response
   ▼
[Browser]
   │
   ├──► 6a. Display transcribed text (user bubble)
   ├──► 6b. Display response text (assistant bubble)
   └──► 6c. Auto-play audio response
   │
   ▼
[Usuario escucha respuesta]
```

---

## 🧠 Memory Management Architecture

```
┌─────────────────────────────────────────────────┐
│          ConversationService                     │
│  (Application Layer - Session Manager)          │
├─────────────────────────────────────────────────┤
│                                                  │
│  conversations: Dict[UUID, Conversation]        │
│                                                  │
│  session_1 ──► Conversation                     │
│                  │                               │
│                  ├─ Message (system)            │
│                  ├─ Message (user): "Hola..."   │
│                  ├─ Message (assistant): "..."  │
│                  ├─ Message (user): "..."       │
│                  └─ Message (assistant): "..."  │
│                                                  │
│  session_2 ──► Conversation                     │
│                  └─ Messages...                 │
│                                                  │
│  session_3 ──► Conversation                     │
│                  └─ Messages...                 │
│                                                  │
└─────────────────────────────────────────────────┘

Key Features:
• Each session maintains independent conversation
• Full history retained in memory (no truncation by default)
• Optional max_messages limit per conversation
• System message preserved during clear operations
• Thread-safe for concurrent requests
```

---

## 📦 Component Responsibilities

### Domain Layer
- **Purpose**: Business logic and invariants
- **Responsibility**: Define core entities and rules
- **Examples**:
  - `Conversation`: Aggregate root managing message collection
  - `Message`: Immutable value object
- **Dependencies**: None (pure domain)

### Application Layer
- **Purpose**: Orchestrate use cases
- **Responsibility**: Coordinate domain and infrastructure
- **Examples**:
  - `VoiceAssistantService`: Full pipeline orchestration
  - `ConversationService`: Session and memory management
- **Dependencies**: Domain + Infrastructure

### Infrastructure Layer
- **Purpose**: Technical implementations
- **Responsibility**: External service integration
- **Examples**:
  - `WhisperSTTClient`: Speech-to-text wrapper
  - `LMStudioClient`: LLM communication
  - `Pyttsx3TTSClient`: Text-to-speech wrapper
- **Dependencies**: External libraries

### Presentation Layer
- **Purpose**: User interface and API
- **Responsibility**: HTTP handling and UI rendering
- **Examples**:
  - FastAPI app and routes
  - HTML/CSS/JS frontend
- **Dependencies**: Application layer

---

## ⚡ Performance Optimizations

### Latency Reduction Strategies

1. **Async/Await Everywhere**
   - All services are async
   - ThreadPoolExecutor for CPU-bound tasks (Whisper, TTS)
   - Non-blocking IO

2. **Lazy Loading**
   - Whisper model loads on first use
   - TTS engine initialized per-request

3. **Model Selection**
   - Whisper `base` model (balance speed/accuracy)
   - Configurable to `tiny` for max speed
   - LLM max_tokens=150 for faster generation

4. **Audio Processing**
   - 16kHz sample rate (optimal for Whisper)
   - Mono channel (reduces data size)
   - VAD filtering to remove silence

5. **Parallel Operations**
   - Multiple conversations handled concurrently
   - FastAPI with uvicorn workers

---

## 🔒 Security Considerations

### Current Implementation
- **All Local**: No data leaves the machine
- **No Authentication**: Single-user system
- **No Persistence**: Conversations cleared on restart
- **HTTP Only**: Local network only (localhost)

### For Production
- Add authentication (API keys, OAuth)
- Add HTTPS support
- Rate limiting
- Input validation and sanitization
- Conversation persistence with encryption

---

## 📊 Monitoring & Observability

### Current Implementation
- **Logging**: Loguru with configurable levels
- **Metrics**: Latency per pipeline stage
- **Health Checks**: LLM and TTS connectivity

### Metrics Tracked
- STT latency (seconds)
- LLM latency (seconds)
- TTS latency (seconds)
- Total pipeline latency (seconds)
- Active conversation count

---

## 🔮 Future Architecture Enhancements

### WebSocket Streaming
```
[Browser] ←──WebSocket──► [FastAPI]
    │                          │
    │ Stream audio chunks ──►  │
    │                          ├─► STT (incremental)
    │                          ├─► LLM (streaming)
    │                          └─► TTS (incremental)
    │ ◄── Stream response      │
```

### Database Persistence
```
[ConversationService]
         │
         ▼
   [Repository]
         │
         ▼
    [SQLite/PostgreSQL]
         │
    Conversations
    Messages
    Users
```

---

**Architecture designed for:**
- ✅ Low latency (< 3s total)
- ✅ Offline operation
- ✅ Maintainability (DDD)
- ✅ Testability (mocked dependencies)
- ✅ Extensibility (pluggable components)

