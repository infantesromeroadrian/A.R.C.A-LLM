# 🔧 Backend A.R.C.A-LLM

Backend del asistente de voz con integración STT, LLM y TTS.

## 🚀 Instalación

#### Con entorno virtual (si funciona en tu sistema)

```bash
python3 -m venv arca-venv
source arca-venv/bin/activate  # En Windows: arca-venv\Scripts\activate
pip install -r requirements.txt
```

#### Sin entorno virtual (instalación --user)

```bash
python3 -m pip install --user --upgrade pip setuptools wheel
python3 -m pip install --user -r requirements.txt
```

### Opción 3: Docker (Más fácil)

```bash
# Desde la raíz del proyecto
docker-compose up backend
```

## ▶️ Ejecutar

### Con el script de inicio

```bash
python3 run_arca.py
```

### Con uvicorn directamente

```bash
python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📋 Requisitos Previos

1. **LM Studio** corriendo en `http://127.0.0.1:1234`
2. **Modelo cargado** en LM Studio (ej: qwen/qwen3-4b-2507)
3. **Python 3.11+** instalado

## 🔧 Configuración

Crea un archivo `.env` en la raíz del proyecto (opcional):

```env
LM_STUDIO_URL=http://127.0.0.1:1234/v1
LM_STUDIO_MODEL=qwen/qwen3-4b-2507
WHISPER_MODEL=tiny
API_PORT=8000
```

## 📡 Endpoints

- `GET /api/health` - Health check
- `POST /api/voice/process` - Procesar audio
- `GET /api/conversation/{id}` - Obtener historial
- `GET /docs` - Documentación Swagger

## 🐛 Troubleshooting

### Error: "externally-managed-environment"

Usa `--user` para instalar:
```bash
python3 -m pip install --user -r requirements.txt
```

### Error: "venv no se crea correctamente"

Algunos sistemas tienen problemas con venv. Usa instalación `--user` directamente.

### Backend no inicia

1. Verifica que LM Studio esté corriendo
2. Verifica que el modelo esté cargado
3. Revisa los logs para más detalles

## 📚 Más Información

Ver [README principal](../README.md) para documentación completa.

