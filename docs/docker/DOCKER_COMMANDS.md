# 🐳 A.R.C.A LLM - Comandos Docker Compose

## 🚀 Comandos Básicos

### Iniciar el Sistema
```bash
# Primera vez o después de cambios
docker-compose up --build

# Inicio normal
docker-compose up

# En background (detached)
docker-compose up -d
```

### Detener el Sistema
```bash
# Detener servicios (mantiene contenedores)
docker-compose stop

# Detener y eliminar contenedores
docker-compose down

# Detener y limpiar TODO (incluyendo modelos descargados)
docker-compose down -v
```

### Ver Estado
```bash
# Ver servicios corriendo
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f

# Ver últimas 50 líneas de logs
docker-compose logs --tail=50

# Ver logs específicos de arca-llm
docker-compose logs -f arca-llm
```

---

## 🔧 Comandos de Desarrollo

### Reconstruir Imagen
```bash
# Reconstruir sin caché (después de cambiar requirements.txt)
docker-compose build --no-cache

# Reconstruir y arrancar
docker-compose up --build
```

### Reiniciar Servicio
```bash
# Reiniciar sin reconstruir
docker-compose restart

# Reiniciar específico
docker-compose restart arca-llm
```

### Acceder al Contenedor
```bash
# Entrar con bash
docker-compose exec arca-llm bash

# Ejecutar comando específico
docker-compose exec arca-llm python --version
```

---

## 📊 Monitoreo

### Ver Uso de Recursos
```bash
# Ver CPU, RAM, Network en tiempo real
docker stats

# Ver solo de A.R.C.A
docker stats arca-llm
```

### Health Check Manual
```bash
# Verificar salud del servicio
curl http://localhost:8000/api/health

# O con formato bonito
curl -s http://localhost:8000/api/health | python -m json.tool
```

---

## 🧹 Limpieza

### Limpiar Contenedores Detenidos
```bash
docker container prune
```

### Limpiar Imágenes No Usadas
```bash
docker image prune
```

### Limpiar Todo (Peligroso!)
```bash
# ⚠️ Elimina TODOS los contenedores, redes, imágenes no usadas
docker system prune -a

# Con volúmenes también
docker system prune -a --volumes
```

---

## 🔍 Debugging

### Ver Logs con Timestamps
```bash
docker-compose logs -f --timestamps
```

### Ver Solo Errores
```bash
docker-compose logs | grep ERROR
```

### Inspeccionar Contenedor
```bash
docker inspect arca-llm
```

### Ver Variables de Entorno
```bash
docker-compose exec arca-llm env
```

---

## 📦 Gestión de Volúmenes

### Ver Volúmenes
```bash
docker volume ls
```

### Inspeccionar Volumen
```bash
docker volume inspect arca-llm_models
```

### Eliminar Volúmenes No Usados
```bash
docker volume prune
```

---

## 🎯 Comandos Comunes del Día a Día

```bash
# Iniciar A.R.C.A
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f

# Reiniciar después de cambios en código
docker-compose restart

# Detener A.R.C.A
docker-compose down

# Ver estado y uso de recursos
docker-compose ps
docker stats arca-llm
```

---

## ⚡ Tips

### Inicio Rápido
```bash
# Alias útil (agregar a .bashrc o .zshrc)
alias arca-up="docker-compose up -d"
alias arca-down="docker-compose down"
alias arca-logs="docker-compose logs -f"
alias arca-restart="docker-compose restart"
```

### Ver Todo en Un Comando
```bash
# Estado + Logs + Recursos
docker-compose ps && docker-compose logs --tail=20 && docker stats --no-stream arca-llm
```

---

## 🆘 Solución de Problemas

### Problema: Contenedor no arranca
```bash
# Ver logs detallados
docker-compose logs arca-llm

# Reconstruir desde cero
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Problema: Cambios en código no se reflejan
```bash
# Verificar que el volumen esté montado
docker-compose exec arca-llm ls -la /app/src

# Reiniciar
docker-compose restart
```

### Problema: Puerto ocupado
```bash
# Ver qué está usando el puerto
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# O cambiar puerto en docker-compose.yml
```

---

## 📝 Notas

- **Hot reload:** Los cambios en `./src/` se detectan automáticamente
- **Modelos:** Se guardan en `./models/` y persisten entre reinicios
- **Logs:** Se guardan en `./logs/` y persisten entre reinicios
- **Health check:** Docker verifica salud cada 30 segundos automáticamente

