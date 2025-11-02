# 🎤 MSMK Voice Assistant - Frontend

Interfaz de usuario para el asistente de voz A.R.C.A LLM.

> 📁 Este es el directorio `frontend/` del proyecto MSMK Voice Assistant.

## 🚀 Inicio Rápido

### Opción 1: Con npm (recomendado)

```bash
# Instalar dependencias (solo la primera vez)
npm install

# Iniciar servidor en puerto 8080
npm start

# O abrir automáticamente en el navegador
npm run dev
```

### Opción 2: Con Python (sin npm)

```bash
# Python 3
python3 -m http.server 8080

# O con npm (usa Python internamente)
npm run serve
```

### Opción 3: Con npx (sin instalar)

```bash
npx http-server -p 8080
```

## 🌐 Acceso

Una vez iniciado, abre tu navegador en:

- **http://localhost:8080**

## 🔗 Integración con Backend

Este frontend requiere que el backend A.R.C.A-LLM esté corriendo en:

- **http://localhost:8000**

### Verificar Backend

```bash
curl http://localhost:8000/api/health
```

Debe retornar:

```json
{
  "status": "healthy",
  "service": "A.R.C.A LLM Voice Assistant"
}
```

## 📋 Requisitos Previos

- **Backend**: A.R.C.A-LLM corriendo en puerto 8000
- **Navegador**: Chrome, Firefox, Edge (soporta getUserMedia)
- **Micrófono**: Acceso permitido en el navegador

## 🛠️ Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `npm start` | Inicia servidor en puerto 8080 |
| `npm run dev` | Inicia servidor y abre navegador |
| `npm run serve` | Usa Python para servir (sin dependencias npm) |

## 📁 Estructura

```
ia interfaz/
├── index.html          # Página principal
├── css/               # Estilos
├── js/                # JavaScript
│   ├── backend-integration.js  # Integración con backend
│   ├── state.js       # Gestión de estado
│   └── ...
└── package.json       # Configuración npm
```

## 🐛 Troubleshooting

### "Failed to fetch"
- Verifica que el backend esté corriendo: `curl http://localhost:8000/api/health`
- Revisa la consola del navegador (F12)

### "Microphone access denied"
- Permite acceso al micrófono en la configuración del navegador
- Asegúrate de usar `localhost` (no `127.0.0.1`)

### Puerto 8080 ocupado
Cambia el puerto en `package.json`:

```json
"start": "http-server -p 3000 -c-1"
```

## 📚 Documentación Adicional

- [Guía de Integración Backend](./BACKEND_INTEGRATION.md)
- [Repositorio Backend](https://github.com/infantesromeroadrian/A.R.C.A-LLM)

