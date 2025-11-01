# ⚡ Quick Start - Docker en 5 Minutos

## 🎯 Lo Esencial

### 1. Instalar Docker Desktop

**Windows/Mac:**
- Descargar: https://www.docker.com/products/docker-desktop
- Instalar y abrir Docker Desktop
- Esperar a que inicie (icono en systray)

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo systemctl start docker
```

---

### 2. Configurar LM Studio

1. **Abrir LM Studio**
2. **Cargar modelo:**
   - Pestaña "Discover"
   - Buscar: `qwen3-8b`
   - Descargar
3. **Iniciar servidor:**
   - Pestaña "Local Server"
   - Port: `1234`
   - Click "Start Server"

---

### 3. Iniciar A.R.C.A con Docker

```bash
# En el directorio del proyecto
docker-compose up
```

**Primera vez toma ~5 minutos** (descarga imagen Python + dependencias)

---

### 4. Usar la Aplicación

1. Abrir navegador: **http://localhost:8000**
2. Click en botón del micrófono 🎤
3. Hablar
4. Click de nuevo para enviar
5. Esperar respuesta

---

## 🔧 Comandos Principales

```bash
# Iniciar
docker-compose up

# Iniciar en background
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down

# Reconstruir (después de cambios)
docker-compose build --no-cache
docker-compose up
```

---

## ❓ Problemas Comunes

### ❌ "Cannot connect to LM Studio"

**Solución:**
- Verificar que LM Studio esté corriendo
- Verificar puerto 1234
- Verificar que el modelo esté cargado

### ❌ "Port 8000 already in use"

**Solución:**
Editar `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Cambiar 8000 por 8001
```

### ❌ Modelo Whisper tarda mucho

**Primera vez descarga el modelo (~75MB)**  
**Siguientes veces es instantáneo** (está cacheado)

---

## ✅ Listo

**¡A.R.C.A ya está funcionando!** 🎉

Ver documentación completa: [DOCKER_SETUP.md](DOCKER_SETUP.md)

