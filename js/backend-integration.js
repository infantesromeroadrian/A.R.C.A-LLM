/* ===== INTEGRACIÓN CON BACKEND A.R.C.A-LLM ===== */

// Configuración del backend
const CONFIG = {
    BACKEND_URL: 'http://localhost:8000',
    AUDIO_FORMAT: 'audio/webm',
    MIN_RECORDING_TIME: 500, // ms
    MAX_RECORDING_TIME: 30000, // ms
    RETRY_ATTEMPTS: 3
};

const API_VOICE_ENDPOINT = `${CONFIG.BACKEND_URL}/api/voice/process`;

// Variables para captura de audio (expuestas globalmente)
window.mediaRecorder = null;
window.audioChunks = [];
let audioStream = null;
let conversationId = null;
window.recordingStartTime = null;

// Inicializar captura de audio
async function iniciarCaptura() {
    try {
        if (!audioStream) {
            console.log('🎤 Solicitando acceso al micrófono...');
            audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            console.log('✅ Acceso al micrófono concedido');
            
            // Intentar usar WebM, fallback a código por defecto
            const mimeTypes = [
                'audio/webm;codecs=opus',
                'audio/webm',
                'audio/ogg;codecs=opus',
                'audio/mp4'
            ];
            
            let mimeType = '';
            for (const type of mimeTypes) {
                if (MediaRecorder.isTypeSupported(type)) {
                    mimeType = type;
                    console.log(`✅ Usando formato de audio: ${mimeType}`);
                    break;
                }
            }
            
            if (mimeType) {
                window.mediaRecorder = new MediaRecorder(audioStream, { mimeType });
            } else {
                window.mediaRecorder = new MediaRecorder(audioStream);
                console.log('⚠️ Usando formato por defecto del navegador');
            }
            
            window.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    console.log(`📥 Chunk recibido: ${event.data.size} bytes`);
                    window.audioChunks.push(event.data);
                } else {
                    console.warn('⚠️ Chunk vacío recibido');
                }
            };
            
            window.mediaRecorder.onstop = async () => {
                console.log('🎤 MediaRecorder detenido. Chunks recibidos:', window.audioChunks.length);
                const recordingDuration = window.recordingStartTime ? Date.now() - window.recordingStartTime : 0;
                
                // Validar tiempo mínimo de grabación
                if (recordingDuration < CONFIG.MIN_RECORDING_TIME) {
                    console.warn(`⚠️ Grabación muy corta (${recordingDuration}ms). Mínimo requerido: ${CONFIG.MIN_RECORDING_TIME}ms`);
                    if (window.statusText) window.statusText.textContent = 'Grabación muy corta';
                    if (window.setSystemActive) window.setSystemActive(false);
                    window.audioChunks = [];
                    window.recordingStartTime = null;
                    return;
                }
                
                if (window.audioChunks.length === 0) {
                    console.error('❌ No hay chunks de audio para enviar');
                    if (window.statusText) window.statusText.textContent = 'Error: Sin audio capturado';
                    if (window.setSystemActive) window.setSystemActive(false);
                    window.recordingStartTime = null;
                    return;
                }
                
                const audioBlob = new Blob(window.audioChunks, { type: CONFIG.AUDIO_FORMAT });
                console.log(`📦 Audio Blob creado: ${audioBlob.size} bytes, tipo: ${audioBlob.type}`);
                window.audioChunks = [];
                window.recordingStartTime = null;
                await enviarAudioAlBackend(audioBlob);
            };

            window.mediaRecorder.onerror = (event) => {
                console.error('Error en MediaRecorder:', event.error);
                if (window.statusText) window.statusText.textContent = 'Error de grabación';
                if (window.setSystemActive) window.setSystemActive(false);
            };
        }
        
        return true;
    } catch (error) {
        console.error('Error al acceder al micrófono:', error);
        if (window.statusText) window.statusText.textContent = 'Error de micrófono';
        if (window.setSystemActive) window.setSystemActive(false);
        return false;
    }
}

