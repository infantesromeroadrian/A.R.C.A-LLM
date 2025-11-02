/* ===== GESTOR DE ESTADO ===== */

// Elementos del DOM
const statusText = document.getElementById('statusText');
const freqBars = document.getElementById('freqBars');
const clickHint = document.getElementById('clickHint');
const orbeCircle = document.querySelector('.orbe-circle');
const orbeCircle2 = document.querySelector('.orbe-circle-2');
const highlightTextEl = document.querySelector('.highlight-text');

// Variables de estado
let systemActive = false;
let currentPulse = 0;
let currentVoiceLevel = 0;
let targetVoiceLevel = 0;

// Alternar estado del sistema con integración de backend
async function alternarSistema() {
    if (!systemActive) {
        // Activar sistema
        systemActive = true;
        actualizarInterfaz();
        
        // Inicializar captura si es la primera vez
        if (!window.mediaRecorder) {
            const success = await window.iniciarCaptura();
            if (!success) {
                systemActive = false;
                actualizarInterfaz();
                return;
            }
        }
        
        // Iniciar grabación
        window.audioChunks = [];
        if (window.mediaRecorder && window.mediaRecorder.state === 'inactive') {
            console.log('🎙️ Iniciando grabación de audio...');
            window.mediaRecorder.start(100); // Recibir chunks cada 100ms
            // Registrar tiempo de inicio para validación de duración mínima
            window.recordingStartTime = Date.now();
            statusText.textContent = 'Escuchando...';
            console.log('✅ Grabación iniciada');
        } else {
            console.warn('⚠️ MediaRecorder no disponible o ya está activo. Estado:', window.mediaRecorder?.state);
        }
        
    } else {
        // Desactivar sistema
        systemActive = false;
        actualizarInterfaz();
        
        // Detener grabación y enviar
        if (window.mediaRecorder && window.mediaRecorder.state === 'recording') {
            console.log('🛑 Deteniendo grabación de audio...');
            window.mediaRecorder.stop();
            statusText.textContent = 'Procesando...';
            console.log('✅ Grabación detenida, esperando evento onstop...');
        } else {
            console.warn('⚠️ MediaRecorder no está grabando. Estado:', window.mediaRecorder?.state);
        }
    }
}

// Actualizar interfaz según el estado
function actualizarInterfaz() {
    if (systemActive) {
        statusText.classList.add('active', 'listening');
        freqBars.classList.add('active');
        orbeCircle.classList.add('active');
        orbeCircle2.classList.add('active');
        if (highlightTextEl) highlightTextEl.classList.add('active');
        clickHint.style.display = 'none';
    } else {
        statusText.classList.remove('active', 'listening');
        freqBars.classList.remove('active');
        orbeCircle.classList.remove('active');
        orbeCircle2.classList.remove('active');
        if (highlightTextEl) highlightTextEl.classList.remove('active');
        clickHint.style.display = 'block';
    }
}

// Actualizar pulso del sistema
function actualizarPulso() {
    if (systemActive) {
        currentPulse = Math.min(1, currentPulse + 0.03);
    } else {
        currentPulse = Math.max(0, currentPulse - 0.02);
    }
}

// Actualizar nivel de voz con suavizado
function actualizarVoiceLevel() {
    const smoothFactor = 0.15;
    currentVoiceLevel += (targetVoiceLevel - currentVoiceLevel) * smoothFactor;
}

// Calcular intensidad combinada
function calcularIntensidad() {
    return systemActive 
        ? Math.max(currentPulse * 0.3, currentVoiceLevel) 
        : currentPulse;
}

// Exponer variables y funciones necesarias globalmente para backend-integration.js
window.statusText = statusText;
window.systemActive = () => systemActive;
window.setSystemActive = (value) => {
    systemActive = value;
    actualizarInterfaz();
};
window.actualizarInterfaz = actualizarInterfaz;
