/**
 * Enhanced API client for communicating with the backend
 * Includes comprehensive error handling, retry logic, and request/response interceptors
 */
import axios, { AxiosInstance, AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';
import { supabase } from './supabaseClient';

// Backend API base URL
const API_BASE_URL =
    import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

// Request timeout configurations
const DEFAULT_TIMEOUT = 30000; // 30 seconds
const RETRY_ATTEMPTS = 3;
const RETRY_DELAY = 1000; // 1 second

// Integration types
export type Platform = 'github' | 'discord' | 'slack' | 'discourse';

export interface IntegrationConfig {
    // Platform-specific configuration
    [key: string]: string | number | boolean | null | undefined;
}

// Error response types
export interface APIErrorResponse {
    error: {
        code: string;
        message: string;
        correlation_id?: string;
        timestamp?: number;
        path?: string;
        context?: Record<string, unknown>;
        details?: Array<{
            field: string;
            message: string;
            type: string;
        }>;
    };
}

// Health check types
export interface HealthCheckResponse {
    status: 'healthy' | 'degraded' | 'unhealthy';
    timestamp: number;
    environment: string;
    version: string;
    response_time: number;
    services: Record<string, ServiceStatus>;
}

export interface ServiceStatus {
    name: string;
    status: 'healthy' | 'degraded' | 'unhealthy';
    response_time?: number;
    critical: boolean;
    error?: string;
    details?: Record<string, unknown>;
}

// Custom error class
export class APIError extends Error {
    public readonly code: string;
    public readonly correlationId?: string;
    public readonly context?: Record<string, unknown>;
    public readonly statusCode: number;

    constructor(
        message: string,
        code: string,
        statusCode: number,
        correlationId?: string,
        context?: Record<string, unknown>
    ) {
        super(message);
        this.name = 'APIError';
        this.code = code;
        this.statusCode = statusCode;
        this.correlationId = correlationId;
        this.context = context;
    }

    static fromResponse(error: AxiosError<APIErrorResponse>): APIError {
        const errorData = error.response?.data?.error;
        return new APIError(
            errorData?.message || error.message,
            errorData?.code || 'UNKNOWN_ERROR',
            error.response?.status || 500,
            errorData?.correlation_id,
            errorData?.context
        );
    }
}

// Retry configuration
interface RetryConfig {
    attempts: number;
    delay: number;
    backoff: number;
    retryCondition?: (error: AxiosError) => boolean;
}

export interface Integration {
    id: string;
    user_id: string;
    platform: Platform;
    organization_name: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
    config?: IntegrationConfig;
}

export interface IntegrationCreateRequest {
    platform: Platform;
    organization_name: string;
    organization_link?: string; // GitHub URL or Discord Server ID
    config?: IntegrationConfig;
}

export interface IntegrationUpdateRequest {
    organization_name?: string;
    organization_link?: string;
    is_active?: boolean;
    config?: IntegrationConfig;
}

export interface IntegrationStatus {
    platform: Platform;
    is_connected: boolean;
    organization_name?: string;
    last_updated?: string;
}

/**
 * Enhanced API Client class for backend communication
 * Includes retry logic, comprehensive error handling, and request/response logging
 */
class ApiClient {
    private client: AxiosInstance;
    private retryConfig: RetryConfig;

    constructor() {
        this.retryConfig = {
            attempts: RETRY_ATTEMPTS,
            delay: RETRY_DELAY,
            backoff: 1.5,
            retryCondition: (error: AxiosError) => {
                // Retry on network errors, timeouts, and 5xx status codes
                return (
                    !error.response ||
                    error.code === 'NETWORK_ERROR' ||
                    error.code === 'TIMEOUT' ||
                    (error.response.status >= 500 && error.response.status < 600)
                );
            }
        };

        this.client = axios.create({
            baseURL: API_BASE_URL,
            timeout: DEFAULT_TIMEOUT,
            headers: {
                'Content-Type': 'application/json',
            },
        });

        this.setupInterceptors();
    }

    private setupInterceptors(): void {
        // Request interceptor - add auth token and logging
        this.client.interceptors.request.use(
            async (config) => {
                // Add request ID for tracking
                const requestId = this.generateRequestId();
                config.headers['X-Request-ID'] = requestId;

                // Add auth token
                try {
                    const {
                        data: { session },
                    } = await supabase.auth.getSession();

                    if (session?.access_token) {
                        config.headers.Authorization = `Bearer ${session.access_token}`;
                    }
                } catch (error) {
                    console.warn('Failed to get auth session:', error);
                }

                // Log request in development
                if (import.meta.env.DEV) {
                    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {
                        requestId,
                        headers: config.headers,
                        data: config.data
                    });
                }

                return config;
            },
            (error) => {
                console.error('[API Request Error]', error);
                return Promise.reject(error);
            }
        );

        // Response interceptor - handle errors and logging
        this.client.interceptors.response.use(
            (response) => {
                // Log successful response in development
                if (import.meta.env.DEV) {
                    console.log(`[API Response] ${response.status} ${response.config.url}`, {
                        requestId: response.config.headers['X-Request-ID'],
                        correlationId: response.headers['x-correlation-id'],
                        processTime: response.headers['x-process-time'],
                        data: response.data
                    });
                }
                return response;
            },
            async (error: AxiosError<APIErrorResponse>) => {
                const correlationId = error.response?.headers['x-correlation-id'];
                
                // Log error details
                console.error('[API Error]', {
                    status: error.response?.status,
                    statusText: error.response?.statusText,
                    correlationId,
                    requestId: error.config?.headers?.['X-Request-ID'],
                    url: error.config?.url,
                    method: error.config?.method,
                    data: error.response?.data
                });

                // Handle specific error cases
                if (error.response?.status === 401) {
                    // Handle unauthorized - redirect to login or refresh token
                    await this.handleUnauthorized();
                } else if (error.response?.status === 403) {
                    // Handle forbidden
                    this.handleForbidden();
                } else if (error.response?.status >= 500) {
                    // Handle server errors
                    this.handleServerError(error);
                }

                // Convert to our custom error format
                const apiError = APIError.fromResponse(error);
                return Promise.reject(apiError);
            }
        );
    }

    private generateRequestId(): string {
        return `req_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
    }

    private async handleUnauthorized(): Promise<void> {
        console.warn('Unauthorized request - user may need to log in again');
        // Could dispatch a Redux action or event to trigger login flow
        // For now, just clear the session
        try {
            await supabase.auth.signOut();
        } catch (error) {
            console.error('Failed to sign out:', error);
        }
    }

    private handleForbidden(): void {
        console.warn('Forbidden request - user lacks necessary permissions');
        // Could show a user-friendly message about insufficient permissions
    }

    private handleServerError(error: AxiosError): void {
        console.error('Server error occurred:', error.response?.status, error.response?.statusText);
        // Could show a user-friendly message about server issues
    }

    private async retryRequest<T>(
        requestFn: () => Promise<AxiosResponse<T>>,
        attempt: number = 1
    ): Promise<AxiosResponse<T>> {
        try {
            return await requestFn();
        } catch (error) {
            const axiosError = error as AxiosError;
            
            if (
                attempt < this.retryConfig.attempts &&
                this.retryConfig.retryCondition?.(axiosError)
            ) {
                const delay = this.retryConfig.delay * Math.pow(this.retryConfig.backoff, attempt - 1);
                
                console.warn(`Request failed, retrying in ${delay}ms (attempt ${attempt}/${this.retryConfig.attempts})`);
                
                await new Promise(resolve => setTimeout(resolve, delay));
                return this.retryRequest(requestFn, attempt + 1);
            }
            
            throw error;
        }
    }

    /**
     * Create a new integration with retry logic
     */
    async createIntegration(
        data: IntegrationCreateRequest
    ): Promise<Integration> {
        const response = await this.retryRequest(() =>
            this.client.post<Integration>('/v1/integrations/', data)
        );
        return response.data;
    }

    /**
     * Get all integrations for the current user
     */
    async getIntegrations(): Promise<Integration[]> {
        const response = await this.retryRequest(() =>
            this.client.get<{
                integrations: Integration[];
                total: number;
            }>('/v1/integrations/')
        );
        return response.data.integrations;
    }

    /**
     * Get a specific integration by ID
     */
    async getIntegration(integrationId: string): Promise<Integration> {
        const response = await this.retryRequest(() =>
            this.client.get<Integration>(`/v1/integrations/${integrationId}`)
        );
        return response.data;
    }

    /**
     * Get integration status for a platform
     */
    async getIntegrationStatus(platform: Platform): Promise<IntegrationStatus> {
        const response = await this.retryRequest(() =>
            this.client.get<IntegrationStatus>(`/v1/integrations/status/${platform}`)
        );
        return response.data;
    }

    /**
     * Update an existing integration
     */
    async updateIntegration(
        integrationId: string,
        data: IntegrationUpdateRequest
    ): Promise<Integration> {
        const response = await this.retryRequest(() =>
            this.client.put<Integration>(`/v1/integrations/${integrationId}`, data)
        );
        return response.data;
    }

    /**
     * Delete an integration
     * Note: DELETE requests are not retried by default to avoid duplicate operations
     */
    async deleteIntegration(integrationId: string): Promise<void> {
        await this.client.delete(`/v1/integrations/${integrationId}`);
    }

    /**
     * Enhanced health check with detailed information
     */
    async healthCheck(): Promise<HealthCheckResponse> {
        const response = await this.retryRequest(() =>
            this.client.get<HealthCheckResponse>('/v1/health')
        );
        return response.data;
    }

    /**
     * Simple health check returning boolean
     */
    async isHealthy(): Promise<boolean> {
        try {
            const health = await this.healthCheck();
            return health.status === 'healthy' || health.status === 'degraded';
        } catch (error) {
            console.error('Backend health check failed:', error);
            return false;
        }
    }

    /**
     * Get detailed health information for debugging
     */
    async getDetailedHealth(): Promise<HealthCheckResponse | null> {
        try {
            const response = await this.client.get<HealthCheckResponse>('/v1/health/detailed');
            return response.data;
        } catch (error) {
            console.error('Detailed health check failed:', error);
            return null;
        }
    }

    /**
     * Check specific service health
     */
    async checkServiceHealth(service: string): Promise<ServiceStatus | null> {
        try {
            const response = await this.client.get<ServiceStatus>(`/v1/health/${service}`);
            return response.data;
        } catch (error) {
            console.error(`${service} health check failed:`, error);
            return null;
        }
    }

    /**
     * Generic GET request with retry logic
     */
    async get<T>(url: string): Promise<T> {
        const response = await this.retryRequest(() =>
            this.client.get<T>(url)
        );
        return response.data;
    }

    /**
     * Generic POST request with retry logic
     */
    async post<T>(url: string, data?: unknown): Promise<T> {
        const response = await this.retryRequest(() =>
            this.client.post<T>(url, data)
        );
        return response.data;
    }

    /**
     * Generic PUT request with retry logic
     */
    async put<T>(url: string, data?: unknown): Promise<T> {
        const response = await this.retryRequest(() =>
            this.client.put<T>(url, data)
        );
        return response.data;
    }

    /**
     * Generic DELETE request (no retry to avoid duplicate operations)
     */
    async delete(url: string): Promise<void> {
        await this.client.delete(url);
    }
}

// Export singleton instance
export const apiClient = new ApiClient();
