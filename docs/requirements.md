# Documento de Requirements - A.R.C.A LLM

**Proyecto:** A.R.C.A LLM (Advanced Reasoning Cognitive Architecture - Language Model with Memory)  
**Fecha:** 2025-10-31  
**Tipo:** Sistema de Asistente Conversacional por Voz  
**Estado:** Proyecto Nuevo - From Scratch

---

## 1. CONTEXTO DE NEGOCIO

### 1.1 Problema a Resolver
Crear un asistente de voz conversacional con IA que permita interacción natural mediante habla, manteniendo memoria completa de la conversación para un contexto continuo y coherente.

### 1.2 Objetivo Medible
- **Latencia Total:** < 3 segundos (desde audio input hasta audio output)
- **Precisión STT:** > 90% en español
- **Memoria Conversacional:** 100% de retención durante sesión activa
- **Disponibilidad:** Sistema offline funcional sin dependencias cloud

### 1.3 Usuarios Finales
- **Perfil:** Usuario individual (desarrollador/investigador)
- **Nivel Técnico:** Alto (capacidad de ejecutar localmente)
- **Idioma Principal:** Español
- **Conocimiento AI/ML:** Avanzado

### 1.4 Budget y Timeline
- **Budget:** $0 (100% offline, sin costos de API)
- **Timeline:** Implementación inicial 1 día (MVP funcional)
- **Tipo:** MVP con capacidad de producción local

---

## 2. DATOS

### 2.1 Tipo de Datos
- **Input:** Audio (voz del usuario) - formato WAV/WEBM
- **Procesamiento:** Texto transcrito + Historial conversacional
- **Output:** Audio sintético (respuesta del asistente)

### 2.2 Volumen de Datos
- **Audio Input:** ~10-30 segundos por mensaje (típico)
- **Historial:** Conversación completa en memoria (ilimitado durante sesión)
- **Almacenamiento:** En memoria RAM (no persistente entre reinicios)

### 2.3 Formato
- **Audio Input:** WEBM (navegador) → convertido a WAV 16kHz mono
- **Texto:** UTF-8 String
- **Audio Output:** WAV → convertido a formato reproducible web

### 2.4 Ubicación
- **Audio Temporal:** Memoria/Buffer (no persiste en disco)
- **Historial Conversacional:** Diccionario en memoria Python
- **Modelos:** faster-whisper descargado localmente

### 2.5 Calidad de Datos
- **Audio:** Calidad depende del micrófono del usuario
- **Transcripción:** Determinística (modelo Whisper)
- **No requiere labeling:** Sistema generativo

### 2.6 Colección Adicional
- No se requiere colección de datos
- Sistema usa modelos pre-entrenados (Whisper, LM Studio LLM)

### 2.7 Datos Estáticos vs Dinámicos
- **Dinámicos:** Conversación en tiempo real
- **Estáticos:** Modelos pre-entrenados

---

## 3. SOLUCIÓN AI/ML

### 3.1 Tipo de Problema
- **Speech-to-Text:** Transcripción de audio (modelo pre-entrenado Whisper)
- **Language Model:** Generación de texto conversacional (LLM local)
- **Text-to-Speech:** Síntesis de voz (pyttsx3)
- **Memoria Conversacional:** Gestión de contexto completo

### 3.2 Modelos Aplicables

**STT (Speech-to-Text):**
- **Modelo:** Whisper (OpenAI) via faster-whisper
- **Variante:** `base` (balance velocidad/precisión) o `tiny` (máxima velocidad)
- **Justificación:** Mejor modelo open-source para STT, soporte español excelente

