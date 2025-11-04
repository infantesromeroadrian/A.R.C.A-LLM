"""
Frontend Tkinter - Jarvis-Style Orb Interface.

Interfaz desktop con orbe animado estilo Jarvis/Iron Man para A.R.C.A-LLM.

Components:
- OrbeWindow: Ventana principal con Canvas
- AnimationEngine: Motor de animación smooth
- OrbStates: Estados del orbe (idle, listening, processing, speaking)
- VoiceController: Integración con VoiceAssistantService
- AudioThreadManager: Threading para audio non-blocking

Architecture:
- Presentation Layer: Tkinter UI
- Integration: Reusar VoiceAssistantService existente
- Threading: Audio en background
"""

from .orbe_window import OrbeWindow

__all__ = ["OrbeWindow"]

