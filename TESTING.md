# 🧪 A.R.C.A-LLM Testing Guide

Guía completa de testing para A.R.C.A-LLM Voice Assistant.

---

## 📊 Estado Actual

| Categoría | Tests | Status | Coverage |
|-----------|-------|--------|----------|
| **Domain (Message)** | 13 | ✅ 100% | 100% |
| **Domain (Conversation)** | 27 | ✅ 100% | 97% |
| **Application (ConversationService)** | 22 | ✅ 100% | 98% |
| **Integration (API)** | 14 | ✅ 100% | 84% (routes) |
| **TOTAL** | **76** | **✅ 100%** | **Overall: 47%** |

**Notas**:
- 2 tests de integración se skip correctamente (requieren servicios reales)
- Infrastructure layer (STT/LLM/TTS) está mockeado en tests
- E2E tests pendientes (planeados para futuro)

---

## 🚀 Ejecución Rápida

### Ejecutar todos los tests
```bash
python run_tests.py
```

### Tests por categoría
```bash
python run_tests.py --unit          # Solo tests unitarios (rápido)
python run_tests.py --integration   # Solo tests de integración
python run_tests.py --domain        # Solo tests del dominio
python run_tests.py --application   # Solo tests de aplicación
```

### Con cobertura
```bash
python run_tests.py --coverage      # Reporte en terminal
python run_tests.py --html          # Genera HTML en htmlcov/
```

### Modo desarrollo
```bash
python run_tests.py --failed        # Solo tests que fallaron
python run_tests.py --watch         # Auto-reload (requiere pytest-watch)
```

---

## 📁 Estructura de Tests

```
tests/
├── conftest.py                  # Fixtures compartidos
├── pytest.ini                   # Configuración de pytest
├── README.md                    # Documentación detallada
│
├── unit/                        # Tests unitarios (sin I/O)
│   ├── domain/                 # Value Objects y Aggregates
│   │   ├── test_message.py    # ✅ 13 tests (100% coverage)
│   │   └── test_conversation.py  # ✅ 27 tests (97% coverage)
│   │
│   ├── application/            # Servicios de aplicación
│   │   └── test_conversation_service.py  # ✅ 22 tests (98% coverage)
│   │
│   └── infrastructure/         # Clientes (mockeados)
│       └── (pendiente)
│
├── integration/                # Tests de API con mocks
│   └── test_api_endpoints.py  # ✅ 14 tests (84% coverage)
│
└── e2e/                        # End-to-end (futuro)
    └── (pendiente)
```

---

## 🎯 Estrategia de Testing

### 1. **Tests Unitarios** (`tests/unit/`)

**Objetivo**: Probar lógica de negocio aislada.

**Características**:
- ✅ Rápidos (< 1 segundo por test)
- ✅ Sin I/O (sin red, sin disco, sin DB)
- ✅ Determin

ísticos (mismos inputs = mismos outputs)
- ✅ Fáciles de depurar

**Qué probamos**:
- **Domain Layer**: Value Objects, Entities, Aggregates
  - Inmutabilidad
  - Validaciones
  - Lógica de negocio
  - Igualdad por valor
  
- **Application Layer**: Servicios de aplicación
  - Orquestación de domain objects
  - Casos de uso
  - Coordinación (sin lógica de negocio)

**Ejemplo**:
```python
def test_message_immutability():
    """Test that Message is immutable (frozen)."""
    msg = Message.create_user_message("Test")
    
    with pytest.raises(FrozenInstanceError):
        msg.content = "Modified"  # ❌ Debe fallar
```

---

### 2. **Tests de Integración** (`tests/integration/`)

**Objetivo**: Probar integración entre capas.

**Características**:
- ✅ Lentos (10-20 segundos)
- ✅ Con I/O mockeado (httpx AsyncClient)
- ✅ Prueban contratos entre capas

**Qué probamos**:
- Endpoints de API
- Validación de requests
- Serialización/deserialización
- CORS y headers
- Error handling

**Ejemplo**:
```python
async def test_health_endpoint(client):
    """Test /health endpoint returns status."""
    response = await client.get("/health")
    
    assert response.status_code == 200
    assert "status" in response.json()
```

---

### 3. **Tests E2E** (`tests/e2e/`) - Futuro

**Objetivo**: Probar flujos completos con servicios reales.

**Características**:
- ⚠️ Muy lentos (minutos)
- ⚠️ Requieren servicios externos (LM Studio, Whisper)
- ⚠️ Frágiles (dependen de red/servicios)

**Qué probaremos**:
- Conversación completa STT → LLM → TTS
- Manejo de sesiones
- Performance real

---

## 🧩 Fixtures Disponibles

Ver `tests/conftest.py` para fixtures compartidos:

