"""
VoiceController - Integración del orbe Tkinter con backend de voz.

Maneja la captura de audio, comunicación con API y reproducción de respuestas.
"""

import io
import wave
import asyncio
import threading
from typing import Optional, Callable
from uuid import UUID, uuid4
import httpx
import sounddevice as sd
import numpy as np
from loguru import logger


class VoiceController:
    """
    Controlador de voz para interfaz Tkinter.
    
    Responsibilities:
    - Capturar audio del micrófono
    - Enviar audio a backend API
    - Recibir y reproducir respuesta
    - Gestionar estados de la conversación
    - Thread-safe operations con Tkinter
    
    Architecture:
    - Integration layer: Comunica Tkinter con Backend API
    - Threading: Audio operations en background
    - Async HTTP: Comunicación con API
    """
    
    # Audio configuration
    SAMPLE_RATE = 16000  # 16kHz (óptimo para Whisper)
    CHANNELS = 1         # Mono
    DTYPE = np.int16     # 16-bit PCM
    
    def __init__(
        self,
        api_url: str = "http://localhost:8000",
        on_state_change: Optional[Callable[[str], None]] = None
    ):
        """
        Inicializar controlador de voz.
        
        Args:
            api_url: URL del backend API
            on_state_change: Callback para cambios de estado
        """
        self.api_url = api_url
        self.on_state_change = on_state_change
        
        # State management
        self.is_recording = False
        self.recording_data = []
        self.session_id: Optional[UUID] = None
        
        # Threading
        self.audio_thread: Optional[threading.Thread] = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        
        logger.info(f"🎤 VoiceController initialized: API={api_url}")
    
    def start_recording(self) -> None:
        """
        Iniciar grabación de audio desde el micrófono.
        
        Starts recording in a separate thread to avoid blocking Tkinter UI.
        """
        if self.is_recording:
            logger.warning("⚠️ Already recording")
            return
        
        self.is_recording = True
        self.recording_data = []
        
        logger.info("🎤 Starting audio recording...")
        self._notify_state_change("listening")
        
        # Start recording in thread
        self.audio_thread = threading.Thread(target=self._record_audio)
        self.audio_thread.daemon = True
        self.audio_thread.start()
    
    def stop_recording(self) -> None:
        """
        Detener grabación y procesar audio.
        
        Stops recording and sends audio to backend API for processing.
        """
        if not self.is_recording:
            logger.warning("⚠️ Not recording")
            return
        
        self.is_recording = False
        logger.info("🛑 Stopping audio recording...")
        
        # Wait for recording thread to finish
        if self.audio_thread:
            self.audio_thread.join(timeout=1.0)
        
        # Process audio in background thread
        processing_thread = threading.Thread(target=self._process_audio)
        processing_thread.daemon = True
        processing_thread.start()
    
    def _record_audio(self) -> None:
        """
        Método interno para grabar audio (runs in thread).
        
        Captures audio from microphone while is_recording is True.
        """
        try:
            def audio_callback(indata, frames, time, status):
                """Callback para capturar audio chunks."""
                if status:
                    logger.warning(f"Audio callback status: {status}")
                
                if self.is_recording:
                    self.recording_data.append(indata.copy())
            
            # Start audio stream
            with sd.InputStream(
                samplerate=self.SAMPLE_RATE,
                channels=self.CHANNELS,
                dtype=self.DTYPE,
                callback=audio_callback
            ):
                # Keep recording while is_recording is True
                while self.is_recording:
                    sd.sleep(100)  # Sleep 100ms
            
            logger.info(f"✅ Recording finished: {len(self.recording_data)} chunks")
            
        except Exception as e:
            logger.error(f"❌ Recording error: {e}")
            self._notify_state_change("idle")
    
    def _process_audio(self) -> None:
        """
        Procesar audio grabado (runs in thread).
        
        Converts recorded audio to WAV and sends to backend API.
        """
        try:
            self._notify_state_change("processing")
            
            if not self.recording_data:
                logger.warning("⚠️ No audio data recorded")
                self._notify_state_change("idle")
                return
            
            # Convert to numpy array
            audio_array = np.concatenate(self.recording_data, axis=0)
            
            logger.info(f"🎙️ Processing audio: {len(audio_array)} samples")
            
            # Convert to WAV bytes
            wav_bytes = self._audio_to_wav(audio_array)
            
            # Send to API (async operation)
            asyncio.run(self._send_to_api(wav_bytes))
            
        except Exception as e:
            logger.error(f"❌ Processing error: {e}")
            self._notify_state_change("idle")
    
    def _audio_to_wav(self, audio_array: np.ndarray) -> bytes:
        """
        Convertir array de audio a WAV bytes.
        
        Args:
            audio_array: Audio data as numpy array
            
        Returns:
            WAV file as bytes
        """
        wav_buffer = io.BytesIO()
        
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(self.CHANNELS)
            wav_file.setsampwidth(2)  # 16-bit = 2 bytes
            wav_file.setframerate(self.SAMPLE_RATE)
            wav_file.writeframes(audio_array.tobytes())
        
        return wav_buffer.getvalue()
    
    async def _send_to_api(self, audio_bytes: bytes) -> None:
        """
        Enviar audio a backend API y reproducir respuesta.
        
        Args:
            audio_bytes: Audio in WAV format
        """
        try:
            # Prepare session ID
            if not self.session_id:
                self.session_id = uuid4()
            
            logger.info(f"📤 Sending audio to API: {len(audio_bytes)} bytes")
            
            # Create multipart form data
            files = {
                'audio': ('voice.wav', audio_bytes, 'audio/wav')
            }
            
            data = {
                'conversation_id': str(self.session_id)
            }
            
            # Send to API
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_url}/api/voice/process",
                    files=files,
                    data=data
                )
                
                response.raise_for_status()
            
            # Get response audio
            response_audio = response.content
            
            # Get metadata from headers
            transcribed_text = self._decode_header(
                response.headers.get('X-Transcribed-Text', '')
            )
            response_text = self._decode_header(
                response.headers.get('X-Response-Text', '')
            )
            
            logger.info(f"📝 Transcribed: '{transcribed_text}'")
            logger.info(f"🤖 Response: '{response_text}'")
            logger.info(f"🔊 Response audio: {len(response_audio)} bytes")
            
            # Play response
            self._notify_state_change("speaking")
            self._play_audio(response_audio)
            
            # Back to idle
            self._notify_state_change("idle")
            
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ API error: {e.response.status_code} - {e.response.text}")
            self._notify_state_change("idle")
        except Exception as e:
            logger.error(f"❌ Send to API error: {e}")
            self._notify_state_change("idle")
    
    def _decode_header(self, encoded: str) -> str:
        """Decodificar header Base64."""
        try:
            import base64
            return base64.b64decode(encoded).decode('utf-8')
        except Exception:
            return encoded
    
    def _play_audio(self, audio_bytes: bytes) -> None:
        """
        Reproducir audio de respuesta.
        
        Args:
            audio_bytes: Audio in WAV format
        """
        try:
            # Read WAV from bytes
            wav_buffer = io.BytesIO(audio_bytes)
            
            with wave.open(wav_buffer, 'rb') as wav_file:
                sample_rate = wav_file.getframerate()
                audio_data = wav_file.readframes(wav_file.getnframes())
                
                # Convert to numpy array
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                
                logger.info(f"🔊 Playing audio: {len(audio_array)} samples")
                
                # Play audio (blocking)
                sd.play(audio_array, sample_rate)
                sd.wait()  # Wait until playback is finished
                
                logger.info("✅ Audio playback finished")
        
        except Exception as e:
            logger.error(f"❌ Playback error: {e}")
    
    def _notify_state_change(self, state: str) -> None:
        """
        Notificar cambio de estado al callback.
        
        Args:
            state: New state (idle, listening, processing, speaking)
        """
        if self.on_state_change:
            try:
                self.on_state_change(state)
            except Exception as e:
                logger.error(f"❌ State change callback error: {e}")
    
    def cleanup(self) -> None:
        """Limpiar recursos."""
        logger.info("🧹 Cleaning up VoiceController")
        self.is_recording = False
        
        # Stop any ongoing playback
        try:
            sd.stop()
        except Exception:
            pass


# === Testing ===
if __name__ == "__main__":
    import time
    
    print("=" * 60)
    print("🎤 VoiceController Test")
    print("=" * 60)
    print()
    print("Press ENTER to start recording...")
    input()
    
    controller = VoiceController(
        api_url="http://localhost:8000",
        on_state_change=lambda state: print(f"State: {state}")
    )
    
    print("🎤 Recording... (speak now)")
    controller.start_recording()
    
    time.sleep(5)  # Record for 5 seconds
    
    print("🛑 Stopping and processing...")
    controller.stop_recording()
    
    # Wait for processing
    time.sleep(10)
    
    print("✅ Test finished")

