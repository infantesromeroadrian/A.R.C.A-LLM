# BACKLOG - Pending Tickets

---

## TICKET-002: [UI] Implement Base OrbeWindow Class

**Category:** UI  
**Priority:** High  
**Status:** Backlog  
**Estimated Effort:** 2h  
**Dependencies:** TICKET-001

### Description
Crear la ventana principal de Tkinter con Canvas para el orbe Jarvis.

### Acceptance Criteria
- [ ] Clase `OrbeWindow` creada con Tkinter
- [ ] Canvas configurado (800x800px, fondo negro)
- [ ] Orbe central dibujado con create_oval()
- [ ] Ventana sin bordes (overrideredirect)
- [ ] Ventana siempre al frente (topmost)
- [ ] Botón de cerrar (Esc o click derecho)

### Technical Details
**Files to create:**
- `src/frontend_tkinter/orbe_window.py`

**Key classes:**
- `OrbeWindow` - Main window class

---

## TICKET-003: [UI] Add Animation Engine

**Category:** UI  
**Priority:** High  
**Status:** Backlog  
**Estimated Effort:** 3h  
**Dependencies:** TICKET-002

### Description
Implementar motor de animación para transiciones suaves del orbe.

### Acceptance Criteria
- [ ] AnimationEngine class con after() loop
- [ ] Smooth transitions entre estados
- [ ] FPS control (30-60 FPS)
- [ ] Movimiento circular del orbe
- [ ] Efecto breathing (pulsación suave)
- [ ] Sin flicker ni lag visual

### Technical Details
**Files to create:**
- `src/frontend_tkinter/animation_engine.py`

**Key functions:**
- `update_animation()` - Main loop
- `apply_circular_motion()`
- `apply_breathing_effect()`

---

## TICKET-004: [UI] Implement State-Based Animations

**Category:** UI  
**Priority:** High  
**Status:** Backlog  
**Estimated Effort:** 2h  
**Dependencies:** TICKET-003

### Description
Crear animaciones específicas para cada estado del asistente.

### Acceptance Criteria
- [ ] Estado IDLE: Pulsación suave, color azul
- [ ] Estado LISTENING: Ondas expansivas, color verde
- [ ] Estado PROCESSING: Rotación rápida, color morado
- [ ] Estado SPEAKING: Pulsación sincronizada, color cyan
- [ ] Transiciones suaves entre estados

### Technical Details
**Files to create:**
- `src/frontend_tkinter/orb_states.py`

**States enum:**
- IDLE, LISTENING, PROCESSING, SPEAKING

---

## TICKET-005: [INTEGRATION] Integrate with VoiceAssistantService

**Category:** Integration  
**Priority:** High  
**Status:** Backlog  
**Estimated Effort:** 2h  
**Dependencies:** TICKET-004

### Description
Conectar interfaz Tkinter con el pipeline STT→LLM→TTS existente.

### Acceptance Criteria
- [ ] Integración con VoiceAssistantService
- [ ] Click en orbe inicia grabación
- [ ] Release del click procesa audio
- [ ] Estados se actualizan según pipeline
- [ ] Respuesta se reproduce automáticamente
- [ ] Memoria conversacional funciona

### Technical Details
**Files to create:**
- `src/frontend_tkinter/voice_controller.py`

**Integration points:**
- VoiceAssistantService (existente)
- ConversationService (existente)
- Audio recording/playback

---

## TICKET-006: [UI] Add Glow/Pulse Effects

**Category:** UI  
**Priority:** Medium  
**Status:** Backlog  
**Estimated Effort:** 2h  
**Dependencies:** TICKET-003

### Description
Agregar efectos visuales de glow y pulso para efecto Jarvis premium.

### Acceptance Criteria
- [ ] Efecto glow con círculos concéntricos
- [ ] Gradiente radial desde centro
- [ ] Colores configurables
- [ ] Performance >30 FPS con efectos

### Technical Details
**Files to modify:**
- `src/frontend_tkinter/animation_engine.py`

**Techniques:**
- Múltiples overlapping circles con alpha
- Color interpolation

---

## TICKET-007: [INTEGRATION] Add Audio Threading

**Category:** Integration  
**Priority:** Medium  
**Status:** Backlog  
**Estimated Effort:** 2h  
**Dependencies:** TICKET-005

### Description
Implementar threading para que audio no bloquee UI animations.

### Acceptance Criteria
- [ ] Audio processing en thread separado
- [ ] UI permanece responsive durante procesamiento
- [ ] Callbacks thread-safe para actualizar estados
- [ ] Cleanup correcto de threads
- [ ] No race conditions

### Technical Details
**Files to create:**
- `src/frontend_tkinter/audio_thread_manager.py`

**Key libraries:**
- threading
- queue (para comunicación thread-safe)

---

## TICKET-008: [TEST] Unit Tests for Tkinter Components

**Category:** Testing  
**Priority:** Medium  
**Status:** Backlog  
**Estimated Effort:** 2h  
**Dependencies:** TICKET-004

### Description
Crear tests para componentes de Tkinter.

### Acceptance Criteria
- [ ] Tests para OrbeWindow
- [ ] Tests para AnimationEngine
- [ ] Tests para state transitions
- [ ] Coverage >80% de frontend_tkinter/

### Technical Details
**Files to create:**
- `tests/unit/frontend_tkinter/test_orbe_window.py`
- `tests/unit/frontend_tkinter/test_animation_engine.py`

---

## TICKET-009: [TEST] Integration Tests UI + Pipeline

**Category:** Testing  
**Priority:** Medium  
**Status:** Backlog  
**Estimated Effort:** 1h  
**Dependencies:** TICKET-007

### Description
Tests de integración completa UI → Pipeline → Audio.

### Acceptance Criteria
- [ ] Test end-to-end con mock de audio
- [ ] Verificar estados se actualizan correctamente
- [ ] Verificar threading funciona sin deadlocks

### Technical Details
**Files to create:**
- `tests/integration/test_tkinter_voice_pipeline.py`

---

## TICKET-010: [DOC] Update Documentation for Tkinter UI

**Category:** Documentation  
**Priority:** Low  
**Status:** Backlog  
**Estimated Effort:** 1h  
**Dependencies:** TICKET-009

### Description
Documentar nueva interfaz Tkinter en README y docs.

### Acceptance Criteria
- [ ] README.md actualizado con opción Tkinter
- [ ] Screenshots del orbe Jarvis
- [ ] Instrucciones de uso
- [ ] Comparison web vs desktop UI

### Technical Details
**Files to modify:**
- `README.md`
- `docs/README.md`

**Files to create:**
- `docs/tkinter/TKINTER_UI_GUIDE.md`

---

**Total Tickets in Backlog:** 9

