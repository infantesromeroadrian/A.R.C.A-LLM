/* ===== INTEGRACIÓN CON BACKEND A.R.C.A-LLM ===== */

// Configuración del backend
// Detecta automáticamente si está en Docker o desarrollo local
// IMPORTANTE: El micrófono se captura en el navegador del cliente (tu Mac),
// no en el servidor. El audio se envía al backend en el servidor Ubuntu.
const isDocker = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
const CONFIG = {
    // Si está en Docker, usa URL relativa (nginx hace proxy a /api)
    // Si es desarrollo local, usa localhost:8000
    // Si accedes desde Mac a servidor remoto, el proxy de nginx manejará /api
    BACKEND_URL: isDocker ? '' : 'http://localhost:8000',
    AUDIO_FORMAT: 'audio/webm',
    MIN_RECORDING_TIME: 500, // ms
    MAX_RECORDING_TIME: 30000, // ms
    RETRY_ATTEMPTS: 3
};

const API_VOICE_ENDPOINT = `${CONFIG.BACKEND_URL}/api/voice/process`;
const TARGET_SAMPLE_RATE = 16000;

// Variables para captura de audio (expuestas globalmente)
window.mediaRecorder = null;
window.audioChunks = [];
let audioStream = null;
let conversationId = null;
window.recordingStartTime = null;
window.userAudioAnalyser = null;
let userAudioContext = null;
let userAnalyserNode = null;

async function convertBlobToWav(blob, targetSampleRate = TARGET_SAMPLE_RATE) {
    try {
        if (!blob || blob.size === 0) {
            console.warn('⚠️ Blob vacío, usando audio original');
            return blob;
        }

        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (!AudioCtx) {
            console.warn('⚠️ AudioContext no disponible en este navegador, se envía audio original');
            return blob;
        }

        const arrayBuffer = await blob.arrayBuffer();
        const audioContext = new AudioCtx();

        const audioBuffer = await new Promise((resolve, reject) => {
            audioContext.decodeAudioData(
                arrayBuffer,
                (decoded) => resolve(decoded),
                (error) => reject(error)
            );
        });

        await audioContext.close();

        const numberOfChannels = audioBuffer.numberOfChannels;
        const duration = audioBuffer.duration;
        const length = Math.ceil(duration * targetSampleRate);

        const offlineContext = new OfflineAudioContext(numberOfChannels, length, targetSampleRate);
        const source = offlineContext.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(offlineContext.destination);
        source.start(0);

        const renderedBuffer = await offlineContext.startRendering();

        const wavArrayBuffer = audioBufferToWav(renderedBuffer);
        return new Blob([wavArrayBuffer], { type: 'audio/wav' });
    } catch (error) {
        console.warn('⚠️ Error convirtiendo audio a WAV. Se envía original.', error);
        return blob;
    }
}

function audioBufferToWav(buffer) {
    const numChannels = buffer.numberOfChannels;
    const sampleRate = buffer.sampleRate;
    const format = 1;
    const bitDepth = 16;

    const numSamples = buffer.length;
    const bytesPerSample = bitDepth / 8;
    const blockAlign = numChannels * bytesPerSample;
    const byteRate = sampleRate * blockAlign;
    const dataLength = numSamples * blockAlign;
    const bufferLength = 44 + dataLength;

    const arrayBuffer = new ArrayBuffer(bufferLength);
    const view = new DataView(arrayBuffer);

    let offset = 0;

    function writeString(str) {
        for (let i = 0; i < str.length; i++) {
            view.setUint8(offset++, str.charCodeAt(i));
        }
    }

    function writeUint32(value) {
        view.setUint32(offset, value, true);
        offset += 4;
    }

    function writeUint16(value) {
        view.setUint16(offset, value, true);
        offset += 2;
    }

    writeString('RIFF');
    writeUint32(36 + dataLength);
    writeString('WAVE');
    writeString('fmt ');
    writeUint32(16);
    writeUint16(format);
    writeUint16(numChannels);
    writeUint32(sampleRate);
    writeUint32(byteRate);
    writeUint16(blockAlign);
    writeUint16(bitDepth);
    writeString('data');
    writeUint32(dataLength);

    const interleaved = interleave(buffer);
    const volume = 32767;
    for (let i = 0; i < interleaved.length; i++, offset += 2) {
        let sample = Math.max(-1, Math.min(1, interleaved[i]));
        view.setInt16(offset, sample < 0 ? sample * volume : sample * volume, true);
    }

    return arrayBuffer;
}

