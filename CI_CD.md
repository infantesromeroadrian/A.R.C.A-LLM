# 🚀 CI/CD - A.R.C.A-LLM

Documentación de Continuous Integration y Continuous Deployment.

---

## 📊 Status Badges

Añade estos badges a tu `README.md`:

```markdown
[![Tests](https://github.com/TU_USUARIO/A.R.C.A-LLM/actions/workflows/tests.yml/badge.svg)](https://github.com/TU_USUARIO/A.R.C.A-LLM/actions/workflows/tests.yml)
[![CI](https://github.com/TU_USUARIO/A.R.C.A-LLM/actions/workflows/ci.yml/badge.svg)](https://github.com/TU_USUARIO/A.R.C.A-LLM/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/TU_USUARIO/A.R.C.A-LLM/branch/main/graph/badge.svg)](https://codecov.io/gh/TU_USUARIO/A.R.C.A-LLM)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
```

**Reemplaza `TU_USUARIO` con tu username de GitHub.**

---

## 🔄 Workflows Configurados

### **1. Tests (`tests.yml`)** - Completo

**Se ejecuta en**: Push a `main`/`develop` y Pull Requests

**Jobs**:
- ✅ **Test** - Ejecuta suite completa de tests
  - Python 3.10 y 3.11
  - Coverage reports
  - Upload a Codecov
  
- ✅ **Lint** - Validación de código
  - Ruff (linting rápido)
  - MyPy (type checking)
  
- ✅ **Security** - Escaneo de seguridad
  - Bandit (security issues)

**Duración**: ~3-5 minutos

---

### **2. CI (`ci.yml`)** - Rápido

**Se ejecuta en**: Todos los push y PR

**Jobs**:
- ✅ **Quick Test** - Tests unitarios solamente
  - Solo Python 3.10
  - Tests rápidos (< 2 min)
  - Valida coverage mínimo 60%

**Duración**: ~1-2 minutos

---

## 📦 Dependencias del CI

El CI instala automáticamente:
- ✅ Todas las dependencias de `requirements.txt`
- ✅ `uv` para instalación rápida
- ✅ Herramientas de linting (ruff, mypy)
- ✅ Bandit para security scanning

---

## 🎯 Qué valida el CI

### **Tests**
```bash
✅ 105 tests unitarios e integración
✅ Coverage mínimo: 60% (actual: 67%)
✅ Múltiples versiones de Python (3.10, 3.11)
```

### **Code Quality**
```bash
✅ Ruff - Linting y formateo
✅ MyPy - Type checking
✅ Bandit - Security issues
```

### **Coverage**
```bash
✅ Reporte automático en cada PR
✅ Upload a Codecov (opcional)
✅ Artifacts disponibles por 30 días
```

---

## 🔧 Configuración Local vs CI

### **Local (desarrollo)**
```bash
python run_tests.py              # Todos los tests
python run_tests.py --unit       # Solo unitarios (rápido)
python run_tests.py --coverage   # Con coverage
```

### **CI (automático)**
```bash
# CI ejecuta automáticamente:
python run_tests.py --coverage   # En tests.yml
python run_tests.py --unit       # En ci.yml (rápido)
```

---

## 📈 Codecov Integration (Opcional)

### **1. Registrar en Codecov**

