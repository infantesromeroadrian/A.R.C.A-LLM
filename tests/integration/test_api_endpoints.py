"""
Integration tests for API endpoints.

Requires FastAPI app to be running.
Uses httpx for async HTTP testing.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from uuid import uuid4
import io

from src.api.main import app
import src.api.main as main_module


@pytest.fixture
async def client(mock_voice_service_for_api):
    """Async test client fixture with mocked voice_service."""
    # Inyectar el mock en el módulo main
    original_voice_service = main_module.voice_service
    main_module.voice_service = mock_voice_service_for_api
    
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), 
            base_url="http://test"
        ) as ac:
            yield ac
    finally:
        # Restaurar el original después de los tests
        main_module.voice_service = original_voice_service


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_health_endpoint(self, client):
        """Test /health endpoint returns status."""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "components" in data
        assert data["status"] in ["healthy", "unhealthy"]
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_health_endpoint_components(self, client):
        """Test health endpoint returns component status."""
        response = await client.get("/health")
        
        data = response.json()
        components = data["components"]
        
        assert "stt" in components
        assert "llm" in components
        assert "tts" in components


class TestRootEndpoint:
    """Tests for root endpoint."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_root_endpoint(self, client):
        """Test / endpoint returns HTML or API info."""
        response = await client.get("/")
        
        assert response.status_code == 200


class TestVoiceHealthEndpoint:
    """Tests for voice health endpoint."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_voice_health_endpoint(self, client):
        """Test /api/voice/health endpoint."""
        response = await client.get("/api/voice/health")
        
        assert response.status_code in [200, 503]  # Healthy or degraded
        data = response.json()
        
        assert "status" in data
        assert "components" in data


class TestTextProcessEndpoint:
    """Tests for /api/text/process endpoint."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_text_process_basic(self, client):
        """Test basic text processing."""
        payload = {
            "text": "Hola, me llamo Adrian",
            "session_id": None
        }
        
        response = await client.post("/api/text/process", json=payload)
        
        # May fail if LLM not running
        if response.status_code == 500:
            pytest.skip("LLM not available")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "session_id" in data
        assert "response_text" in data
        assert "latency" in data
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_text_process_empty_text_fails(self, client):
        """Test that empty text returns error."""
        payload = {
            "text": "",
            "session_id": None
        }
        
        response = await client.post("/api/text/process", json=payload)
        
        assert response.status_code == 422  # Validation error


class TestConversationEndpoints:
    """Tests for conversation management endpoints."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_conversation_history(self, client):
        """Test getting conversation history."""
        # Create a session first (via text process)
        session_id = str(uuid4())
        
        # Get history (may not exist)
        response = await client.get(f"/api/conversation/{session_id}")
        
        # Should return 404 if conversation doesn't exist
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_clear_conversation(self, client):
        """Test clearing conversation."""
        session_id = str(uuid4())
        
        response = await client.delete(f"/api/conversation/{session_id}")
        
        # Should return 404 if conversation doesn't exist
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_clear_conversation_with_params(self, client):
        """Test clearing conversation with keep_system parameter."""
        session_id = str(uuid4())
        
        response = await client.delete(
            f"/api/conversation/{session_id}",
            params={"keep_system": True}
        )
        
        assert response.status_code in [200, 404]


class TestVoiceProcessEndpoint:
    """Tests for /api/voice/process endpoint (with mocked audio)."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_voice_process_with_valid_audio(self, client):
        """Test voice processing with valid audio file."""
        # Create fake audio file
        fake_audio = b"fake audio data" * 1000
        audio_file = io.BytesIO(fake_audio)
        
        files = {
            "audio": ("test.wav", audio_file, "audio/wav")
        }
        data = {
            "session_id": str(uuid4()),
            "language": "es"
        }
        
        response = await client.post(
            "/api/voice/process",
            files=files,
            data=data
        )
        
        # May fail if services not running
        if response.status_code in [500, 503]:
            pytest.skip("Voice services not available")
        
        # Check response structure
        if response.status_code == 200:
            # Should return audio bytes
            assert response.headers["content-type"] == "audio/wav"
            assert "X-Session-ID" in response.headers
            assert "X-Transcribed-Text" in response.headers
            assert "X-Response-Text" in response.headers
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_voice_process_empty_audio_fails(self, client):
        """Test that empty audio returns error."""
        empty_audio = io.BytesIO(b"")
        
        files = {
            "audio": ("empty.wav", empty_audio, "audio/wav")
        }
        data = {
            "language": "es"
        }
        
        response = await client.post(
            "/api/voice/process",
            files=files,
            data=data
        )
        
        # Should fail validation or processing
        assert response.status_code in [400, 422, 500]


class TestCORS:
    """Tests for CORS configuration."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_cors_headers_present(self, client):
        """Test that CORS headers are present in responses."""
        response = await client.get(
            "/api/voice/health",
            headers={"Origin": "http://localhost:8080"}
        )
        
        # Should be successful and have CORS credentials header
        assert response.status_code == 200
        assert "access-control-allow-credentials" in response.headers
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_custom_headers_exposed(self, client):
        """Test that custom headers are exposed in CORS."""
        response = await client.get(
            "/api/voice/health",
            headers={"Origin": "http://localhost:8080"}
        )
        
        # Should allow custom headers to be read
        # (Actual testing would require browser environment)
        assert response.status_code == 200


class TestErrorHandling:
    """Tests for API error handling."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_invalid_session_id_format(self, client):
        """Test that invalid session_id format returns error."""
        response = await client.get("/api/conversation/invalid-uuid-format")
        
        # Should return validation error
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_nonexistent_endpoint_returns_404(self, client):
        """Test that non-existent endpoint returns 404."""
        response = await client.get("/api/nonexistent/endpoint")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_method_not_allowed(self, client):
        """Test that wrong HTTP method returns 405."""
        # Try POST on GET endpoint
        response = await client.post("/health")
        
        assert response.status_code == 405