function interleave(buffer) {
    const numChannels = buffer.numberOfChannels;
    const length = buffer.length;
    const result = new Float32Array(length * numChannels);
    let index = 0;

    for (let i = 0; i < length; i++) {
        for (let channel = 0; channel < numChannels; channel++) {
            result[index++] = buffer.getChannelData(channel)[i];
        }
    }

    return result;
}

// Configurar análisis de audio en tiempo real del usuario
function configurarAnalisisAudioUsuario(stream) {
    try {
        if (!userAudioContext) {
            userAudioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
        
        if (!userAnalyserNode) {
            const source = userAudioContext.createMediaStreamSource(stream);
            userAnalyserNode = userAudioContext.createAnalyser();
            userAnalyserNode.fftSize = 256;
            source.connect(userAnalyserNode);
        }
        
        window.userAudioAnalyser = userAnalyserNode;
        console.log('✅ Análisis de audio del usuario configurado');
    } catch (error) {
        console.warn('⚠️ No se pudo configurar análisis de audio del usuario:', error);
    }
}

// Iniciar análisis de audio del usuario en tiempo real
function iniciarAnalisisAudioUsuario() {
    if (!window.userAudioAnalyser || !window.systemActive || !window.systemActive()) {
        return;
    }
    
    const dataArray = new Uint8Array(window.userAudioAnalyser.frequencyBinCount);
    
    function analizarAudioUsuario() {
        if (!window.userAudioAnalyser || !window.systemActive || !window.systemActive()) {
            return;
        }
        
        window.userAudioAnalyser.getByteFrequencyData(dataArray);
        
        // Calcular nivel promedio
        const sum = dataArray.reduce((a, b) => a + b, 0);
        const average = sum / dataArray.length;
        const level = average / 255; // Normalizar 0-1
        
        // Aplicar umbral mínimo para evitar ruido de fondo
        const threshold = 0.05;
        const adjustedLevel = level > threshold ? (level - threshold) / (1 - threshold) : 0;
        
        // Actualizar nivel de voz del usuario
        if (window.updateUserVoiceLevel) {
            window.updateUserVoiceLevel(adjustedLevel);
        }
        
        requestAnimationFrame(analizarAudioUsuario);
    }
    
    analizarAudioUsuario();
}

// Exponer función globalmente
window.iniciarAnalisisAudioUsuario = iniciarAnalisisAudioUsuario;

// Verificar soporte de getUserMedia
function verificarSoporteMicrofono() {
    console.log('🔍 Verificando soporte de micrófono...');
    console.log('📍 Hostname:', location.hostname);
    console.log('🔒 Protocolo:', location.protocol);
    console.log('🛡️ isSecureContext:', window.isSecureContext);
    console.log('📱 navigator.mediaDevices:', navigator.mediaDevices);
    
    // Verificar si estamos en un contexto seguro (HTTPS o localhost)
    // NOTA: Los navegadores modernos permiten micrófono en HTTP si es localhost o 127.0.0.1
    // Para servidores remotos, se recomienda HTTPS, pero algunos navegadores lo permiten en HTTP
    const isSecureContext = window.isSecureContext || 
                           location.protocol === 'https:' || 
                           location.hostname === 'localhost' || 
                           location.hostname === '127.0.0.1' ||
                           location.hostname === '[::1]' ||
                           location.hostname.startsWith('192.168.') ||  // Red local privada
                           location.hostname.startsWith('10.') ||      // Red local privada
                           location.hostname.startsWith('172.16.');    // Red local privada
    
    if (!isSecureContext && location.protocol !== 'https:') {
        console.warn('⚠️ No estás en un contexto completamente seguro');
        console.warn('   Protocolo actual:', location.protocol);
        console.warn('   Hostname actual:', location.hostname);
        console.warn('   Algunos navegadores pueden requerir HTTPS para acceder al micrófono');
        // No retornamos false aquí, intentamos de todos modos
    }
    
    // Verificar soporte de mediaDevices
    if (!navigator.mediaDevices) {
        console.error('❌ navigator.mediaDevices no está disponible');
        console.log('🔍 Intentando fallback a API legacy...');
        
        // Fallback para navegadores antiguos
        if (navigator.getUserMedia) {
            console.warn('⚠️ Usando API legacy getUserMedia');
            navigator.mediaDevices = {
                getUserMedia: function(constraints) {
                    return new Promise((resolve, reject) => {
                        navigator.getUserMedia(constraints, resolve, reject);
                    });
                }
            };
        } else if (navigator.webkitGetUserMedia) {
            console.warn('⚠️ Usando API legacy webkitGetUserMedia');
            navigator.mediaDevices = {
                getUserMedia: function(constraints) {
                    return new Promise((resolve, reject) => {
                        navigator.webkitGetUserMedia(constraints, resolve, reject);
                    });
                }
            };
        } else if (navigator.mozGetUserMedia) {
            console.warn('⚠️ Usando API legacy mozGetUserMedia');
            navigator.mediaDevices = {
                getUserMedia: function(constraints) {
                    return new Promise((resolve, reject) => {
                        navigator.mozGetUserMedia(constraints, resolve, reject);
                    });
                }
            };
        } else {
            console.error('❌ No se encontró ninguna API de getUserMedia disponible');
            return false;
        }
    }
    
    if (!navigator.mediaDevices.getUserMedia) {
        console.error('❌ getUserMedia no está disponible en navigator.mediaDevices');
        return false;
    }
    
    console.log('✅ Soporte de micrófono verificado correctamente');
    return true;
}

// Inicializar captura de audio
async function iniciarCaptura() {
    try {
        // Verificar soporte antes de intentar acceder
        if (!verificarSoporteMicrofono()) {
            throw new Error('El navegador no soporta acceso al micrófono. Usa HTTPS o localhost.');
        }
        
        if (!audioStream) {
            console.log('🎤 Solicitando acceso al micrófono...');
            
            // Verificación adicional justo antes de usar getUserMedia
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error('navigator.mediaDevices.getUserMedia no está disponible. Verifica que estés usando HTTPS o localhost.');
            }
            
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
            
            // Configurar análisis de audio en tiempo real del usuario
            configurarAnalisisAudioUsuario(audioStream);
            
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
                
                // Resetear nivel de voz del usuario cuando termina de grabar
                if (window.updateUserVoiceLevel) {
                    window.updateUserVoiceLevel(0);
                }
                
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

        // Convertir audio a WAV (Whisper prefiere PCM lineal)
        let audioToSend = audioBlob;
        try {
            audioToSend = await convertBlobToWav(audioBlob);
        } catch (conversionError) {
            console.warn('⚠️ Error al convertir audio a WAV:', conversionError);
            audioToSend = audioBlob;
        }

        const audioFilename = audioToSend.type === 'audio/wav' ? 'voice.wav' : 'voice.webm';
        formData.append('audio', audioToSend, audioFilename);
        formData.append('language', 'es');
        
        // IMPORTANTE: Solo enviar session_id si existe y no fue reseteado por un error
        // Si conversationId es null, el backend creará una conversación nueva
        if (conversationId) {
            formData.append('session_id', conversationId);
        }
        // Si conversationId es null, no enviar nada y el backend generará un nuevo UUID

        // Enviar al backend
        console.log(`🚀 Enviando audio al backend: ${audioBlob.size} bytes`);
        const response = await fetch(API_VOICE_ENDPOINT, {
            method: 'POST',
            body: formData
        });

        console.log(`📡 Respuesta recibida: ${response.status} ${response.statusText}`);

        if (!response.ok) {
            let errorMessage = `Error ${response.status}`;
            let errorDetail = '';
            
            try {
                const errorText = await response.text();
                console.error('❌ Error del backend:', errorText);
                
                // Intentar parsear como JSON
                try {
                    const errorJson = JSON.parse(errorText);
                    errorDetail = errorJson.detail || errorJson.message || errorText;
                    
                    // Detectar tipos específicos de error
                    if (errorDetail.includes('limpiada automáticamente') || errorDetail.includes('ha sido limpiada')) {
                        // El backend ya limpió el historial automáticamente
                        errorMessage = '✅ Problema resuelto automáticamente';
                        errorDetail = 'El modelo no reconocía alguna palabra en el historial. ' +
                            'La conversación ha sido limpiada automáticamente. ' +
                            'Por favor, intenta de nuevo con tu mensaje.';
                    } else if (errorDetail.includes('out of vocabulary') || (errorDetail.includes('Token') && errorDetail.includes('out of vocabulary'))) {
                        errorMessage = '⚠️ Error: palabra no reconocida';
                        errorDetail = 'El modelo no puede procesar alguna palabra en el historial de conversación.\n\n' +
                            'Esto puede deberse a:\n' +
                            '• Palabras poco comunes en conversaciones anteriores (como "karaoke")\n' +
                            '• El historial contiene palabras que el modelo no reconoce\n\n' +
                            '💡 Limpiando el historial automáticamente...';
                        
                        // CRÍTICO: Limpiar conversación ANTES de resetear conversationId
                        // Guardar el conversationId actual antes de limpiarlo
                        const currentConversationId = conversationId;
                        
                        if (currentConversationId) {
                            console.log('🧹 Limpiando conversación existente con palabras problemáticas:', currentConversationId);
                            try {
                                const clearUrl = isDocker ? `/api/conversation/${currentConversationId}` : `${CONFIG.BACKEND_URL}/api/conversation/${currentConversationId}`;
                                const clearResponse = await fetch(clearUrl, { method: 'DELETE' });
                                if (clearResponse.ok) {
                                    console.log('✅ Conversación limpiada en backend');
                                } else {
                                    console.warn('⚠️ No se pudo limpiar conversación en backend');
                                }
                            } catch (clearError) {
                                console.warn('⚠️ Error al limpiar conversación:', clearError);
                            }
                        }
                        
                        // SIEMPRE resetear conversationId para forzar nueva conversación limpia
                        // Esto asegura que la próxima petición NO envíe session_id
                        conversationId = null;
                        console.log('🔄 ConversationId reseteado a null - próxima petición creará conversación nueva');
                        
                        // Mostrar mensaje de confirmación
                        if (window.addAIMessage) {
                            setTimeout(() => {
                                window.addAIMessage('✅ Historial limpiado completamente. La próxima vez será una conversación nueva y limpia.\n\nPor favor, intenta de nuevo con tu mensaje.');
                            }, 500);
                        }
                    } else if (errorDetail.includes('vocabulario limitado') || 
                               (errorDetail.includes('vocabulary') && errorDetail.includes('limitado')) ||
                               (errorDetail.includes('modelo de transcripción') && errorDetail.includes('tiny'))) {
                        errorMessage = 'Error: Modelo de transcripción con vocabulario limitado';
                        errorDetail = 'El modelo Whisper "tiny" tiene un vocabulario limitado y no puede transcribir algunas palabras. ' +
                            'Intenta usar palabras más comunes o considera cambiar a un modelo más grande (base, small, medium).';
                    } else if (errorDetail.includes('Whisper transcription error') || errorDetail.includes('Whisper no pudo')) {
                        errorMessage = '⚠️ Error de transcripción de voz';
                        errorDetail = 'Whisper no pudo procesar el audio. Esto puede deberse a:\n\n' +
                            '• Palabras poco comunes que el modelo "tiny" no reconoce\n' +
                            '• Calidad de audio insuficiente\n' +
                            '• Ruido de fondo excesivo\n\n' +
                            '💡 Solución: Intenta hablar más claro y usar palabras más comunes.';
                        
                        // Resetear conversationId para próxima vez
                        conversationId = null;
                        console.log('🔄 ConversationId reseteado debido a error de Whisper');
                        
                        // Intentar limpiar si existe conversación
                        limpiarConversacion().catch(() => {
                            // Ignorar si no hay conversación
                        });
                    } else if (errorDetail.includes('LLM') || errorDetail.includes('language model')) {
                        errorMessage = 'Error del modelo de lenguaje';
                        errorDetail = 'El modelo de IA no pudo generar una respuesta. Intenta de nuevo.';
                    } else if (errorDetail.includes('TTS') || errorDetail.includes('text-to-speech')) {
                        errorMessage = 'Error de síntesis de voz';
                        errorDetail = 'No se pudo generar el audio de respuesta.';
                    } else {
                        errorMessage = 'Error al procesar la solicitud';
                    }
                } catch (parseError) {
                    // Si no es JSON, usar el texto directamente
                    errorDetail = errorText || `Error ${response.status}: ${response.statusText}`;
                }
            } catch (textError) {
                errorDetail = `Error ${response.status}: ${response.statusText}`;
            }
            
            // Mostrar error en el chat dorado
            if (window.addAIMessage) {
                let errorText = '';
                
                // Si el backend ya limpió automáticamente, mostrar mensaje positivo
                if (errorDetail.includes('limpiada automáticamente') || errorDetail.includes('ha sido limpiada')) {
                    errorText = `${errorMessage}\n\n${errorDetail}`;
                } else {
                    errorText = `⚠️ ${errorMessage}\n\n${errorDetail}`;
                    
                    // Si es error de vocabulario, ya se limpió arriba, solo mostrar mensaje
                    if (!errorDetail.includes('out of vocabulary') && !errorDetail.includes('Limpia la conversación')) {
                        errorText += '\n\nPor favor, intenta de nuevo.';
                    }
                }
                
                window.addAIMessage(errorText);
            }
            
            throw new Error(errorDetail);
        }

        // Obtener headers (Base64 encoded)
        const sessionIdHeader = response.headers.get('X-Session-ID');
        const conversationIdHeader = response.headers.get('X-Conversation-Id'); // Fallback
        const transcribedTextHeader = response.headers.get('X-Transcribed-Text');
        const llmResponseHeader = response.headers.get('X-Response-Text');

        // Decodificar session ID con manejo de errores
        // Priorizar X-Session-ID, luego X-Conversation-Id como fallback
        const idHeader = sessionIdHeader || conversationIdHeader;
        if (idHeader) {
            try {
                // Intentar decodificar Base64 primero
                conversationId = atob(idHeader);
            } catch (e) {
                // Si no es Base64, usar directamente
                console.log('Session ID no es Base64, usando directamente');
                conversationId = idHeader;
            }
            console.log('📝 Session ID recibido del backend:', conversationId);
        } else {
            console.log('⚠️ No se recibió Session ID del backend');
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
        
        // Determinar mensaje de estado según el tipo de error
        let statusMessage = 'Error de conexión';
        if (error.message.includes('transcripción') || error.message.includes('Whisper')) {
            statusMessage = 'Error de transcripción';
        } else if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
            statusMessage = 'Sin conexión';
            console.error('No se pudo conectar con el backend. Verifica que esté corriendo en', CONFIG.BACKEND_URL);
        } else if (error.message.includes('modelo de lenguaje') || error.message.includes('LLM')) {
            statusMessage = 'Error del modelo';
        } else if (error.message.includes('síntesis') || error.message.includes('TTS')) {
            statusMessage = 'Error de audio';
        }
        
        if (window.statusText) window.statusText.textContent = statusMessage;
        if (window.setSystemActive) window.setSystemActive(false);
        
        // El error ya se mostró en el chat si fue un error del backend (500, etc.)
        // Solo mostrar aquí si es un error de red
        if (error.message.includes('Failed to fetch') && !window.addAIMessage) {
            // Fallback si no hay chat disponible
            alert(`Error de conexión: No se pudo conectar con el backend.\n\nVerifica que el servidor esté corriendo en ${CONFIG.BACKEND_URL}`);
        }
    }
}

// Reproducir respuesta con sincronización visual
async function reproducirRespuesta(audioBlob) {
    try {
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);

        // Marcar que la IA está hablando
        if (window.setIsAISpeaking) {
            window.setIsAISpeaking(true);
        }
        
        // Resetear nivel de voz del usuario mientras la IA habla
        if (window.updateUserVoiceLevel) {
            window.updateUserVoiceLevel(0);
        }

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
                if (window.setIsAISpeaking) {
                    window.setIsAISpeaking(false);
                }
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
            if (window.setIsAISpeaking) {
                window.setIsAISpeaking(false);
            }
            if (window.setSystemActive) window.setSystemActive(false);
            URL.revokeObjectURL(audioUrl);
        };

        // Reproducir audio
        await audio.play();
        actualizarOrbeConAudio();
        
        // Cuando termine, resetear
        audio.onended = () => {
            window.updateAIVoiceLevel(0);
            if (window.setIsAISpeaking) {
                window.setIsAISpeaking(false);
            }
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
        if (window.setIsAISpeaking) {
            window.setIsAISpeaking(false);
        }
        if (window.setSystemActive) window.setSystemActive(false);
    }
}

