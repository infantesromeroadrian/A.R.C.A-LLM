# Architecture Decision Record (ADR) - A.R.C.A LLM

**Fecha:** 2025-10-31  
**Status:** ✅ Approved  
**Decisor:** Development Team

---

## Contexto

Se requiere construir un sistema de asistente conversacional por voz que:
- Funcione completamente offline
- Mantenga memoria conversacional completa
- Tenga latencia < 3 segundos
- Sea fácil de mantener y extender

---

## Decisiones Arquitectónicas

### 1. Domain-Driven Design (DDD)

**Decisión:** Usar arquitectura DDD con capas bien definidas

**Razones:**
- ✅ Separación clara de responsabilidades
- ✅ Fácil de testear (domain independiente)
- ✅ Fácil de mantener y evolucionar
- ✅ Business logic encapsulada en dominio

**Alternativas consideradas:**
- ❌ Arquitectura monolítica simple: Difícil de mantener a largo plazo
- ❌ Microservicios: Demasiado complejo para un sistema local

**Impacto:**
- Estructura de directorios clara
- Tests más fáciles de escribir
- Cambios futuros más seguros

---

### 2. Speech-to-Text: faster-whisper

**Decisión:** Usar faster-whisper (local) en lugar de APIs cloud

**Razones:**
- ✅ Completamente offline
- ✅ Sin costos de API
- ✅ Baja latencia con modelo `base`
- ✅ Excelente precisión en español
- ✅ Optimizado (CTranslate2)

**Alternativas consideradas:**
- ❌ OpenAI Whisper API: Requiere internet, costos
- ❌ Google Speech-to-Text: Requiere internet, costos
- ❌ Whisper original: Más lento que faster-whisper

**Impacto:**
- Primera ejecución descarga modelo (~150MB)
- Requiere RAM (~1GB para modelo base)
- Latencia ~1 segundo para 10s de audio

---

### 3. LLM: LM Studio con modelo local

**Decisión:** Usar LM Studio como servidor local

**Razones:**
- ✅ Completamente offline
- ✅ Sin costos de API
- ✅ Interfaz compatible con OpenAI SDK
- ✅ Usuario puede elegir modelo
- ✅ Fácil de configurar

**Alternativas consideradas:**
- ❌ llama.cpp directo: Más complejo de configurar
- ❌ Ollama: Requiere instalación adicional
- ❌ OpenAI API: Requiere internet, costos altos

**Impacto:**
- Usuario debe tener LM Studio instalado
- Requiere modelo descargado (~10GB+)
- Requiere GPU o CPU potente

---

### 4. Text-to-Speech: pyttsx3

**Decisión:** Usar pyttsx3 (motor local) en lugar de TTS cloud

**Razones:**
- ✅ Completamente offline
- ✅ Sin costos
- ✅ Baja latencia (~0.5s)
- ✅ Fácil de instalar
- ✅ Compatible con Windows/Mac/Linux

**Alternativas consideradas:**
- ❌ OpenAI TTS API: Requiere internet, costos
- ❌ ElevenLabs: Requiere internet, costos altos
- ❌ Coqui TTS: Más complejo, pero mejor calidad (futuro)

**Impacto:**
- Voz robótica (calidad media)
- Pero suficiente para MVP
- Posible upgrade a Coqui TTS futuro

---

### 5. Memoria Conversacional: In-Memory Storage

**Decisión:** Almacenar conversaciones en memoria RAM (dict)

**Razones:**
- ✅ Simplicidad (MVP)
- ✅ Latencia mínima
- ✅ No requiere base de datos
- ✅ Suficiente para sesiones cortas

**Alternativas consideradas:**
- ❌ SQLite: Overhead innecesario para MVP
- ❌ Redis: Requiere servicio adicional

**Impacto:**
- Conversaciones se pierden al reiniciar
- RAM limitada para conversaciones muy largas
- Fácil migrar a DB después

---

### 6. Web Framework: FastAPI

**Decisión:** Usar FastAPI para API y servir frontend

**Razones:**
- ✅ Async nativo (crítico para latencia)
- ✅ Type hints y validación automática
- ✅ Documentación auto-generada (Swagger)
- ✅ Rápido y moderno
- ✅ CORS fácil de configurar

**Alternativas consideradas:**
- ❌ Flask: No async nativo
- ❌ Django: Demasiado pesado para este caso

**Impacto:**
- Excelente DX (developer experience)
- Fácil de extender con nuevos endpoints
- Performance excelente

---

### 7. Frontend: Vanilla HTML/CSS/JS

**Decisión:** No usar framework frontend (React, Vue, etc.)

**Razones:**
- ✅ Simplicidad (no build step)
- ✅ Rápido de desarrollar para MVP
- ✅ Fácil de mantener
- ✅ MediaRecorder API nativa

**Alternativas consideradas:**
- ❌ React: Overhead innecesario para UI simple
- ❌ Vue: Similar a React

**Impacto:**
- Desarrollo más rápido
- Menos dependencias
- Fácil de entender

---

### 8. Async/Await Completo

**Decisión:** Usar async/await en todos los servicios

**Razones:**
- ✅ Latencia mínima (no blocking)
- ✅ Mejor utilización de CPU
- ✅ Múltiples requests concurrentes

**Alternativas consideradas:**
- ❌ Síncrono: Blocking, latencia alta

**Impacto:**
- ThreadPoolExecutor para pyttsx3 (síncrono)
- Código más complejo pero performance superior

---

### 9. Configuration: pydantic-settings

**Decisión:** Usar pydantic-settings para configuración

**Razones:**
- ✅ Validación automática de tipos
- ✅ Variables de entorno
- ✅ Type hints
- ✅ Fácil de testear

**Alternativas consideradas:**
- ❌ python-decouple: Menos features
- ❌ Config manual: Sin validación

**Impacto:**
- Errores de configuración detectados al startup
- Configuración type-safe

---

### 10. Testing: pytest con mocks

**Decisión:** Usar pytest con unittest.mock

**Razones:**
- ✅ No requiere servicios externos corriendo
- ✅ Tests rápidos
- ✅ Fácil de escribir

**Alternativas consideradas:**
- ❌ Integration tests completos: Requieren LM Studio corriendo

**Impacto:**
- Tests unitarios completos para domain/application
- Integration tests opcionales

---

## Resumen de Trade-offs

| Aspecto | Beneficio | Costo |
|---------|-----------|-------|
| Offline completo | Privacidad, $0 costos | Requiere hardware local potente |
| DDD Architecture | Mantenibilidad | Más archivos/complejidad inicial |
| In-Memory storage | Latencia mínima | Sin persistencia entre reinicios |
| pyttsx3 TTS | Offline, gratis | Calidad de voz media |
| Whisper base | Balance speed/accuracy | Primera descarga ~150MB |

---

## Próximas Decisiones Arquitectónicas

### Corto Plazo
- [ ] WebSocket vs Polling para streaming
- [ ] Persistencia: SQLite vs PostgreSQL
- [ ] Upgrade TTS: Coqui vs otros

### Largo Plazo
- [ ] Multi-tenant architecture
- [ ] Distributed deployment
- [ ] Cloud-hybrid option

---

**Decision Status:** ✅ Todas las decisiones implementadas en MVP

