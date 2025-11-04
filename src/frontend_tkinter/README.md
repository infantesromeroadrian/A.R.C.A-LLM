# Frontend Tkinter - Jarvis Orb Interface

**Status:** 🔄 En Desarrollo  
**Branch:** frontendTkinter  
**Session:** 2025-11-04  

---

## 🎨 Overview

Interfaz desktop con orbe animado estilo Jarvis/Iron Man para A.R.C.A-LLM.

**Características:**
- ✨ Orbe animado con efectos glow
- 🎤 Activación por click
- 🌈 4 estados visuales (idle, listening, processing, speaking)
- 🖥️ Ventana siempre al frente
- ⚡ 60 FPS smooth animations

---

## 🏗️ Architecture

```
src/frontend_tkinter/
├── __init__.py                  # Module exports
├── orbe_window.py               # ✅ Main window (TICKET-001/002 completed)
├── animation_engine.py          # ⏳ Animation system (TICKET-003)
├── orb_states.py               # ⏳ State management (TICKET-004)
├── voice_controller.py         # ⏳ Voice integration (TICKET-005)
└── audio_thread_manager.py     # ⏳ Audio threading (TICKET-007)
```

---

## 🚀 Quick Start

### Run Standalone (Testing)

```bash
# Desde raíz del proyecto
python -m src.frontend_tkinter.orbe_window

# Verás el orbe animado
# Click para simular estados
```

### Run with Voice Pipeline (Futuro)

```bash
# Por implementar en TICKET-005
python run_arca_tkinter.py
```

---

## 🎯 Components

### OrbeWindow (✅ Implemented)

Ventana principal con Canvas y orbe animado.

**Features:**
- Canvas 800x800px
- Orbe central con radio base 80px
- 5 glow layers para efecto luminoso
- Estados: IDLE, LISTENING, PROCESSING, SPEAKING
- Animaciones: breathing, pulsing
- Event handling: click, release, Esc, right-click

**Usage:**
```python
from src.frontend_tkinter import OrbeWindow, OrbState

def on_click():
    print("Orb clicked!")
    window.set_state(OrbState.LISTENING)

def on_release():
    print("Processing...")
    window.set_state(OrbState.PROCESSING)

window = OrbeWindow(
    on_click_callback=on_click,
    on_release_callback=on_release
)

window.run()
```

---

## 🎨 Animation System

### States

| State | Color | Animation | Use Case |
|-------|-------|-----------|----------|
| **IDLE** | Cyan (#00D9FF) | Breathing suave (0.5Hz) | Esperando input |
| **LISTENING** | Green (#00FF41) | Pulsación rápida (2Hz) | Grabando audio |
| **PROCESSING** | Purple (#B026FF) | Pulsación muy rápida (3Hz) | Procesando LLM |
| **SPEAKING** | Cyan (#00D9FF) | Pulsación sync (futuro) | Reproduciendo TTS |

### Animation Techniques

**Breathing Effect:**
```python
size = base_size + amplitude * sin(time * frequency * 2π)
```

**Glow Effect:**
- 5 círculos concéntricos
- Radio incrementado en 15px por layer
- Outline color según estado

---

## 🔧 Configuration

### Window

```python
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
BACKGROUND_COLOR = "#000000"  # Black
```

### Orb

```python
ORB_CENTER_X = 400
ORB_CENTER_Y = 400
ORB_BASE_RADIUS = 80
```

### Animation

```python
FPS = 60
FRAME_DELAY = 16  # ms (1000/60)
```

---

## 📋 Tickets Status

| Ticket | Component | Status | Progress |
|--------|-----------|--------|----------|
| TICKET-001 | Setup structure | ✅ | 100% |
| TICKET-002 | OrbeWindow base | ✅ | 100% |
| TICKET-003 | AnimationEngine | ⏳ | 0% |
| TICKET-004 | State animations | ⏳ | 0% |
| TICKET-005 | Voice integration | ⏳ | 0% |
| TICKET-006 | Glow effects | ⏳ | 0% |
| TICKET-007 | Audio threading | ⏳ | 0% |
| TICKET-008 | Unit tests | ⏳ | 0% |
| TICKET-009 | Integration tests | ⏳ | 0% |
| TICKET-010 | Documentation | ⏳ | 10% |

---

## 🧪 Testing

```bash
# Unit tests (cuando estén implementados)
pytest tests/unit/frontend_tkinter/ -v

# Integration tests
pytest tests/integration/test_tkinter_voice_pipeline.py -v

# Manual testing
python -m src.frontend_tkinter.orbe_window
```

---

## 📚 Documentation

- **Session Log:** `historyMD/2025-11-04_session-001.md`
- **Architecture Decision:** `historyMD/decisions/2025-11-04_001_tkinter-jarvis-interface.md`
- **Tickets:** `tickets/`

---

## 🔮 Future Enhancements

- [ ] Audio amplitude visualization (TICKET-005)
- [ ] Voice waveform around orb
- [ ] Particle effects on transitions
- [ ] Customizable themes
- [ ] Settings panel
- [ ] Drag & drop window positioning
- [ ] Multi-monitor support
- [ ] Transparency/opacity controls

---

## 🐛 Known Issues

- None yet (MVP stage)

---

## 💡 Tips

1. **Performance:** If FPS drops, reduce glow layers
2. **Testing:** Use standalone mode for UI testing
3. **Colors:** Edit STATE_COLORS dict in OrbeWindow
4. **Size:** Adjust ORB_BASE_RADIUS for larger/smaller orb

---

**Created:** 2025-11-04  
**Last Updated:** 2025-11-04  
**Maintained By:** AI Assistant + Adrian Infantes

