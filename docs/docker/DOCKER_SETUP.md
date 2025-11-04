# 🐳 A.R.C.A LLM - Setup con Docker

## 🚀 Inicio Rápido

### 1. Prerequisitos

- **Docker Desktop** instalado y corriendo
- **LM Studio** corriendo en tu máquina host en `http://192.168.1.38:1234`
- **Modelo qwen/qwen3-4b-2507** cargado en LM Studio

---

### 2. Iniciar con Docker Compose

```bash
# Construir la imagen (primera vez o después de cambios)
docker-compose build

# Iniciar el servicio
docker-compose up

# O en modo detached (background)
docker-compose up -d
```

---

### 3. Acceder a la Aplicación

Abre tu navegador en: **http://localhost:8000**

---

### 4. Ver Logs

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver logs específicos del servicio
docker-compose logs -f arca-llm
```

---

### 5. Detener el Servicio

```bash
# Detener (mantiene los contenedores)
docker-compose stop

# Detener y eliminar contenedores
docker-compose down

# Detener, eliminar y limpiar volúmenes
docker-compose down -v
```

---

## 🔧 Configuración

### Variables de Entorno

Todas las configuraciones están en `docker-compose.yml` bajo la sección `environment`:

```yaml
environment:
  # LLM
  LM_STUDIO_URL: "http://host.docker.internal:1234/v1"
  LM_STUDIO_MODEL: "qwen/qwen3-4b-2507"
  
  # Whisper
  WHISPER_MODEL: "tiny"  # tiny, base, small, medium, large
  
  # TTS
  TTS_RATE: "175"
  TTS_VOLUME: "0.9"
```

**Para cambiar configuración:**
1. Editar `docker-compose.yml`
2. Reiniciar: `docker-compose restart`

---

## 📦 Persistencia de Datos

Los modelos descargados se guardan en:
- `./models/hf_cache/` - Modelos Whisper
- `./logs/` - Logs de la aplicación

**Estos directorios persisten entre reinicios.**

---

## 🔍 Troubleshooting

### Problema: No puede conectar con LM Studio

**Solución:**
1. Verificar que LM Studio esté corriendo
2. Verificar que el servidor local esté en puerto `1234`
3. En Windows/Mac, Docker usa `host.docker.internal` para el host

### Problema: Puerto 8000 ya en uso

**Solución:**
Cambiar puerto en `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Usar puerto 8001 en lugar de 8000
```

### Problema: Modelo Whisper descarga lento

**Solución:**
Primera vez toma 1-2 minutos. Luego se cachea en `./models/`

### Ver logs de errores

```bash
docker-compose logs --tail=100 arca-llm
```

---

## 🛠️ Comandos Útiles

```bash
# Reconstruir imagen (después de cambios en requirements.txt)
docker-compose build --no-cache

# Reiniciar servicio
docker-compose restart

# Ver estado
docker-compose ps

# Entrar al contenedor
docker-compose exec arca-llm bash

# Ver uso de recursos
docker stats
```

---

## 🚀 Modo Desarrollo

Para desarrollo con hot-reload, el código está montado como volumen:

```yaml
volumes:
  - ./src:/app/src  # Cambios en código se reflejan automáticamente
```

**Uvicorn detecta cambios automáticamente y recarga.**

---

## 📊 Recursos del Sistema

**Configuración actual:**
- CPU: 2-4 cores
- RAM: 4-8 GB

**Para ajustar:**
Editar en `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 4G
```

---

## ✅ Checklist de Inicio

- [ ] Docker Desktop instalado y corriendo
- [ ] LM Studio corriendo en puerto 1234
- [ ] Modelo Qwen3-8B cargado en LM Studio
- [ ] Puerto 8000 disponible
- [ ] Ejecutar: `docker-compose up`
- [ ] Abrir: http://localhost:8000
- [ ] Probar conversación con el micrófono

---

## 🎯 Ventajas de Docker

✅ **Sin conflictos de dependencias**  
✅ **Mismo entorno en cualquier máquina**  
✅ **Fácil deploy**  
✅ **Aislamiento completo**  
✅ **Rollback fácil**  

---

## 📝 Notas

- Primera vez toma 5-10 minutos (descarga imagen Python + dependencias)
- Modelos Whisper se descargan la primera vez (automático)
- Los logs se guardan en `./logs/`
- Para actualizar código: los cambios en `./src/` se reflejan automáticamente

