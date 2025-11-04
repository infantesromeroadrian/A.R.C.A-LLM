#!/usr/bin/env python3
"""
Script para ejecutar interfaz Tkinter local que se conecta al backend en Docker.

Setup:
1. Backend en Docker: docker-compose up -d
2. Frontend Tkinter: python run_tkinter_local.py

El frontend Tkinter corre local (con display) y se conecta a la API en Docker.
"""

import sys
from pathlib import Path

print("=" * 60)
print("🤖 A.R.C.A LLM - Tkinter Local + Backend Docker")
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
print("   → curl http://localhost:8000/api/health")
print("   → Debe retornar JSON con 'status': 'healthy'")
print()

print("3. ¿LM Studio está corriendo?")
print("   → http://192.168.1.38:1234")
print("   → Modelo: qwen/qwen3-4b-2507 cargado")
print()

response = input("¿Todo listo? Iniciar interfaz Tkinter (y/n): ")

if response.lower() != 'y':
    print("❌ Abortado. Asegúrate de tener el backend corriendo primero.")
    print()
    print("Para iniciar backend:")
    print("  docker-compose up -d")
    sys.exit(0)

print()
print("=" * 60)
print("🚀 Iniciando Interfaz Tkinter...")
print("=" * 60)
print()

# Importar y ejecutar
from src.frontend_tkinter.orbe_window import OrbeWindow, OrbState

def on_click():
    """Callback cuando se hace click en el orbe."""
    print("🎤 Orbe clicked - Activando grabación...")
    window.set_state(OrbState.LISTENING)
    # TODO: Integrar con backend API (TICKET-005)

def on_release():
    """Callback cuando se suelta el click."""
    print("🛑 Recording released - Procesando...")
    window.set_state(OrbState.PROCESSING)
    
    # Simular procesamiento (por ahora)
    window.root.after(2000, lambda: window.set_state(OrbState.SPEAKING))
    window.root.after(4000, lambda: window.set_state(OrbState.IDLE))
    
    # TODO: Enviar audio a backend API en Docker (TICKET-005)

try:
    print("🎨 Tkinter Frontend:")
    print("   - Ventana 800x800px")
    print("   - Orbe animado estilo Jarvis")
    print("   - Click en orbe para activar")
    print("   - Esc o Click derecho para salir")
    print()
    print("🔌 Backend:")
    print("   - API: http://localhost:8000")
    print("   - Docker container: arca-llm")
    print()
    print("=" * 60)
    
    window = OrbeWindow(
        title="A.R.C.A - Jarvis Interface (Local)",
        on_click_callback=on_click,
        on_release_callback=on_release
    )
    
    window.run()
    
except KeyboardInterrupt:
    print()
    print("👋 Interfaz cerrada por usuario")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

