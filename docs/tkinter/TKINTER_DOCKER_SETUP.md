# 🐳 Tkinter + Docker Setup

## 🎯 Problema

**Tkinter necesita display gráfico**, y Docker containers **no tienen acceso al display del host por defecto**.

---

## ✅ Solución Recomendada: Híbrido

**Backend en Docker + Frontend Tkinter Local**

### Ventajas:
- ✅ Fácil de configurar
- ✅ No requiere X11 forwarding
- ✅ Performance completo del display nativo
- ✅ Backend aislado en Docker
- ✅ Frontend con acceso completo a GPU/display

### Setup:

```bash
# 1. Iniciar backend en Docker
docker-compose up -d

# 2. Verificar que funciona
curl http://localhost:8000/api/health

# 3. Ejecutar frontend Tkinter local
python run_tkinter_local.py
```

---

## ⚠️ Alternativa: Todo en Docker (NO RECOMENDADO)

**Esta opción NO está implementada** porque:
- ❌ Muy complejo en Mac (requiere XQuartz + X11 forwarding)
- ❌ Performance inferior vs solución híbrida
- ❌ Difícil de mantener
- ❌ Más lento que Tkinter nativo

**Si realmente necesitas correr GUI en Docker:**
1. Considerar usar VNC en lugar de X11
2. O mejor aún: usar el frontend web (más portable)
3. La solución híbrida es siempre mejor para desarrollo

---

## 📊 Comparación de Opciones

| Aspecto | Híbrido (Local+Docker) | Todo Docker |
|---------|------------------------|-------------|
| **Setup** | ✅ Fácil | ⚠️ Complejo |
| **Performance** | ✅ Nativo | ⚠️ Overhead |
| **Mac** | ✅ Funciona | ⚠️ XQuartz requerido |
| **Linux** | ✅ Funciona | ✅ Funciona (con X11) |
| **Windows** | ✅ Funciona | ❌ No soportado |
| **Mantenimiento** | ✅ Simple | ⚠️ Complejo |

---

## 🎯 Recomendación

**Usar solución híbrida:**

```bash
# Backend API en Docker
docker-compose up -d

# Frontend Tkinter local
python run_tkinter_local.py
```

**Frontend local se conecta a API en Docker vía http://localhost:8000**

---

## 🔧 Scripts Disponibles

### `run_tkinter_local.py`

Ejecuta interfaz Tkinter local que se conecta al backend en Docker.

```bash
python run_tkinter_local.py
```

### `docker-compose.yml` (Original)

Docker compose estándar del proyecto - usa este.

```bash
docker-compose up -d
```

---

## ❓ FAQ

### ¿Por qué no funciona Tkinter en Docker?

Tkinter es una biblioteca GUI que necesita:
- Sistema de ventanas (X11, Wacom, etc.)
- Display graphics hardware
- Event loop con acceso al sistema operativo

Docker containers son **headless** por diseño.

### ¿Puedo usar el frontend web en lugar de Tkinter?

¡Sí! El frontend web (FastAPI + HTML/JS) funciona perfectamente en Docker:

```bash
docker-compose up
# Abrir http://localhost:8000
```

### ¿Cuándo usar Tkinter vs Web?

**Usar Tkinter cuando:**
- Necesitas interfaz desktop nativa
- Quieres orbe siempre visible
- Prefieres aplicación standalone

**Usar Web cuando:**
- Deployment en servidor
- Acceso desde múltiples dispositivos
- No quieres instalar nada en cliente

---

## 📝 Notas

- Frontend web sigue disponible en puerto 8000
- Tkinter es una **alternativa**, no reemplazo
- Ambos frontends usan el mismo backend/API
- Elegir según necesidad

---

**Actualizado:** 2025-11-04  
**Status:** Documentado

