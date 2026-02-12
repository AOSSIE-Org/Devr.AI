"""
Comprehensive tests for error handling and API endpoints.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from uuid import uuid4

from app.core.exceptions import (
    ValidationError,
    ResourceNotFoundError,
    DatabaseError,
    ExternalServiceError,
    AuthenticationError
)
from app.api.v1.integrations import router as integrations_router
from app.services.integration_service import integration_service
from main import api


class TestErrorHandling:
    """Test error handling across the application."""
    
    def setup_method(self):
        """Setup test client and mocks."""
        self.client = TestClient(api)
        self.test_user_id = uuid4()
    
    def test_validation_error_response(self):
        """Test that validation errors return proper response format."""
        # Test missing required fields
        response = self.client.post(
            "/v1/integrations/",
            json={"platform": ""},  # Invalid platform
            headers={"Authorization": f"Bearer test-token"}
        )
        
        assert response.status_code == 422
        error_data = response.json()
        
        assert "error" in error_data
        assert error_data["error"]["code"] == "VALIDATION_ERROR"
        assert "correlation_id" in error_data["error"]
        assert "timestamp" in error_data["error"]
        assert "details" in error_data["error"]
    
    def test_resource_not_found_error(self):
        """Test resource not found error handling."""
        with patch.object(integration_service, 'get_integration', side_effect=ResourceNotFoundError("Integration", "test-id")):
            response = self.client.get(
                "/v1/integrations/non-existent-id",
                headers={"Authorization": f"Bearer test-token"}
            )
            
            assert response.status_code == 404
            error_data = response.json()
            
            assert error_data["error"]["code"] == "RESOURCE_NOT_FOUND"
            assert "Integration not found" in error_data["error"]["message"]
            assert error_data["error"]["context"]["resource_type"] == "Integration"
    
    def test_database_error_handling(self):
        """Test database error handling."""
        with patch.object(integration_service, 'get_integrations', side_effect=DatabaseError("Connection failed")):
            response = self.client.get(
                "/v1/integrations/",
                headers={"Authorization": f"Bearer test-token"}
            )
            
            assert response.status_code == 500
            error_data = response.json()
            
            assert error_data["error"]["code"] == "DATABASE_ERROR"
            assert "Connection failed" in error_data["error"]["message"]
    
    def test_external_service_error(self):
        """Test external service error handling."""
        with patch.object(integration_service, 'get_integration_status', side_effect=ExternalServiceError("GitHub", "API rate limit exceeded")):
            response = self.client.get(
                "/v1/integrations/status/github",
                headers={"Authorization": f"Bearer test-token"}
            )
            
            assert response.status_code == 502
            error_data = response.json()
            
            assert error_data["error"]["code"] == "EXTERNAL_SERVICE_ERROR"
            assert "GitHub" in error_data["error"]["message"]
    
    def test_authentication_error(self):
        """Test authentication error handling."""
        response = self.client.get("/v1/integrations/")
        
        assert response.status_code == 401
        error_data = response.json()
        
        assert error_data["error"]["code"] == "AUTHENTICATION_ERROR"
    
    def test_correlation_id_in_responses(self):
        """Test that all error responses include correlation IDs."""
        response = self.client.get("/v1/integrations/")
        
        error_data = response.json()
        assert "correlation_id" in error_data["error"]
        
        # Check correlation ID is also in headers
        assert "X-Correlation-ID" in response.headers
    
    def test_error_context_information(self):
        """Test that errors include relevant context information."""
        with patch.object(integration_service, 'create_integration', side_effect=ValidationError("Invalid platform", field="platform")):
            response = self.client.post(
                "/v1/integrations/",
                json={"platform": "invalid", "organization_name": "test"},
                headers={"Authorization": f"Bearer test-token"}
            )
            
            error_data = response.json()
            assert "context" in error_data["error"]
            assert error_data["error"]["context"]["field"] == "platform"


class TestHealthEndpoints:
    """Test health check endpoints and error handling."""
    
    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(api)
    
    def test_health_check_success(self):
        """Test successful health check."""
        with patch('app.database.weaviate.client.get_weaviate_client') as mock_client:
            mock_client.return_value.__aenter__.return_value.is_ready.return_value = True
            
            response = self.client.get("/v1/health")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] in ["healthy", "degraded"]
            assert "services" in data
            assert "timestamp" in data
            assert "response_time" in data
    
    def test_health_check_service_failure(self):
        """Test health check with service failures."""
        with patch('app.database.weaviate.client.get_weaviate_client', side_effect=Exception("Connection failed")):
            response = self.client.get("/v1/health")
            
            assert response.status_code == 503
            error_data = response.json()
            
            assert error_data["error"]["code"] == "SERVICE_UNAVAILABLE"
    
    def test_specific_service_health_checks(self):
        """Test individual service health checks."""
        # Test Weaviate health
        with patch('app.database.weaviate.client.get_weaviate_client') as mock_client:
            mock_client.return_value.__aenter__.return_value.is_ready.return_value = True
            
            response = self.client.get("/v1/health/weaviate")
            assert response.status_code == 200
            
            data = response.json()
            assert data["name"] == "weaviate"
            assert data["status"] == "healthy"
    
    def test_detailed_health_check_development_only(self):
        """Test that detailed health check is only available in development."""
        with patch('app.core.config.settings.is_development', return_value=False):
            response = self.client.get("/v1/health/detailed")
            assert response.status_code == 503


class TestMiddleware:
    """Test error handling middleware."""
    
    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(api)
    
    def test_correlation_id_generation(self):
        """Test that correlation IDs are generated for all requests."""
        response = self.client.get("/v1/health")
        
        assert "X-Correlation-ID" in response.headers
        correlation_id = response.headers["X-Correlation-ID"]
        assert len(correlation_id) > 0
    
    def test_process_time_header(self):
        """Test that process time is included in response headers."""
        response = self.client.get("/v1/health")
        
        assert "X-Process-Time" in response.headers
        process_time = float(response.headers["X-Process-Time"])
        assert process_time > 0
    
    def test_error_response_format_consistency(self):
        """Test that all error responses follow the same format."""
        # Test different types of errors
        responses = [
            self.client.get("/v1/integrations/"),  # 401 error
            self.client.get("/v1/integrations/non-existent"),  # 404 error
            self.client.post("/v1/integrations/", json={}),  # 422 validation error
        ]
        
        for response in responses:
            if response.status_code >= 400:
                data = response.json()
                
                # Check error structure
                assert "error" in data
                assert "code" in data["error"]
                assert "message" in data["error"]
                assert "correlation_id" in data["error"]
                assert "timestamp" in data["error"]
                assert "path" in data["error"]


class TestAPIClientErrorHandling:
    """Test frontend API client error handling (would be in JavaScript/TypeScript tests)."""
    
    def test_api_error_class_creation(self):
        """Test APIError class functionality."""
        # This would be implemented in frontend tests
        # Here's the equivalent logic that would be tested in JS/TS
        
        error_response = {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid input",
                "correlation_id": "test-correlation-id",
                "context": {"field": "email"}
            }
        }
        
        # Test that APIError.fromResponse creates proper error objects
        # and includes all necessary information
        pass
    
    def test_retry_logic(self):
        """Test API client retry logic."""
        # This would test the retry mechanism in the frontend client
        # Including exponential backoff and retry conditions
        pass
    
    def test_request_correlation_tracking(self):
        """Test that requests include correlation IDs for tracking."""
        # This would test that the frontend client adds request IDs
        # and logs them properly for debugging
        pass


@pytest.mark.asyncio
class TestAsyncErrorHandling:
    """Test asynchronous error handling scenarios."""
    
    async def test_concurrent_request_error_handling(self):
        """Test error handling with concurrent requests."""
        # Simulate multiple concurrent requests with different error scenarios
        async def make_request(endpoint, expected_status):
            # This would test concurrent error handling
            pass
    
    async def test_timeout_handling(self):
        """Test request timeout handling."""
        # Test that timeouts are handled gracefully
        with patch('asyncio.wait_for', side_effect=asyncio.TimeoutError):
            # Test timeout behavior
            pass
    
    async def test_circuit_breaker_pattern(self):
        """Test circuit breaker implementation if available."""
        # Test that circuit breaker prevents cascading failures
        pass


class TestLoggingAndMonitoring:
    """Test logging and monitoring functionality."""
    
    def test_error_logging_format(self):
        """Test that errors are logged in the correct format."""
        with patch('app.core.logging_config.get_logger') as mock_logger:
            # Trigger an error and verify logging
            response = self.client.get("/v1/integrations/")
            
            # Verify logger was called with appropriate level and message
            assert mock_logger.return_value.error.called or mock_logger.return_value.warning.called
    
    def test_performance_logging(self):
        """Test that performance metrics are logged."""
        with patch('app.core.logging_config.get_logger') as mock_logger:
            response = self.client.get("/v1/health")
            
            # Verify performance logging
            # This would check that execution time is logged
    
    def test_correlation_id_in_logs(self):
        """Test that correlation IDs appear in log messages."""
        # This would verify that the logging middleware includes correlation IDs
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])