### Domain Fixtures
- `sample_conversation()` - Conversación de prueba
- `session_id()` - UUID único
- `sample_messages()` - Lista de mensajes de ejemplo

### Application Fixtures
- `conversation_service()` - ConversationService real
- `voice_assistant_service()` - VoiceAssistantService mockeado

### Infrastructure Fixtures (Mocked)
- `mock_stt_client()` - WhisperSTTClient mockeado
- `mock_llm_client()` - LMStudioClient mockeado
- `mock_tts_client()` - Pyttsx3TTSClient mockeado

### Integration Fixtures
- `client()` - AsyncClient para tests de API
- `mock_voice_service_for_api()` - Voice service para API tests

---

## 📈 Coverage Reports

### Ver cobertura en terminal
```bash
python run_tests.py --coverage
```

### Generar HTML report
```bash
python run_tests.py --html
# Abre htmlcov/index.html en tu navegador
```

### Ver cobertura de un módulo específico
```bash
pytest tests/unit/domain/ --cov=src/domain --cov-report=term-missing
```

---

## 🔧 Configuración

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    unit: Unit tests (fast, no I/O)
    integration: Integration tests (with mocked I/O)
    e2e: End-to-end tests (with real services)
    slow: Slow tests (> 5 seconds)

asyncio_mode = auto
asyncio_default_fixture_loop_scope = function

timeout = 300

# Coverage
addopts = 
    --strict-markers
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    -ra
```

---

## 🐛 Debugging Tests

### Ejecutar un test específico
```bash
pytest tests/unit/domain/test_message.py::TestMessage::test_create_user_message -v
```

### Ver stdout/stderr
```bash
pytest tests/unit/domain/ -v -s
```

### Entrar en debugger cuando falla
```bash
pytest tests/unit/domain/ --pdb
```

### Ver logs
```bash
pytest tests/unit/domain/ -v --log-cli-level=DEBUG
```

---

## 📝 Escribir Nuevos Tests

### Template para Test Unitario

```python
"""
Tests para [NombreDelMódulo].

Tests:
- [Descripción del test]
- [Descripción del test]
"""

import pytest
from src.domain.message import Message


class TestMessage:
    """Tests for Message Value Object."""
    
    def test_create_user_message(self):
        """Test that factory creates valid user message."""
        msg = Message.create_user_message("Hello")
        
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.timestamp is not None
```

### Template para Test de Integración

```python
"""
Integration tests para [NombreDelEndpoint].

Tests:
- [Descripción del test]
"""

import pytest
from httpx import AsyncClient


class TestMyEndpoint:
    """Tests for /my/endpoint."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_my_endpoint(self, client):
        """Test endpoint returns expected response."""
        response = await client.get("/my/endpoint")
        
        assert response.status_code == 200
        assert "data" in response.json()
```

---

## 🚨 CI/CD Integration (Futuro)

### GitHub Actions (ejemplo)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python run_tests.py --coverage
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

---

## 🎓 Best Practices

### ✅ DO

- ✅ Escribir tests antes de refactorizar
- ✅ Un assert por test (cuando sea posible)
- ✅ Nombres descriptivos: `test_message_validates_empty_content()`
- ✅ Usar fixtures para setup repetitivo
- ✅ Tests independientes (no dependen entre sí)
- ✅ Mockear I/O en tests unitarios
- ✅ Probar edge cases y errores

### ❌ DON'T

- ❌ Tests lentos en unit tests
- ❌ Tests que dependen de orden de ejecución
- ❌ Tests que modifican estado global
- ❌ Múltiples asserts no relacionados
- ❌ Tests que dependen de servicios externos (usar mocks)
- ❌ Tests sin asserts (smoke tests)
- ❌ Copy-paste de código de test

---

## 📚 Recursos

### Documentación
- [pytest](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [httpx](https://www.python-httpx.org/async/)

### Testing Philosophy
- [Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Testing Best Practices](https://testdriven.io/blog/testing-best-practices/)
- [DDD Testing](https://www.domainlanguage.com/ddd/)

---

## 🤝 Contribuir

Al agregar features nuevas:

1. ✅ Escribir tests primero (TDD)
2. ✅ Asegurar > 80% coverage
3. ✅ Ejecutar `python run_tests.py --coverage`
4. ✅ Verificar que todos los tests pasen
5. ✅ Commit con tests incluidos

---

## 📞 Soporte

¿Problemas con los tests?

1. Revisar logs: `pytest -v --log-cli-level=DEBUG`
2. Revisar fixtures en `tests/conftest.py`
3. Revisar documentación en `tests/README.md`
4. Ejecutar tests en modo verbose: `pytest -vv`

---

**Última actualización**: Noviembre 2025  
**Versión**: 1.0.0  
**Mantenido por**: A.R.C.A-LLM Team