**LLM (Language Model):**
- **Modelo:** qwen/qwen3-4b-2507
- **Servidor:** LM Studio (http://192.168.1.38:1234)
- **Parámetros:** 4B parámetros, optimizado para velocidad y conversación
- **Justificación:** Modelo local rápido y eficiente, excelente para español, sin costos

**TTS (Text-to-Speech):**
- **Modelo:** pyttsx3 (engine local)
- **Justificación:** Offline, gratuito, calidad aceptable, baja latencia

### 3.3 Métricas de Éxito
- **Latencia STT:** < 1 segundo para 10s de audio
- **Latencia LLM:** < 1.5 segundos para respuesta de 50 tokens
- **Latencia TTS:** < 0.5 segundos para 50 tokens
- **Latencia Total:** < 3 segundos end-to-end
- **Retención de Memoria:** 100% de mensajes previos durante sesión

### 3.4 Interpretabilidad
- No requerida (sistema conversacional)
- Transparencia en transcripción (mostrar texto transcrito)

### 3.5 Constraints del Modelo
- **Latencia Máxima:** 3 segundos total
- **Tamaño:** Modelos deben correr en GPU/CPU consumidor
- **Offline:** 100% offline, sin internet
- **Idioma:** Optimizado para español

---

## 4. ARQUITECTURA Y TECNOLOGÍAS

### 4.1 Lenguaje
- **Python 3.11+** (ecosistema completo)

### 4.2 Frameworks ML
- **faster-whisper:** STT local optimizado
- **OpenAI SDK:** Cliente para LM Studio (compatible)
- **pyttsx3:** TTS local

### 4.3 Deployment
- **Local Development:** localhost:8000
- **No Cloud:** Sistema completamente offline
- **Docker (opcional):** Para portabilidad futura

### 4.4 Infraestructura de Datos
- **En Memoria:** Diccionario Python para historial conversacional
- **No Database:** Sistema stateless entre reinicios
- **Sesiones:** Identificadas por session_id (UUID)

### 4.5 Orquestación
- **No requerida:** Sistema monolítico simple
- **Logging:** Loguru para debugging
- **Monitoring:** Logs de latencia por componente

### 4.6 Integraciones
- **LM Studio:** API REST local (port 1234)
- **Navegador:** MediaRecorder API para captura de audio
- **No integraciones externas**

---

## 5. SEGURIDAD Y COMPLIANCE

### 5.1 Datos Sensibles
- **Audio:** Conversaciones privadas del usuario
- **Texto:** Contenido conversacional personal
- **Mitigación:** Todo permanece local, nada enviado a cloud

### 5.2 Regulaciones
- **No aplican:** Sistema personal de uso local
- **GDPR:** N/A (sin almacenamiento persistente)

### 5.3 Encriptación
- **No requerida:** Sistema local sin red
- **Comunicación:** HTTP local (localhost)

### 5.4 Consideraciones Éticas
- **Privacidad:** Máxima (todo local)
- **Bias:** Depende del modelo LLM usado (sin intervención)
- **Transparency:** Usuario consciente del sistema local

---

## 6. MONITORING Y MAINTENANCE

### 6.1 Monitoreo
- **Logs:** Loguru para debugging
- **Métricas de Latencia:** Tiempo de cada componente (STT, LLM, TTS)
- **Health Check:** Endpoint `/health` para verificar servicios

### 6.2 Estrategia de Retraining
- **No aplica:** Modelos pre-entrenados
- **Actualización:** Cambiar modelos Whisper/LLM manualmente

### 6.3 Mantenimiento
- **Desarrollador:** Usuario mismo
- **Documentación:** README con instrucciones de uso
- **No training necesario:** Sistema auto-explicativo

---

## 7. ARQUITECTURA PROPUESTA

### 7.1 Componentes Principales

**Frontend (Web Interface):**
- HTML con botón de voz grande
- JavaScript MediaRecorder para audio capture
- Auto-reproducción de respuestas

**Backend (FastAPI):**
- API REST para procesamiento de voz
- WebSocket para streaming (opcional)
- Gestión de sesiones conversacionales

**Infrastructure Layer:**
- WhisperSTTClient: Transcripción con faster-whisper
- LMStudioClient: Generación con LLM local
- Pyttsx3TTSClient: Síntesis de voz

**Domain Layer:**
- Conversation (Aggregate): Gestiona memoria completa
- Message (Value Object): Mensajes inmutables

**Application Layer:**
- ConversationService: Gestión de memoria
- VoiceAssistantService: Orquestación pipeline completo

### 7.2 Flujo de Datos

```
[Usuario] → [Navegador: MediaRecorder]
    ↓
[POST /api/voice/process: audio bytes]
    ↓
[WhisperSTT] → Texto transcrito
    ↓
[ConversationService] → Agregar mensaje usuario + historial
    ↓
[LMStudioClient] → Generar respuesta con contexto completo
    ↓
[ConversationService] → Guardar respuesta en memoria
    ↓
[Pyttsx3TTS] → Convertir texto a audio
    ↓
[Response: audio bytes] → [Navegador: Auto-play]
```

---

## 8. RIESGOS IDENTIFICADOS

### Riesgo 1: Latencia Acumulada
- **Descripción:** STT + LLM + TTS puede exceder 3 segundos
- **Mitigación:** 
  - Usar Whisper modelo `tiny` (más rápido)
  - Limitar LLM max_tokens a 100-150
  - Pre-cargar motores al startup
  - Procesamiento async completo

### Riesgo 2: Calidad TTS con pyttsx3
- **Descripción:** pyttsx3 tiene voz robótica comparado con TTS modernos
- **Mitigación:** 
  - Ajustar rate y volume para mejor naturalidad
  - Opción futura: upgrade a Coqui TTS o VITS local

### Riesgo 3: Memoria RAM con Conversaciones Largas
- **Descripción:** Historial completo puede consumir mucha RAM
- **Mitigación:**
  - Implementar límite opcional de mensajes (ej: últimos 50)
  - Endpoint para limpiar memoria
  - Monitoreo de uso de memoria

### Riesgo 4: Dependencia de LM Studio
- **Descripción:** Requiere LM Studio corriendo en port 1234
- **Mitigación:**
  - Health check al startup
  - Error handling robusto
  - Instrucciones claras en README

---

## 9. FASES DEL PROYECTO

### Fase 1: Setup y Configuración (30 min)
- Crear estructura de directorios
- Configurar environment (.env)
- Actualizar requirements.txt
- Instalar dependencias

### Fase 2: Infrastructure Layer (1.5 horas)
- Implementar WhisperSTTClient
- Implementar LMStudioClient
- Implementar Pyttsx3TTSClient
- Tests unitarios de cada cliente

### Fase 3: Domain & Application Layers (1 hora)
- Crear domain models (Conversation, Message)
- Implementar ConversationService
- Implementar VoiceAssistantService
- Tests de memoria conversacional

### Fase 4: API & Frontend (1.5 horas)
- FastAPI app con routes
- Endpoints de voz
- Interfaz web con botón de voz
- JavaScript para MediaRecorder

### Fase 5: Testing & Optimization (1 hora)
- Tests de integración
- Optimización de latencia
- Logging y monitoring
- Documentation

**Duración Total Estimada:** 5-6 horas

---

## 10. CRITERIOS DE ACEPTACIÓN

- [ ] Usuario puede hablar presionando botón
- [ ] Audio se transcribe correctamente a texto
- [ ] LLM genera respuesta coherente
- [ ] Respuesta se convierte a audio
- [ ] Audio se reproduce automáticamente
- [ ] Memoria conversacional funciona (recuerda nombre, contexto previo)
- [ ] Latencia total < 3 segundos
- [ ] Interfaz web simple e intuitiva
- [ ] Sistema funciona completamente offline
- [ ] Tests passing con 90%+ coverage
- [ ] Documentación completa en README

---

**Estado:** ✅ Requirements Aprobados - Listo para Phase 2 (Diagramas)