// Enviar audio al backend
async function enviarAudioAlBackend(audioBlob) {
    try {
        // Verificar que el audio no esté vacío
        if (audioBlob.size === 0) {
            console.warn('Audio vacío, ignorando envío');
            if (window.setSystemActive) window.setSystemActive(false);
            return;
        }

        if (window.statusText) window.statusText.textContent = 'Procesando...';

        // Preparar FormData
        const formData = new FormData();
        formData.append('audio', audioBlob, 'voice.webm');
        
        if (conversationId) {
            formData.append('conversation_id', conversationId);
        }

        // Enviar al backend
        console.log(`🚀 Enviando audio al backend: ${audioBlob.size} bytes`);
        const response = await fetch(API_VOICE_ENDPOINT, {
            method: 'POST',
            body: formData
        });

        console.log(`📡 Respuesta recibida: ${response.status} ${response.statusText}`);

        if (!response.ok) {
            const errorText = await response.text().catch(() => '');
            console.error('❌ Error del backend:', errorText);
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        // Obtener headers (Base64 encoded)
        const conversationIdHeader = response.headers.get('X-Conversation-Id');
        const transcribedTextHeader = response.headers.get('X-Transcribed-Text');
        const llmResponseHeader = response.headers.get('X-Response-Text');

        // Decodificar conversation ID con manejo de errores
        if (conversationIdHeader) {
            try {
                conversationId = atob(conversationIdHeader);
            } catch (e) {
                console.warn('Error decodificando conversation ID:', e);
                // Intentar usar directamente si no es Base64
                conversationId = conversationIdHeader;
            }
        }
        
        let transcribedText = '';
        let llmResponse = '';
        
        if (transcribedTextHeader) {
            try {
                // Decodificar Base64 y luego a UTF-8 correctamente
                const binaryString = atob(transcribedTextHeader);
                const bytes = new Uint8Array(binaryString.length);
                for (let i = 0; i < binaryString.length; i++) {
                    bytes[i] = binaryString.charCodeAt(i);
                }
                transcribedText = new TextDecoder('utf-8').decode(bytes);
            } catch (e) {
                console.warn('Error decodificando texto transcrito:', e);
                // Fallback: intentar directamente
                try {
                    transcribedText = decodeURIComponent(escape(atob(transcribedTextHeader)));
                } catch (e2) {
                    console.error('Error en fallback de decodificación:', e2);
                }
            }
        }
        
        if (llmResponseHeader) {
            try {
                // Decodificar Base64 y luego a UTF-8 correctamente
                const binaryString = atob(llmResponseHeader);
                const bytes = new Uint8Array(binaryString.length);
                for (let i = 0; i < binaryString.length; i++) {
                    bytes[i] = binaryString.charCodeAt(i);
                }
                llmResponse = new TextDecoder('utf-8').decode(bytes);
            } catch (e) {
                console.warn('Error decodificando respuesta LLM:', e);
                // Fallback: intentar directamente
                try {
                    llmResponse = decodeURIComponent(escape(atob(llmResponseHeader)));
                } catch (e2) {
                    console.error('Error en fallback de decodificación:', e2);
                }
            }
        }

        // Mostrar transcripción en consola
        if (transcribedText) {
            console.log('Usuario:', transcribedText);
            // Añadir mensaje del usuario al chat dorado
            if (window.addUserMessage) {
                window.addUserMessage(transcribedText);
            }
        }
        if (llmResponse) {
            console.log('A.R.C.A:', llmResponse);
            // Añadir respuesta de la IA al chat dorado
            if (window.addAIMessage) {
                window.addAIMessage(llmResponse);
            }
        }

        // Obtener y reproducir audio
        const audioResponseBlob = await response.blob();
        
        if (audioResponseBlob.size === 0) {
            throw new Error('Respuesta de audio vacía');
        }

        await reproducirRespuesta(audioResponseBlob);

    } catch (error) {
        console.error('Error al comunicarse con backend:', error);
        if (window.statusText) window.statusText.textContent = 'Error de conexión';
        if (window.setSystemActive) window.setSystemActive(false);
        
        // Mostrar mensaje más específico si es posible
        if (error.message.includes('Failed to fetch')) {
            console.error('No se pudo conectar con el backend. Verifica que esté corriendo en', CONFIG.BACKEND_URL);
        }
    }
}

// Reproducir respuesta con sincronización visual
async function reproducirRespuesta(audioBlob) {
    try {
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);

        // Analizar audio para animar el orbe
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const source = audioContext.createMediaElementSource(audio);
        const analyser = audioContext.createAnalyser();
        
        source.connect(analyser);
        analyser.connect(audioContext.destination);
        
        analyser.fftSize = 256;
        const dataArray = new Uint8Array(analyser.frequencyBinCount);
        
        // Función para actualizar animación del orbe con el audio
        function actualizarOrbeConAudio() {
            if (audio.paused || audio.ended) {
                window.updateAIVoiceLevel(0);
                return;
            }
            
            analyser.getByteFrequencyData(dataArray);
            
            // Calcular nivel promedio
            const sum = dataArray.reduce((a, b) => a + b, 0);
            const average = sum / dataArray.length;
            const level = average / 255; // Normalizar 0-1
            
            window.updateAIVoiceLevel(level);
            
            requestAnimationFrame(actualizarOrbeConAudio);
        }
        
        // Manejar errores de reproducción
        audio.onerror = (e) => {
            console.error('Error al reproducir audio:', e);
            window.updateAIVoiceLevel(0);
            if (window.setSystemActive) window.setSystemActive(false);
            URL.revokeObjectURL(audioUrl);
        };

        // Reproducir audio
        await audio.play();
        actualizarOrbeConAudio();
        
        // Cuando termine, resetear
        audio.onended = () => {
            window.updateAIVoiceLevel(0);
            if (window.setSystemActive) window.setSystemActive(false);
            URL.revokeObjectURL(audioUrl);
            
            // Limpiar recursos de audio
            source.disconnect();
            analyser.disconnect();
            audioContext.close().catch(console.error);
        };

    } catch (error) {
        console.error('Error al reproducir respuesta:', error);
        window.updateAIVoiceLevel(0);
        if (window.setSystemActive) window.setSystemActive(false);
    }
}