// Verificar salud del backend
async function verificarBackend() {
    try {
        const healthUrl = isDocker ? '/api/health' : `${CONFIG.BACKEND_URL}/api/health`;
        const response = await fetch(healthUrl);
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
    
    // Limpiar recursos de análisis de audio del usuario
    if (userAudioContext) {
        userAudioContext.close().catch(console.error);
        userAudioContext = null;
    }
    userAnalyserNode = null;
    window.userAudioAnalyser = null;
    
    window.audioChunks = [];
    window.mediaRecorder = null;
}

// Limpiar conversación en el backend
async function limpiarConversacion() {
    if (!conversationId) {
        console.log('No hay conversación activa para limpiar');
        // Aun así, asegurarse de que conversationId esté en null
        conversationId = null;
        return;
    }
    
    try {
        console.log('🧹 Limpiando conversación:', conversationId);
        const clearUrl = isDocker ? `/api/conversation/${conversationId}` : `${CONFIG.BACKEND_URL}/api/conversation/${conversationId}`;
        
        const response = await fetch(clearUrl, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            console.log('✅ Conversación limpiada en el backend');
            // Resetear conversationId para crear una nueva en el próximo mensaje
            conversationId = null;
        } else {
            console.warn('⚠️ No se pudo limpiar la conversación en el backend');
            // Aun así, resetear el conversationId localmente
            conversationId = null;
        }
    } catch (error) {
        console.error('❌ Error al limpiar conversación:', error);
        // Aun así, resetear el conversationId localmente
        conversationId = null;
    }
}

// Exponer funciones necesarias globalmente
window.iniciarCaptura = iniciarCaptura;
window.enviarAudioAlBackend = enviarAudioAlBackend;
window.reproducirRespuesta = reproducirRespuesta;
window.limpiarRecursosAudio = limpiarRecursosAudio;
window.limpiarConversacion = limpiarConversacion;

// Verificar backend al cargar (opcional, solo para logging)
window.addEventListener('load', async () => {
    const backendDisponible = await verificarBackend();
    if (!backendDisponible) {
        console.warn('⚠️ Backend no disponible. Asegúrate de que esté corriendo en', CONFIG.BACKEND_URL);
    }
});

