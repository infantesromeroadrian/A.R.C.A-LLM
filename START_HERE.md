# 🎯 A.R.C.A LLM - Empezar Aquí

## 🚀 Pasos para Iniciar (5 minutos)

### Paso 1: Verificar Prerequisitos

- [ ] **Docker Desktop instalado** (https://www.docker.com/products/docker-desktop)
- [ ] **Docker Desktop corriendo** (ver icono en systray)
- [ ] **LM Studio instalado**
- [ ] **LM Studio corriendo en puerto 1234**
- [ ] **Modelo Qwen3-8B cargado en LM Studio**

---

### Paso 2: Iniciar A.R.C.A

Abre una terminal en el directorio del proyecto:

```bash
docker-compose up
```

**Espera a ver:**
```
✅ A.R.C.A LLM is ready!
```

---

### Paso 3: Usar la Aplicación

1. Abre tu navegador
2. Ve a: **http://localhost:8000**
3. Click en el botón del micrófono 🎤
4. Habla
5. Click de nuevo para enviar
6. Espera la respuesta

---

## 📚 Documentación

- **[docs/docker/DOCKER_SETUP.md](docs/docker/DOCKER_SETUP.md)** - Documentación completa de Docker
- **[docs/docker/DOCKER_COMMANDS.md](docs/docker/DOCKER_COMMANDS.md)** - Todos los comandos útiles
- **[docs/setup/QUICK_START_DOCKER.md](docs/setup/QUICK_START_DOCKER.md)** - Guía rápida
- **[README.md](README.md)** - Información general del proyecto

---

## 🔧 Comandos Rápidos

```bash
# Iniciar
docker-compose up

# Iniciar en background
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down

# Reiniciar (después de cambios)
docker-compose restart
```

---

## ❓ ¿Problemas?

### "Cannot connect to LM Studio"
- ✅ Verificar que LM Studio esté corriendo
- ✅ Verificar que esté en puerto 1234
- ✅ Verificar que el modelo esté cargado

### "Port 8000 already in use"
- Editar `docker-compose.yml` y cambiar `8000:8000` a `8001:8000`

### Otros problemas
- Ver [docs/docker/DOCKER_SETUP.md](docs/docker/DOCKER_SETUP.md) sección "Troubleshooting"
- Ver [docs/troubleshooting/TEST_LM_STUDIO.md](docs/troubleshooting/TEST_LM_STUDIO.md) para problemas con LM Studio

---

## 🎉 ¡Listo!

Tu asistente de voz A.R.C.A está corriendo en:
**http://localhost:8000**

**¡Empieza a hablar con tu IA local!** 🎤🤖

