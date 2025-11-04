"""
OrbeWindow - Ventana principal con orbe animado estilo Jarvis.

Ventana Tkinter con Canvas que muestra un orbe central animado
que responde a los estados del asistente de voz.
"""

import tkinter as tk
from tkinter import Canvas
import math
from typing import Literal, Callable, Optional
from enum import Enum


class OrbState(Enum):
    """Estados posibles del orbe Jarvis."""
    IDLE = "idle"              # Pulsación suave, esperando
    LISTENING = "listening"    # Ondas expansivas, grabando
    PROCESSING = "processing"  # Rotación rápida, pensando
    SPEAKING = "speaking"      # Pulsación con audio, hablando


class OrbeWindow:
    """
    Ventana principal con orbe animado estilo Jarvis.
    
    Responsibilities:
    - Crear ventana sin bordes, siempre al frente
    - Renderizar orbe central con Canvas
    - Gestionar animaciones según estado
    - Capturar eventos de click para activar voz
    - Integrar con pipeline de voz
    
    Architecture:
    - Presentation Layer: UI con Tkinter
    - Single Responsibility: Solo visualización y eventos UI
    - Integration: Callbacks para comunicación con VoiceController
    """
    
    # === Window Configuration ===
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 800
    BACKGROUND_COLOR = "#000000"  # Negro
    
    # === Orb Configuration ===
    ORB_CENTER_X = 400
    ORB_CENTER_Y = 400
    ORB_BASE_RADIUS = 80
    
    # === Colors by State ===
    STATE_COLORS = {
        OrbState.IDLE: "#00D9FF",        # Cyan brillante
        OrbState.LISTENING: "#00FF41",   # Verde Matrix
        OrbState.PROCESSING: "#B026FF",  # Morado
        OrbState.SPEAKING: "#00D9FF"     # Cyan (igual que idle)
    }
    
    # === Animation Configuration ===
    FPS = 60
    FRAME_DELAY = int(1000 / FPS)  # ms entre frames
    
    def __init__(
        self,
        title: str = "A.R.C.A - Jarvis Interface",
        on_click_callback: Optional[Callable[[], None]] = None,
        on_release_callback: Optional[Callable[[], None]] = None
    ):
        """
        Inicializar ventana del orbe Jarvis.
        
        Args:
            title: Título de la ventana
            on_click_callback: Función a llamar cuando se hace click en orbe
            on_release_callback: Función a llamar cuando se suelta el click
        """
        # === Create Root Window ===
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.root.configure(bg=self.BACKGROUND_COLOR)
        
        # Configurar ventana para estar siempre al frente (opcional)
        self.root.attributes('-topmost', True)
        
        # === State Management ===
        self.current_state = OrbState.IDLE
        self.animation_running = True
        
        # === Animation Variables ===
        self.animation_time = 0.0
        self.breathing_phase = 0.0
        self.rotation_angle = 0.0
        
        # === Callbacks ===
        self.on_click_callback = on_click_callback
        self.on_release_callback = on_release_callback
        
        # === Create Canvas ===
        self.canvas = Canvas(
            self.root,
            width=self.WINDOW_WIDTH,
            height=self.WINDOW_HEIGHT,
            bg=self.BACKGROUND_COLOR,
            highlightthickness=0  # Sin borde
        )
        self.canvas.pack()
        
        # === Create Orb Elements ===
        self._create_orb_elements()
        
        # === Bind Events ===
        self._bind_events()
        
        # === Start Animation Loop ===
        self._animate()
    
    def _create_orb_elements(self) -> None:
        """Crear los elementos visuales del orbe."""
        # Glow layers (múltiples círculos para efecto glow)
        self.glow_layers = []
        
        for i in range(5):
            alpha = 1.0 - (i * 0.15)  # Decreciente transparencia
            radius = self.ORB_BASE_RADIUS + (i * 15)
            
            # Color con alpha (simulado con stipple)
            color = self._get_current_color()
            
            glow = self.canvas.create_oval(
                self.ORB_CENTER_X - radius,
                self.ORB_CENTER_Y - radius,
                self.ORB_CENTER_X + radius,
                self.ORB_CENTER_Y + radius,
                fill="",
                outline=color,
                width=3,
                tags="glow"
            )
            self.glow_layers.append(glow)
        
        # Core orb (orbe principal)
        self.core_orb = self.canvas.create_oval(
            self.ORB_CENTER_X - self.ORB_BASE_RADIUS,
            self.ORB_CENTER_Y - self.ORB_BASE_RADIUS,
            self.ORB_CENTER_X + self.ORB_BASE_RADIUS,
            self.ORB_CENTER_Y + self.ORB_BASE_RADIUS,
            fill=self._get_current_color(),
            outline="",
            tags="core"
        )
    
    def _bind_events(self) -> None:
        """Vincular eventos de mouse."""
        self.canvas.tag_bind("core", "<Button-1>", self._on_orb_click)
        self.canvas.tag_bind("core", "<ButtonRelease-1>", self._on_orb_release)
        
        # Esc para cerrar
        self.root.bind("<Escape>", lambda e: self.root.quit())
        
        # Click derecho para menú/cerrar
        self.root.bind("<Button-3>", lambda e: self.root.quit())
    
    def _on_orb_click(self, event) -> None:
        """Manejar click en el orbe."""
        if self.on_click_callback:
            self.on_click_callback()
    
    def _on_orb_release(self, event) -> None:
        """Manejar release del click."""
        if self.on_release_callback:
            self.on_release_callback()
    
    def _get_current_color(self) -> str:
        """Obtener color según estado actual."""
        return self.STATE_COLORS.get(self.current_state, "#00D9FF")
    
    def _animate(self) -> None:
        """
        Loop principal de animación.
        
        Ejecuta a ~60 FPS usando after() para no bloquear UI.
        """
        if not self.animation_running:
            return
        
        # Incrementar tiempo de animación
        self.animation_time += 0.016  # ~60 FPS
        
        # Aplicar animaciones según estado
        self._apply_state_animation()
        
        # Programar siguiente frame
        self.root.after(self.FRAME_DELAY, self._animate)
    
    def _apply_state_animation(self) -> None:
        """Aplicar animaciones específicas del estado actual."""
        match self.current_state:
            case OrbState.IDLE:
                self._animate_idle()
            case OrbState.LISTENING:
                self._animate_listening()
            case OrbState.PROCESSING:
                self._animate_processing()
            case OrbState.SPEAKING:
                self._animate_speaking()
    
    def _animate_idle(self) -> None:
        """Animación IDLE: Pulsación suave (breathing)."""
        # Breathing effect: tamaño oscila suavemente
        breathing_amplitude = 10  # píxeles de variación
        breathing_frequency = 0.5  # Hz
        
        size_delta = breathing_amplitude * math.sin(
            self.animation_time * breathing_frequency * 2 * math.pi
        )
        
        current_radius = self.ORB_BASE_RADIUS + size_delta
        
        # Actualizar core orb
        self.canvas.coords(
            self.core_orb,
            self.ORB_CENTER_X - current_radius,
            self.ORB_CENTER_Y - current_radius,
            self.ORB_CENTER_X + current_radius,
            self.ORB_CENTER_Y + current_radius
        )
        
        # Actualizar glow layers
        for i, glow in enumerate(self.glow_layers):
            glow_radius = current_radius + (i * 15)
            self.canvas.coords(
                glow,
                self.ORB_CENTER_X - glow_radius,
                self.ORB_CENTER_Y - glow_radius,
                self.ORB_CENTER_X + glow_radius,
                self.ORB_CENTER_Y + glow_radius
            )
    
    def _animate_listening(self) -> None:
        """Animación LISTENING: Ondas expansivas."""
        # Similar a idle pero con pulsación más rápida
        breathing_amplitude = 15
        breathing_frequency = 2.0  # Más rápido que idle
        
        size_delta = breathing_amplitude * math.sin(
            self.animation_time * breathing_frequency * 2 * math.pi
        )
        
        current_radius = self.ORB_BASE_RADIUS + size_delta
        
        self.canvas.coords(
            self.core_orb,
            self.ORB_CENTER_X - current_radius,
            self.ORB_CENTER_Y - current_radius,
            self.ORB_CENTER_X + current_radius,
            self.ORB_CENTER_Y + current_radius
        )
    
    def _animate_processing(self) -> None:
        """Animación PROCESSING: Rotación y pulsación rápida."""
        # Breathing rápido
        breathing_amplitude = 20
        breathing_frequency = 3.0
        
        size_delta = breathing_amplitude * abs(math.sin(
            self.animation_time * breathing_frequency * 2 * math.pi
        ))
        
        current_radius = self.ORB_BASE_RADIUS + size_delta
        
        self.canvas.coords(
            self.core_orb,
            self.ORB_CENTER_X - current_radius,
            self.ORB_CENTER_Y - current_radius,
            self.ORB_CENTER_X + current_radius,
            self.ORB_CENTER_Y + current_radius
        )
        
        # TODO: Agregar rotación de glow layers (TICKET-003)
    
    def _animate_speaking(self) -> None:
        """Animación SPEAKING: Pulsación sincronizada (futuro: con audio)."""
        # Por ahora, similar a listening pero diferente color
        self._animate_listening()
        # TODO: Sincronizar con amplitude de audio (TICKET-005)
    
    def set_state(self, new_state: OrbState) -> None:
        """
        Cambiar estado del orbe.
        
        Args:
            new_state: Nuevo estado del orbe
        """
        if self.current_state == new_state:
            return
        
        self.current_state = new_state
        
        # Actualizar color del orbe
        new_color = self._get_current_color()
        self.canvas.itemconfig(self.core_orb, fill=new_color)
        
        # Actualizar color de glow layers
        for glow in self.glow_layers:
            self.canvas.itemconfig(glow, outline=new_color)
    
    def run(self) -> None:
        """Iniciar el loop principal de Tkinter."""
        self.root.mainloop()
    
    def cleanup(self) -> None:
        """Limpiar recursos."""
        self.animation_running = False
        self.root.quit()


# === Main para testing standalone ===
if __name__ == "__main__":
    def on_click():
        print("🎤 Orbe clicked - Start recording")
        window.set_state(OrbState.LISTENING)
    
    def on_release():
        print("🛑 Recording released - Processing")
        window.set_state(OrbState.PROCESSING)
        
        # Simular procesamiento
        window.root.after(2000, lambda: window.set_state(OrbState.SPEAKING))
        window.root.after(4000, lambda: window.set_state(OrbState.IDLE))
    
    window = OrbeWindow(
        on_click_callback=on_click,
        on_release_callback=on_release
    )
    
    print("=" * 60)
    print("🤖 A.R.C.A - Jarvis Orb Interface")
    print("=" * 60)
    print("Click en el orbe para activar voz")
    print("Esc o Click derecho para salir")
    print("=" * 60)
    
    window.run()