// Verificar salud del backend
async function verificarBackend() {
    try {
        const response = await fetch(`${CONFIG.BACKEND_URL}/api/health`);
        if (response.ok) {
            const data = await response.json();
            console.log('Backend saludable:', data);
            return true;
        }
        return false;
    } catch (error) {
        console.warn('Backend no disponible:', error.message);
        return false;
    }
}

// Limpiar recursos de audio
function limpiarRecursosAudio() {
    if (window.mediaRecorder && window.mediaRecorder.state !== 'inactive') {
        try {
            window.mediaRecorder.stop();
        } catch (e) {
            // Ignorar errores si ya está detenido
        }
    }
    
    if (audioStream) {
        audioStream.getTracks().forEach(track => track.stop());
        audioStream = null;
    }
    
    window.audioChunks = [];
    window.mediaRecorder = null;
}

// Exponer funciones necesarias globalmente
window.iniciarCaptura = iniciarCaptura;
window.enviarAudioAlBackend = enviarAudioAlBackend;
window.reproducirRespuesta = reproducirRespuesta;
window.limpiarRecursosAudio = limpiarRecursosAudio;

// Verificar backend al cargar (opcional, solo para logging)
window.addEventListener('load', async () => {
    const backendDisponible = await verificarBackend();
    if (!backendDisponible) {
        console.warn('⚠️ Backend no disponible. Asegúrate de que esté corriendo en', CONFIG.BACKEND_URL);
    }
});