1. Ve a [codecov.io](https://codecov.io)
2. Login con GitHub
3. Añade el repositorio A.R.C.A-LLM
4. Copia el token

### **2. Añadir Token a GitHub Secrets**

1. Ve a tu repo → Settings → Secrets → Actions
2. Click "New repository secret"
3. Name: `CODECOV_TOKEN`
4. Value: [tu token de Codecov]
5. Save

### **3. Ver Reports**

- Dashboard: `https://codecov.io/gh/TU_USUARIO/A.R.C.A-LLM`
- Badge: Se actualiza automáticamente
- Reports en cada PR

---

## 🛡️ Branch Protection Rules (Recomendado)

### **Configurar en GitHub**

1. Ve a: **Settings → Branches → Add rule**
2. Branch name pattern: `main`
3. Activa:
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - Status checks required:
     - `Test / Run Tests (3.10)`
     - `Quick Tests (Python 3.10)`
   - ✅ Require pull request reviews before merging (opcional)

Esto asegura que:
- ❌ No se puede mergear sin tests passing
- ❌ No se puede push directamente a main
- ✅ Todo pasa por PR con validación

---

## 🚨 Troubleshooting CI

### **Tests fallan en CI pero pasan local**

```bash
# Causa común: Diferencias de entorno
# Solución: Ejecutar en un virtualenv limpio

python -m venv test-env
source test-env/bin/activate  # Linux/Mac
test-env\Scripts\activate     # Windows
pip install -r requirements.txt
python run_tests.py
```

### **Coverage muy bajo**

```bash
# Ver qué archivos tienen bajo coverage
python run_tests.py --coverage
coverage report --skip-covered

# Ver HTML detallado
python run_tests.py --html
# Abre: htmlcov/index.html
```

### **CI tarda mucho**

```bash
# El workflow ci.yml es más rápido:
# - Solo ejecuta tests unitarios
# - Solo Python 3.10
# - Sin linting

# Para PR rápidos, solo se ejecuta ci.yml
# Para merge a main, se ejecuta tests.yml completo
```

---

## 📝 Logs y Artifacts

### **Ver logs de CI**

1. Ve a: **Actions** tab en GitHub
2. Click en el workflow run
3. Click en el job que quieres ver
4. Expand steps para ver logs detallados

### **Descargar Coverage Reports**

1. Ve al workflow run
2. Scroll down a "Artifacts"
3. Download: `coverage-report`
4. Unzip y abre `index.html`

---

## 🔄 Workflow de Desarrollo

### **Feature Branch**
```bash
# 1. Crear feature branch
git checkout -b feature/nueva-funcionalidad

# 2. Hacer cambios y tests
python run_tests.py --unit  # Test local

# 3. Commit y push
git add .
git commit -m "feat: nueva funcionalidad"
git push origin feature/nueva-funcionalidad

# 4. CI se ejecuta automáticamente
# - ci.yml (quick tests) ✅
# - tests.yml (full suite) ✅

# 5. Crear PR
# GitHub muestra status de checks

# 6. Mergear cuando todos los checks pasan
```

### **Hotfix en Main**
```bash
# Para emergencias, puedes bypass con:
git push --no-verify origin main

# ⚠️ Solo usar en emergencias!
# El CI aún se ejecutará después del push
```

---

## 🎓 Best Practices

### **✅ DO**
- ✅ Ejecutar tests localmente antes de push
- ✅ Esperar a que CI pase antes de mergear
- ✅ Revisar coverage reports
- ✅ Mantener coverage > 60%
- ✅ Arreglar issues de linting

### **❌ DON'T**
- ❌ Bypass CI checks (excepto emergencias)
- ❌ Ignorar test failures
- ❌ Mergear con coverage bajando
- ❌ Commit código sin probar
- ❌ Deshabilitar workflows sin razón

---

## 📚 Recursos

### **GitHub Actions**
- [Documentación oficial](https://docs.github.com/en/actions)
- [Marketplace de actions](https://github.com/marketplace?type=actions)
- [Workflow syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)

### **Testing**
- [pytest docs](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Codecov](https://docs.codecov.com/)

### **Code Quality**
- [Ruff](https://github.com/astral-sh/ruff)
- [MyPy](https://mypy.readthedocs.io/)
- [Bandit](https://bandit.readthedocs.io/)

---

## 🔮 Futuras Mejoras

### **Fase 2 - CD (Continuous Deployment)**
- [ ] Deploy automático a staging
- [ ] Deploy a producción con tags
- [ ] Docker build y push a registry
- [ ] Semantic versioning automático

### **Fase 3 - Quality Gates**
- [ ] Mutation testing (mutmut)
- [ ] Performance benchmarks
- [ ] Dependency vulnerability scanning
- [ ] Automatic dependency updates (Dependabot)

### **Fase 4 - Monitoring**
- [ ] Health checks en producción
- [ ] Error tracking (Sentry)
- [ ] Performance monitoring
- [ ] Usage analytics

---

**Última actualización**: Noviembre 2025  
**Versión**: 1.0.0  
**Mantenido por**: A.R.C.A-LLM Team

