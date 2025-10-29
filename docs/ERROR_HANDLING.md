# Error Handling Guide

This document provides comprehensive information about the error handling system implemented in Devr.AI, including error codes, response formats, and best practices for handling errors in both backend and frontend components.

## Overview

The Devr.AI application implements a robust error handling system with the following features:

- **Standardized Error Responses**: All API errors follow a consistent JSON format
- **Correlation IDs**: Every request gets a unique correlation ID for tracking
- **Comprehensive Logging**: All errors are logged with context and correlation IDs
- **Retry Logic**: Frontend automatically retries failed requests when appropriate
- **Health Monitoring**: Detailed health checks for all system components

## Error Response Format

All API errors return responses in the following standardized format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "correlation_id": "req_1698765432_abc123def",
    "timestamp": 1698765432.123,
    "path": "/v1/integrations/123",
    "context": {
      "field": "email",
      "resource_type": "Integration",
      "additional_info": "value"
    },
    "details": [
      {
        "field": "email",
        "message": "Invalid email format",
        "type": "value_error"
      }
    ]
  }
}
```

### Response Fields

- **code**: Standardized error code (see Error Codes section)
- **message**: Human-readable description of the error
- **correlation_id**: Unique identifier for request tracking
- **timestamp**: Unix timestamp when the error occurred
- **path**: API endpoint where the error occurred
- **context**: Additional context information specific to the error
- **details**: Array of detailed validation errors (for validation failures)

## Error Codes

### Client Errors (4xx)

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Request validation failed |
| `AUTHENTICATION_ERROR` | 401 | Authentication required or failed |
| `AUTHORIZATION_ERROR` | 403 | Insufficient permissions |
| `RESOURCE_NOT_FOUND` | 404 | Requested resource not found |
| `CONFLICT_ERROR` | 409 | Resource conflict (e.g., duplicate creation) |
| `RATE_LIMIT_ERROR` | 429 | Rate limit exceeded |

### Server Errors (5xx)

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INTERNAL_SERVER_ERROR` | 500 | Unexpected server error |
| `DATABASE_ERROR` | 500 | Database operation failed |
| `CONFIGURATION_ERROR` | 500 | Invalid or missing configuration |
| `EXTERNAL_SERVICE_ERROR` | 502 | External service unavailable |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

### Integration-Specific Errors

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INTEGRATION_NOT_FOUND` | 404 | Integration not found |
| `INTEGRATION_CONFIG_ERROR` | 400 | Invalid integration configuration |
| `GITHUB_API_ERROR` | 502 | GitHub API error |
| `DISCORD_API_ERROR` | 502 | Discord API error |
| `WEAVIATE_ERROR` | 502 | Weaviate database error |
| `SUPABASE_ERROR` | 502 | Supabase error |

## Backend Error Handling

### Custom Exception Classes

The backend uses custom exception classes that extend `BaseAPIException`:

```python
from app.core.exceptions import ValidationError, ResourceNotFoundError

# Validation error
raise ValidationError(
    "Invalid email format",
    field="email",
    context={"provided_value": user_input}
)

# Resource not found
raise ResourceNotFoundError(
    "Integration",
    resource_id="123",
    context={"user_id": "456"}
)
```

### Error Handling Middleware

The `ErrorHandlingMiddleware` automatically:

- Generates correlation IDs for all requests
- Logs request/response details
- Converts exceptions to standardized error responses
- Adds timing information to response headers

### Logging

All errors are logged with the following information:

```python
logger.error(
    f"Database error - {exc.error_code}: {exc.detail}, "
    f"Correlation-ID: {correlation_id}, "
    f"Context: {exc.context}"
)
```

Log files are stored in the `logs/` directory:

- `app.log`: General application logs
- `error.log`: Error-level logs only
- `access.log`: Request/response logs

## Frontend Error Handling

### APIError Class

The frontend uses a custom `APIError` class for structured error handling:

```typescript
try {
  const integration = await apiClient.getIntegration(id);
} catch (error) {
  if (error instanceof APIError) {
    console.error(`API Error: ${error.code} - ${error.message}`);
    console.error(`Correlation ID: ${error.correlationId}`);
    
    // Handle specific error types
    switch (error.code) {
      case 'RESOURCE_NOT_FOUND':
        showNotFoundMessage();
        break;
      case 'VALIDATION_ERROR':
        showValidationErrors(error.context);
        break;
      default:
        showGenericError();
    }
  }
}
```

### Retry Logic

The API client automatically retries failed requests with exponential backoff:

```typescript
const retryConfig = {
  attempts: 3,
  delay: 1000, // 1 second
  backoff: 1.5,
  retryCondition: (error) => {
    // Retry on network errors and 5xx status codes
    return !error.response || 
           error.response.status >= 500;
  }
};
```

### Request Tracking

All requests include unique request IDs for correlation:

```typescript
// Request headers
{
  "X-Request-ID": "req_1698765432_abc123def",
  "Authorization": "Bearer ...",
  "Content-Type": "application/json"
}

