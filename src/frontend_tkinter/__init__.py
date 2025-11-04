"""
Frontend Tkinter - Jarvis-Style Orb Interface.

Interfaz desktop con orbe animado estilo Jarvis/Iron Man para A.R.C.A-LLM.

Components:
- OrbeWindow: Ventana principal con Canvas
- VoiceController: Integración con VoiceAssistantService via API ✅
- OrbState: Estados del orbe (idle, listening, processing, speaking)

Architecture:
- Presentation Layer: Tkinter UI
- Integration: HTTP API calls al backend en Docker
- Threading: Audio recording/playback en background
"""

from .orbe_window import OrbeWindow, OrbState
from .voice_controller import VoiceController

__all__ = ["OrbeWindow", "OrbState", "VoiceController"]

