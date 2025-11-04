#!/usr/bin/env python3
"""
Script para ejecutar interfaz Tkinter con VOZ COMPLETA integrada.

Integra el orbe Jarvis con el backend de voz real (STT→LLM→TTS).

Setup:
1. Backend en Docker: docker-compose up -d
2. Instalar sounddevice: pip install sounddevice
3. Ejecutar: python run_tkinter_voice.py
"""

import sys
from pathlib import Path

print("=" * 60)
print("🤖 A.R.C.A LLM - Tkinter con Voz COMPLETA")
print("=" * 60)
print()

# Verificar que Docker esté corriendo
print("📋 Checklist:")
print()

print("1. ¿Docker está corriendo?")
print("   → docker-compose ps")
print("   → Debe mostrar 'arca-llm' running")
print()

print("2. ¿Backend API responde?")
print("   → curl http://localhost:8000/health")
print("   → Debe retornar JSON con 'status': 'healthy'")
print()

print("3. ¿LM Studio está corriendo?")
print("   → http://192.168.1.38:1234")
print("   → Modelo: qwen/qwen3-4b-2507 cargado")
print()

print("4. ¿Micrófono disponible?")
print("   → Dar permisos de micrófono si lo solicita")
print()

response = input("¿Todo listo? Iniciar interfaz Tkinter con VOZ (y/n): ")

if response.lower() != 'y':
    print("❌ Abortado. Asegúrate de tener el backend corriendo primero.")
    print()
    print("Para iniciar backend:")
    print("  docker-compose up -d")
    sys.exit(0)

print()
print("=" * 60)
print("🚀 Iniciando Interfaz Tkinter con VOZ...")
print("=" * 60)
print()

# Importar componentes
from src.frontend_tkinter.orbe_window import OrbeWindow, OrbState
from src.frontend_tkinter.voice_controller import VoiceController

# Estado global del orbe
current_window: OrbeWindow = None
voice_controller: VoiceController = None

def on_state_change(state: str):
    """
    Callback para cambios de estado desde VoiceController.
    
    Args:
        state: Estado nuevo (idle, listening, processing, speaking)
    """
    global current_window
    
    if not current_window:
        return
    
    # Map string state to OrbState enum
    state_map = {
        "idle": OrbState.IDLE,
        "listening": OrbState.LISTENING,
        "processing": OrbState.PROCESSING,
        "speaking": OrbState.SPEAKING
    }
    
    orb_state = state_map.get(state, OrbState.IDLE)
    
    # Update orb state (thread-safe via after())
    current_window.root.after(0, lambda: current_window.set_state(orb_state))

def on_orb_press():
    """Callback cuando se presiona el orbe (mouse down)."""
    print("🎤 Orbe pressed - Iniciando grabación...")
    voice_controller.start_recording()

def on_orb_release():
    """Callback cuando se suelta el orbe (mouse up)."""
    print("🛑 Orbe released - Procesando audio...")
    voice_controller.stop_recording()

try:
    print("🎨 Tkinter Frontend:")
    print("   - Ventana 800x800px")
    print("   - Orbe animado estilo Jarvis")
    print("   - MANTÉN PRESIONADO para grabar")
    print("   - SUELTA para enviar y procesar")
    print("   - Esc o Click derecho para salir")
    print()
    print("🔌 Backend:")
    print("   - API: http://localhost:8000")
    print("   - Docker container: arca-llm")
    print("   - VOZ COMPLETA INTEGRADA ✅")
    print()
    print("🎤 Micrófono:")
    print("   - Captura en tiempo real")
    print("   - Envío a Whisper STT")
    print("   - Procesamiento con LLM")
    print("   - Respuesta con TTS")
    print()
    print("=" * 60)
    print()
    
    # Crear VoiceController
    voice_controller = VoiceController(
        api_url="http://localhost:8000",
        on_state_change=on_state_change
    )
    
    # Crear ventana del orbe
    current_window = OrbeWindow(
        title="A.R.C.A - Jarvis Voice Interface",
        on_click_callback=on_orb_press,
        on_release_callback=on_orb_release
    )
    
    print("✨ INSTRUCCIONES:")
    print("   1. MANTÉN PRESIONADO el orbe mientras hablas")
    print("   2. SUELTA cuando termines de hablar")
    print("   3. Espera la respuesta (el orbe cambiará de color)")
    print("   4. La respuesta se reproducirá automáticamente")
    print()
    print("🎯 Estados del Orbe:")
    print("   🔵 CYAN = Esperando (Idle)")
    print("   🟢 VERDE = Grabando (Listening)")
    print("   🟣 MORADO = Procesando (Processing)")
    print("   🔵 CYAN = Hablando (Speaking)")
    print()
    print("=" * 60)
    print()
    print("🚀 ¡Listo! Presiona el orbe y habla...")
    print()
    
    # Ejecutar loop principal
    current_window.run()
    
except KeyboardInterrupt:
    print()
    print("👋 Interfaz cerrada por usuario")
except ImportError as e:
    print()
    print("=" * 60)
    print("❌ Error: Falta instalar sounddevice")
    print("=" * 60)
    print()
    print("Solución:")
    print("  pip install sounddevice")
    print()
    print("O con el venv activado:")
    print("  source arca-chatbot-venv/bin/activate")
    print("  uv pip install sounddevice")
    print()
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    # Cleanup
    if voice_controller:
        voice_controller.cleanup()