// Response headers
{
  "X-Correlation-ID": "req_1698765432_abc123def",
  "X-Process-Time": "0.1234"
}
```

## Health Monitoring

### Health Check Endpoints

| Endpoint | Description |
|----------|-------------|
| `/v1/health` | Overall system health |
| `/v1/health/weaviate` | Weaviate database health |
| `/v1/health/discord` | Discord bot health |
| `/v1/health/detailed` | Detailed diagnostics (dev only) |

### Health Response Format

```json
{
  "status": "healthy",
  "timestamp": 1698765432.123,
  "environment": "production",
  "version": "1.0",
  "response_time": 0.1234,
  "services": {
    "weaviate": {
      "name": "weaviate",
      "status": "healthy",
      "response_time": 0.0856,
      "critical": true
    },
    "discord_bot": {
      "name": "discord_bot",
      "status": "healthy",
      "critical": false
    }
  }
}
```

### Service Status Values

- **healthy**: Service is fully operational
- **degraded**: Service is operational but with reduced functionality
- **unhealthy**: Service is not operational

## Best Practices

### Backend Development

1. **Use Appropriate Exception Classes**:
   ```python
   # Good
   raise ValidationError("Invalid email", field="email")
   
   # Avoid
   raise HTTPException(status_code=400, detail="Bad request")
   ```

2. **Include Context Information**:
   ```python
   raise ResourceNotFoundError(
       "Integration",
       resource_id=integration_id,
       context={"user_id": user_id, "platform": platform}
   )
   ```

3. **Log with Correlation IDs**:
   ```python
   logger.info(f"Processing request - Correlation-ID: {correlation_id}")
   ```

4. **Use Performance Decorators**:
   ```python
   @log_performance("create_integration")
   async def create_integration(data):
       # Function implementation
   ```

### Frontend Development

1. **Handle Specific Error Types**:
   ```typescript
   try {
     await apiClient.createIntegration(data);
   } catch (error) {
     if (error instanceof APIError) {
       switch (error.code) {
         case 'VALIDATION_ERROR':
           handleValidationError(error);
           break;
         case 'RATE_LIMIT_ERROR':
           handleRateLimit(error);
           break;
         default:
           handleGenericError(error);
       }
     }
   }
   ```

2. **Provide User-Friendly Messages**:
   ```typescript
   const getErrorMessage = (error: APIError): string => {
     switch (error.code) {
       case 'NETWORK_ERROR':
         return 'Please check your internet connection and try again.';
       case 'SERVICE_UNAVAILABLE':
         return 'The service is temporarily unavailable. Please try again later.';
       default:
         return error.message;
     }
   };
   ```

3. **Use Health Checks**:
   ```typescript
   const checkBackendHealth = async (): Promise<boolean> => {
     try {
       const health = await apiClient.healthCheck();
       return health.status === 'healthy' || health.status === 'degraded';
     } catch {
       return false;
     }
   };
   ```

## Configuration

### Environment Variables

Error handling behavior can be configured through environment variables:

```bash
# Logging configuration
LOG_LEVEL=INFO
ENVIRONMENT=production

# Timeout settings
EXTERNAL_API_TIMEOUT=30
HEALTH_CHECK_TIMEOUT=5

# Rate limiting
RATE_LIMIT_PER_MINUTE=60
```

### Development vs Production

The error handling system adapts based on the environment:

**Development Mode**:
- Detailed error information in responses
- Debug logs enabled
- API documentation endpoints available
- Detailed health check endpoint accessible

**Production Mode**:
- Minimal error information exposed
- Error details logged but not returned to clients
- Enhanced security and performance optimizations
- Detailed diagnostics disabled

## Monitoring and Alerting

### Log Analysis

Use the correlation IDs to trace requests across the system:

```bash
# Find all logs for a specific request
grep "req_1698765432_abc123def" logs/*.log

# Find all errors in the last hour
grep "ERROR" logs/error.log | tail -n 100
```

### Metrics to Monitor

1. **Error Rates**: Track 4xx and 5xx response rates
2. **Response Times**: Monitor API response times
3. **Health Check Status**: Alert on service degradation
4. **External Service Errors**: Monitor third-party API failures

### Alerting Rules

Set up alerts for:

- Error rate > 5% over 5 minutes
- Response time > 2 seconds for 95th percentile
- Critical service health check failures
- Correlation ID gaps (indicating request tracking issues)

## Troubleshooting

### Common Issues

1. **Missing Correlation IDs**: Check that middleware is properly configured
2. **Inconsistent Error Format**: Ensure all endpoints use custom exception classes
3. **Retry Loops**: Verify retry conditions don't retry non-retryable errors
4. **Log Volume**: Adjust log levels in production to manage disk usage

### Debugging Steps

1. **Find the correlation ID** from the error response
2. **Search logs** for all entries with that correlation ID
3. **Trace the request flow** through the system
4. **Check service health** endpoints for component status
5. **Review error context** for additional debugging information

## Updates and Maintenance

This error handling system should be regularly reviewed and updated:

1. **Add new error codes** as new features are developed
2. **Update documentation** when error handling patterns change
3. **Review and analyze** error patterns from production logs
4. **Test error scenarios** as part of the development process