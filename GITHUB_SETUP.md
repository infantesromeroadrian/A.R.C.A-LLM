# 🚀 GitHub Setup - A.R.C.A LLM

## Paso 1: Crear Repositorio en GitHub

### Opción A: Interfaz Web (Recomendado)

1. Ve a https://github.com/new
2. Configura el repositorio:
   - **Repository name**: `A.R.C.A-LLM` (o el nombre que prefieras)
   - **Description**: "Advanced Reasoning Cognitive Architecture - Voice Conversational AI with Memory"
   - **Visibility**: 
     - ✅ **Public** (si quieres compartir)
     - ✅ **Private** (si es solo para desarrollo)
   - **NO marques**:
     - ❌ Add a README file
     - ❌ Add .gitignore
     - ❌ Choose a license
   
3. Click **"Create repository"**

### Opción B: GitHub CLI (Si tienes gh instalado)

```bash
gh repo create A.R.C.A-LLM --public --description "Advanced Reasoning Cognitive Architecture - Voice AI"
```

---

## Paso 2: Vincular Tu Repositorio Local

Una vez creado el repositorio en GitHub, copia la URL SSH o HTTPS.

### SSH (Recomendado si tienes SSH configurado)
```bash
git remote add origin git@github.com:TU-USUARIO/A.R.C.A-LLM.git
git branch -M main
git push -u origin main
```

### HTTPS (Si no tienes SSH)
```bash
git remote add origin https://github.com/TU-USUARIO/A.R.C.A-LLM.git
git branch -M main
git push -u origin main
```

---

## Paso 3: Fork del Frontend

1. Ve a https://github.com/nacho995/msmk-voice-assistant
2. Click en **"Fork"** (esquina superior derecha)
3. Selecciona tu cuenta como destino
4. **NO** marques "Copy the main branch only" (queremos todas las ramas)
5. Click **"Create fork"**

---

## Paso 4: Clonar Tu Fork Localmente

```bash
# Cambiar al directorio padre (fuera de A.R.C.A-LLM)
cd ..

# Clonar TU fork (no el original de nacho995)
git clone git@github.com:TU-USUARIO/msmk-voice-assistant.git

# O con HTTPS:
git clone https://github.com/TU-USUARIO/msmk-voice-assistant.git

# Entrar al repositorio clonado
cd msmk-voice-assistant

# Agregar el repositorio original como "upstream"
git remote add upstream git@github.com:nacho995/msmk-voice-assistant.git

# Verificar remotes configurados
git remote -v
```

Deberías ver:
```
origin    git@github.com:TU-USUARIO/msmk-voice-assistant.git (fetch)
origin    git@github.com:TU-USUARIO/msmk-voice-assistant.git (push)
upstream  git@github.com:nacho995/msmk-voice-assistant.git (fetch)
upstream  git@github.com:nacho995/msmk-voice-assistant.git (push)
```

---

## Paso 5: Crear Rama de Integración

```bash
# Asegurarte de estar en main actualizado
git checkout main
git pull upstream main

# Crear rama para integración con backend
git checkout -b feature/backend-integration

# Push de la nueva rama a tu fork
git push -u origin feature/backend-integration
```

---

## 🎯 Estructura Final

Después de estos pasos tendrás:

```
📁 Projects/AI-Projects/
├── A.R.C.A-LLM/                          (Tu backend)
│   ├── .git/                             ← Repositorio git
│   ├── src/                              ← Código backend
│   ├── docker-compose.yml                ← Docker backend
│   └── ...
│
└── msmk-voice-assistant/                 (Fork del frontend)
    ├── .git/                             ← Repositorio git
    ├── (archivos frontend de nacho995)
    └── ...
```

---

## 🔄 Flujo de Trabajo Diario

### En A.R.C.A-LLM (Backend)

```bash
# Trabajar en features
git checkout -b feature/nueva-funcionalidad
# ... hacer cambios ...
git add .
git commit -m "feat: descripción del cambio"
git push origin feature/nueva-funcionalidad
```

### En msmk-voice-assistant (Frontend Fork)

```bash
# Sincronizar con nacho995 antes de trabajar
git checkout main
git pull upstream main
git push origin main

# Crear rama para cambios
git checkout -b feature/api-integration
# ... hacer cambios ...
git add .
git commit -m "feat: integrar con A.R.C.A LLM backend"
git push origin feature/api-integration

# Crear Pull Request desde GitHub hacia nacho995/main
```

---

## ⚠️ IMPORTANTE: Evitar Conflictos

### ✅ HACER:
1. Siempre trabajar en ramas feature
2. Sincronizar con upstream antes de empezar
3. PRs pequeños y específicos
4. Comunicarte con nacho995 antes de grandes cambios

### ❌ NO HACER:
1. NUNCA push directo a main
2. NO modificar archivos del frontend sin coordinación
3. NO hacer force push
4. NO olvidar sincronizar upstream

---

## 📝 Siguiente Paso

Una vez que hayas:
1. ✅ Creado el repositorio en GitHub
2. ✅ Copiado la URL

Dime "ok" y ejecutaré el comando para vincular tu repositorio local con GitHub.

**URL de tu nuevo repositorio:** `_________________` (completar después de crear)

