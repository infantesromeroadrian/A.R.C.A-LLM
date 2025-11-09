"""
FastAPI Application - A.R.C.A LLM Voice Assistant.

Aplicación principal que expone endpoints para conversación por voz.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
from loguru import logger

from ..config import settings
from ..infrastructure.stt.whisper_client import WhisperSTTClient
from ..infrastructure.llm.lm_studio_client import LMStudioClient
from ..infrastructure.tts.pyttsx3_client import Pyttsx3TTSClient
from ..application.conversation_service import ConversationService
from ..application.voice_assistant_service import VoiceAssistantService


# === Global State ===
voice_service: VoiceAssistantService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager para startup/shutdown.
    
    Inicializa todos los clientes al startup y limpia al shutdown.
    """
    global voice_service
    
    # === STARTUP ===
    logger.info("🚀 Starting A.R.C.A LLM...")
    settings.print_startup_info()
    
    # Inicializar clientes
    logger.info("📦 Initializing clients...")
    
    stt_client = WhisperSTTClient(
        **settings.get_whisper_config()
    )
    
    llm_client = LMStudioClient(
        **settings.get_lm_studio_config()
    )
    
    tts_client = Pyttsx3TTSClient(
        **settings.get_tts_config()
    )
    
    # Inicializar servicios
    conversation_service = ConversationService(max_messages_per_conversation=None)
    
    voice_service = VoiceAssistantService(
        stt_client=stt_client,
        llm_client=llm_client,
        tts_client=tts_client,
        conversation_service=conversation_service
    )
    
    # Health check
    logger.info("🏥 Running startup health check...")
    health = await voice_service.health_check()
    
    if not health["overall"]:
        logger.warning("⚠️ Some components are unhealthy, but starting anyway")
    
    logger.info("✅ A.R.C.A LLM is ready!")
    
    yield
    
    # === SHUTDOWN ===
    logger.info("🛑 Shutting down A.R.C.A LLM...")
    voice_service.cleanup()
    logger.info("👋 Goodbye!")


# === FastAPI App ===
app = FastAPI(
    title="A.R.C.A LLM",
    description="Advanced Reasoning Cognitive Architecture - Voice Conversational Assistant",
    version="1.0.0",
    lifespan=lifespan
)


# === CORS Middleware ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "X-Session-ID",
        "X-Transcribed-Text",
        "X-Response-Text",
        "X-Latency-Total",
        "X-Latency-STT",
        "X-Latency-LLM",
        "X-Latency-TTS"
    ],
)


# === Static Files ===
# Montar directorio static para CSS/JS (solo si existe, opcional)
static_path = Path(__file__).parent.parent / "frontend" / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


# === Routes ===
from .routes import voice_routes  # noqa: E402 - Import after app setup (required)

app.include_router(voice_routes.router, prefix="/api", tags=["voice"])


# === Root Endpoint ===
@app.get("/")
async def root():
    """
    Mostrar información de la API y redirigir al frontend principal.
    """
    from fastapi.responses import HTMLResponse
    
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>A.R.C.A LLM API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #333; }
            .info { background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }
            .link { display: inline-block; margin: 10px 0; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
            .link:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <h1>🤖 A.R.C.A LLM API</h1>
        <div class="info">
            <p><strong>Frontend Principal:</strong></p>
            <a href="http://localhost:3000" class="link">🚀 Ir al Frontend Principal (Puerto 3000)</a>
        </div>
        <div class="info">
            <h3>📡 Endpoints de la API:</h3>
            <ul>
                <li><a href="/docs">📚 Documentación Swagger</a></li>
                <li><a href="/api/health">🏥 Health Check</a></li>
                <li><code>POST /api/voice/process</code> - Procesar audio</li>
            </ul>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    health = await voice_service.health_check()
    
    return {
        "status": "healthy" if health["overall"] else "unhealthy",
        "components": health
    }


# === Para ejecutar con uvicorn ===
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower()
    )

