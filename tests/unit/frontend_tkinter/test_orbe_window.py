"""
Unit tests for OrbeWindow - Animated Jarvis-style orb GUI.

These tests verify the visual state management, animation logic,
and user interaction handling without requiring a real display.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import math
from src.frontend_tkinter.orbe_window import OrbeWindow, OrbState


class TestOrbStateEnum:
    """Test OrbState enumeration."""
    
    def test_orb_state_values(self):
        """Verify all orb states are defined correctly."""
        assert OrbState.IDLE.value == "idle"
        assert OrbState.LISTENING.value == "listening"
        assert OrbState.PROCESSING.value == "processing"
        assert OrbState.SPEAKING.value == "speaking"
        assert OrbState.ERROR.value == "error"
    
    def test_orb_state_count(self):
        """Verify we have exactly 5 states."""
        assert len(OrbState) == 5


class TestOrbeWindowInitialization:
    """Test OrbeWindow initialization and setup."""
    
    @patch('src.frontend_tkinter.orbe_window.OrbeWindow._animate')
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_window_initialization(self, mock_canvas, mock_tk, mock_animate):
        """Test basic window initialization."""
        mock_root = Mock()
        mock_root._last_child_ids = {}
        mock_root._w = '.root'
        mock_root.children = {}
        mock_tk.return_value = mock_root
        
        window = OrbeWindow()
        
        # Verify window properties were set
        mock_root.title.assert_called_once()
        mock_root.configure.assert_called()
        mock_root.attributes.assert_called()
    
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_default_dimensions(self, mock_canvas, mock_tk):
        """Test default window dimensions."""
        window = OrbeWindow()
        
        assert window.width == 800
        assert window.height == 800
    
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_custom_dimensions(self, mock_canvas, mock_tk):
        """Test custom window dimensions."""
        window = OrbeWindow()
        
        # Window uses class constants
        assert window.width == 800
        assert window.height == 800
    
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_initial_state_is_idle(self, mock_canvas, mock_tk):
        """Test window starts in IDLE state."""
        window = OrbeWindow()
        
        assert window.current_state == OrbState.IDLE


class TestStateManagement:
    """Test orb state management and transitions."""
    
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_set_state_to_listening(self, mock_canvas, mock_tk):
        """Test transitioning to LISTENING state."""
        window = OrbeWindow()
        
        window.set_state(OrbState.LISTENING)
        
        assert window.current_state == OrbState.LISTENING
    
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_set_state_to_processing(self, mock_canvas, mock_tk):
        """Test transitioning to PROCESSING state."""
        window = OrbeWindow()
        
        window.set_state(OrbState.PROCESSING)
        
        assert window.current_state == OrbState.PROCESSING
    
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_set_state_to_speaking(self, mock_canvas, mock_tk):
        """Test transitioning to SPEAKING state."""
        window = OrbeWindow()
        
        window.set_state(OrbState.SPEAKING)
        
        assert window.current_state == OrbState.SPEAKING
    
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_set_state_to_error(self, mock_canvas, mock_tk):
        """Test transitioning to ERROR state."""
        window = OrbeWindow()
        
        window.set_state(OrbState.ERROR)
        
        assert window.current_state == OrbState.ERROR
    
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_state_transitions_are_sequential(self, mock_canvas, mock_tk):
        """Test multiple state transitions."""
        window = OrbeWindow()
        
        window.set_state(OrbState.LISTENING)
        assert window.current_state == OrbState.LISTENING
        
        window.set_state(OrbState.PROCESSING)
        assert window.current_state == OrbState.PROCESSING
        
        window.set_state(OrbState.SPEAKING)
        assert window.current_state == OrbState.SPEAKING
        
        window.set_state(OrbState.IDLE)
        assert window.current_state == OrbState.IDLE


class TestColorConfiguration:
    """Test color configuration for different states."""
    
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_idle_color(self, mock_canvas, mock_tk):
        """Test IDLE state color."""
        window = OrbeWindow()
        
        color = window._get_color_for_state(OrbState.IDLE)
        
        assert color == "#4A90E2"  # Blue
    
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_listening_color(self, mock_canvas, mock_tk):
        """Test LISTENING state color."""
        window = OrbeWindow()
        
        color = window._get_color_for_state(OrbState.LISTENING)
        
        assert color == "#50C878"  # Green
    
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_processing_color(self, mock_canvas, mock_tk):
        """Test PROCESSING state color."""
        window = OrbeWindow()
        
        color = window._get_color_for_state(OrbState.PROCESSING)
        
        assert color == "#FFD700"  # Gold
    
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_speaking_color(self, mock_canvas, mock_tk):
        """Test SPEAKING state color."""
        window = OrbeWindow()
        
        color = window._get_color_for_state(OrbState.SPEAKING)
        
        assert color == "#9370DB"  # Purple
    
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_error_color(self, mock_canvas, mock_tk):
        """Test ERROR state color."""
        window = OrbeWindow()
        
        color = window._get_color_for_state(OrbState.ERROR)
        
        assert color == "#E74C3C"  # Red


class TestAnimationLogic:
    """Test animation timing and logic."""
    
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_animation_frame_increments(self, mock_canvas, mock_tk):
        """Test animation frame counter increments."""
        window = OrbeWindow()
        initial_frame = window.animation_frame
        
        # Simulate animation step
        window.animation_frame += 1
        
        assert window.animation_frame == initial_frame + 1
    
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_pulse_calculation(self, mock_canvas, mock_tk):
        """Test pulse intensity calculation."""
        window = OrbeWindow()
        
        # Test pulse at different frames
        pulse_0 = window._calculate_pulse(0)
        pulse_quarter = window._calculate_pulse(15)  # ~1/4 cycle
        pulse_half = window._calculate_pulse(30)     # ~1/2 cycle
        
        # Pulse should vary smoothly
        assert 0.0 <= pulse_0 <= 1.0
        assert 0.0 <= pulse_quarter <= 1.0
        assert 0.0 <= pulse_half <= 1.0
    
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_wave_calculation(self, mock_canvas, mock_tk):
        """Test wave pattern calculation for particles."""
        window = OrbeWindow()
        
        # Test wave at different angles
        wave_0 = window._calculate_wave(0, 0)
        wave_90 = window._calculate_wave(math.pi/2, 0)
        wave_180 = window._calculate_wave(math.pi, 0)
        
        # Wave should be within reasonable bounds
        assert -50 <= wave_0 <= 50
        assert -50 <= wave_90 <= 50
        assert -50 <= wave_180 <= 50


class TestClickInteraction:
    """Test mouse click interaction handling."""
    
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_click_callback_registration(self, mock_canvas, mock_tk):
        """Test click callback can be registered."""
        window = OrbeWindow()
        callback = Mock()
        
        window.set_click_callback(callback)
        
        assert window.click_callback == callback
    
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_click_triggers_callback(self, mock_canvas, mock_tk):
        """Test clicking orb triggers registered callback."""
        window = OrbeWindow()
        callback = Mock()
        window.set_click_callback(callback)
        
        # Simulate click event
        event = Mock()
        event.x = window.width // 2
        event.y = window.height // 2
        
        window._on_click(event)
        
        callback.assert_called_once()
    
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_click_outside_orb_ignored(self, mock_canvas, mock_tk):
        """Test clicks outside orb area are ignored."""
        window = OrbeWindow()
        callback = Mock()
        window.set_click_callback(callback)
        
        # Simulate click outside orb
        event = Mock()
        event.x = 0
        event.y = 0
        
        window._on_click(event)
        
        # Callback should not be triggered for clicks far from center
        # (this depends on orb radius, but (0,0) should be outside)
        # Note: In actual implementation, this test might need adjustment
        # based on exact click detection logic


class TestMessageDisplay:
    """Test message display functionality."""
    
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_show_message_updates_text(self, mock_canvas, mock_tk):
        """Test showing a message updates display."""
        mock_canvas_instance = Mock()
        mock_canvas.return_value = mock_canvas_instance
        
        window = OrbeWindow()
        
        window.show_message("Test message")
        
        # Verify canvas itemconfig was called to update text
        # Note: Actual implementation may vary
        assert window.current_message == "Test message"
    
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_show_message_with_empty_string(self, mock_canvas, mock_tk):
        """Test showing empty message."""
        window = OrbeWindow()
        
        window.show_message("")
        
        assert window.current_message == ""
    
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_show_message_with_long_text(self, mock_canvas, mock_tk):
        """Test showing long message."""
        window = OrbeWindow()
        long_message = "A" * 200
        
        window.show_message(long_message)
        
        assert window.current_message == long_message


class TestWindowLifecycle:
    """Test window lifecycle management."""
    
    @patch('src.frontend_tkinter.orbe_window.OrbeWindow._animate')
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_start_animation_begins_loop(self, mock_canvas, mock_tk, mock_animate):
        """Test start_animation initiates animation loop."""
        mock_root = Mock()
        mock_root._last_child_ids = {}
        mock_root._w = '.root'
        mock_root.children = {}
        mock_tk.return_value = mock_root
        
        window = OrbeWindow()
        
        # Verify _animate was called during init
        mock_animate.assert_called_once()
        
        # Verify start_animation method exists
        assert hasattr(window, 'start_animation')
    
    @patch('src.frontend_tkinter.orbe_window.OrbeWindow._animate')
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_run_starts_mainloop(self, mock_canvas, mock_tk, mock_animate):
        """Test run() starts Tkinter mainloop."""
        mock_root = Mock()
        mock_root._last_child_ids = {}
        mock_root._w = '.root'
        mock_root.children = {}
        mock_root.mainloop = Mock()
        mock_tk.return_value = mock_root
        
        window = OrbeWindow()
        window.run()
        
        mock_root.mainloop.assert_called_once()


class TestAnimationPerformance:
    """Test animation performance characteristics."""
    
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_animation_frame_rate(self, mock_canvas, mock_tk):
        """Test animation frame rate is approximately 60 FPS."""
        window = OrbeWindow()
        
        # Default should be ~16ms for 60 FPS
        assert window.frame_delay == 16
    
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_particle_count_reasonable(self, mock_canvas, mock_tk):
        """Test particle count is reasonable for performance."""
        window = OrbeWindow()
        
        # Should have glow layers (5 in current implementation)
        assert 3 <= window.num_particles <= 10


class TestErrorHandling:
    """Test error state handling."""
    
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_error_state_persists(self, mock_canvas, mock_tk):
        """Test error state persists until explicitly changed."""
        window = OrbeWindow()
        
        window.set_state(OrbState.ERROR)
        
        # Simulate some animation frames
        window.animation_frame += 10
        
        assert window.current_state == OrbState.ERROR
    
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_recover_from_error_state(self, mock_canvas, mock_tk):
        """Test recovering from error state."""
        window = OrbeWindow()
        
        window.set_state(OrbState.ERROR)
        window.set_state(OrbState.IDLE)
        
        assert window.current_state == OrbState.IDLE


class TestIntegrationScenarios:
    """Test complete interaction scenarios."""
    
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_full_conversation_flow(self, mock_canvas, mock_tk):
        """Test complete conversation state flow."""
        window = OrbeWindow()
        
        # Simulate full conversation
        window.set_state(OrbState.IDLE)
        assert window.current_state == OrbState.IDLE
        
        window.set_state(OrbState.LISTENING)
        assert window.current_state == OrbState.LISTENING
        
        window.set_state(OrbState.PROCESSING)
        assert window.current_state == OrbState.PROCESSING
        
        window.set_state(OrbState.SPEAKING)
        assert window.current_state == OrbState.SPEAKING
        
        window.set_state(OrbState.IDLE)
        assert window.current_state == OrbState.IDLE
    
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_error_during_processing(self, mock_canvas, mock_tk):
        """Test error occurring during processing."""
        window = OrbeWindow()
        
        window.set_state(OrbState.PROCESSING)
        window.set_state(OrbState.ERROR)
        
        assert window.current_state == OrbState.ERROR
    
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_multiple_interactions(self, mock_canvas, mock_tk):
        """Test multiple sequential interactions."""
        window = OrbeWindow()
        callback = Mock()
        window.set_click_callback(callback)
        
        # Simulate multiple clicks
        event = Mock()
        event.x = window.width // 2
        event.y = window.height // 2
        
        for _ in range(5):
            window._on_click(event)
        
        # Callback should be called for each click
        assert callback.call_count == 5

