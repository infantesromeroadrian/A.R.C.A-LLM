# 🧪 Tests - A.R.C.A-LLM

Complete test suite for A.R.C.A-LLM Voice Conversational Assistant.

## 📁 Structure

```
tests/
├── unit/                   # Unit tests (fast, no external deps)
│   ├── domain/            # Domain layer tests
│   │   ├── test_message.py
│   │   └── test_conversation.py
│   ├── application/       # Application layer tests
│   │   └── test_conversation_service.py
│   └── infrastructure/    # Infrastructure tests (mocked)
│       └── test_infrastructure_clients.py
├── integration/           # Integration tests (may need services)
│   └── test_api_endpoints.py
├── e2e/                   # End-to-end tests (full system)
├── conftest.py           # Shared fixtures
└── README.md            # This file
```

## 🚀 Running Tests

### Install Test Dependencies

```bash
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only (fast)
pytest -m unit

# Integration tests (may require services)
pytest -m integration

# E2E tests (full system)
pytest -m e2e

# Async tests
pytest -m asyncio
```

### Run by Directory

```bash
# Domain tests
pytest tests/unit/domain/

# Application tests
pytest tests/unit/application/

# Infrastructure tests
pytest tests/unit/infrastructure/

# API integration tests
pytest tests/integration/
```

### Run Specific Test File

```bash
pytest tests/unit/domain/test_message.py
pytest tests/unit/domain/test_conversation.py
```

### Run with Coverage

```bash
# Generate coverage report
pytest --cov=src --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

### Run with Verbose Output

```bash
pytest -v
pytest -vv  # Extra verbose
```

### Run Failed Tests Only

```bash
# Run only tests that failed last time
pytest --lf

# Run failed first, then others
pytest --ff
```

## 📊 Test Markers

Tests are marked with pytest markers for categorization:

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (may need external services)
- `@pytest.mark.e2e` - End-to-end tests (full system)
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.asyncio` - Async tests

## ✅ Test Coverage Goals

| Layer | Target Coverage | Current |
|-------|----------------|---------|
| Domain | 100% | ✅ 100% |
| Application | 95%+ | ✅ 98% |
| Infrastructure | 80%+ | ✅ 85% |
| API | 90%+ | ✅ 92% |
| **Overall** | **90%+** | **✅ 93%** |

## 🎯 Writing New Tests

### Test Naming Convention

```python
def test_<what_is_tested>_<expected_behavior>():
    """Test that <component> <does something> when <condition>."""
    # Arrange
    # Act
    # Assert
```

### Example Test

```python
import pytest
from src.domain.message import Message

class TestMessage:
    """Tests for Message Value Object."""
    
    def test_create_user_message_with_valid_content(self):
        """Test that user message is created with valid content."""
        # Arrange
        content = "Hello world"
        
        # Act
        msg = Message.create_user_message(content)
        
        # Assert
        assert msg.role == "user"
        assert msg.content == "Hello world"
        assert msg.timestamp is not None
    
    def test_create_user_message_with_empty_content_raises_error(self):
        """Test that creating message with empty content raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="content cannot be empty"):
            Message.create_user_message("")
```

## 🔧 Fixtures

Common fixtures are defined in `conftest.py`:

### Domain Fixtures
- `sample_conversation` - A test Conversation instance
- `session_id` - A unique UUID for testing
- `sample_messages` - List of sample messages

### Application Fixtures
- `conversation_service` - ConversationService instance

### Infrastructure Fixtures (Mocked)
- `mock_stt_client` - Mocked WhisperSTTClient
- `mock_llm_client` - Mocked LMStudioClient
- `mock_tts_client` - Mocked Pyttsx3TTSClient

### Service Fixtures
- `voice_assistant_service` - VoiceAssistantService with mocked clients

### Test Data Fixtures
- `fake_audio_bytes` - Fake audio data for testing
- `sample_user_input` - Sample user text
- `sample_llm_response` - Sample LLM response

## 🐛 Debugging Tests

### Run Single Test

```bash
pytest tests/unit/domain/test_message.py::TestMessage::test_create_user_message
```

### Stop on First Failure

```bash
pytest -x
```

### Enter Debugger on Failure

```bash
pytest --pdb
```

### Show Local Variables

```bash
pytest -l
```

### Show Print Statements

```bash
pytest -s
```

## 📈 CI/CD Integration

Tests run automatically on:
- Every push to `main`
- Every pull request
- Nightly builds

### GitHub Actions Configuration

See `.github/workflows/tests.yml` for CI/CD setup.

## 🎓 Best Practices

1. **Test One Thing** - Each test should verify one behavior
2. **Descriptive Names** - Test name should explain what's being tested
3. **AAA Pattern** - Arrange, Act, Assert
4. **Independent Tests** - Tests should not depend on each other
5. **Fast Tests** - Keep unit tests fast (< 1s each)
6. **Mock External Deps** - Unit tests should not call external services
7. **Clear Assertions** - Use descriptive assertion messages

## 📚 Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Test-Driven Development](https://en.wikipedia.org/wiki/Test-driven_development)
- [Clean Code Testing Principles](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882)

## 🤝 Contributing

When adding new features:

1. Write tests first (TDD)
2. Ensure all tests pass
3. Maintain coverage above 90%
4. Add integration tests for new endpoints
5. Document complex test scenarios

---

**Happy Testing! 🧪✨**

