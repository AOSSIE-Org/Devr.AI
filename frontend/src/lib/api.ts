/**
 * API client for communicating with the backend
 */
import axios, { AxiosInstance } from 'axios';
import { supabase } from './supabaseClient';

// Backend API base URL
const API_BASE_URL =
    import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

// Integration types
export type Platform = 'github' | 'discord' | 'slack' | 'discourse';

export interface IntegrationConfig {
    // Platform-specific configuration
    [key: string]: any;
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
 * API Client class for backend communication
 */
class ApiClient {
    private client: AxiosInstance;

    constructor() {
        this.client = axios.create({
            baseURL: API_BASE_URL,
            headers: {
                'Content-Type': 'application/json',
            },
        });

        // Add request interceptor to add auth token
        this.client.interceptors.request.use(
            async (config) => {
                const {
                    data: { session },
                } = await supabase.auth.getSession();

                if (session?.access_token) {
                    config.headers.Authorization = `Bearer ${session.access_token}`;
                }

                return config;
            },
            (error) => {
                return Promise.reject(error);
            }
        );

        // Add response interceptor for error handling
        this.client.interceptors.response.use(
            (response) => response,
            async (error) => {
                if (error.response?.status === 401) {
                    // Clear session and redirect to login
                    // Avoid infinite redirect loop if already on login page
                    if (!window.location.pathname.includes('/login')) {
                        await supabase.auth.signOut();
                        const returnUrl = encodeURIComponent(window.location.pathname + window.location.search);
                        window.location.href = `/login?returnUrl=${returnUrl}`;
                    }
                }
                return Promise.reject(error);
            }
        );
    }

    /**
     * Create a new integration
     */
    async createIntegration(
        data: IntegrationCreateRequest
    ): Promise<Integration> {
        const response = await this.client.post<Integration>(
            '/v1/integrations/',
            data
        );
        return response.data;
    }

    /**
     * Get all integrations for the current user
     */
    async getIntegrations(): Promise<Integration[]> {
        const response = await this.client.get<{
            integrations: Integration[];
            total: number;
        }>('/v1/integrations/');
        return response.data.integrations;
    }

    /**
     * Get a specific integration by ID
     */
    async getIntegration(integrationId: string): Promise<Integration> {
        const response = await this.client.get<Integration>(
            `/v1/integrations/${integrationId}`
        );
        return response.data;
    }

    /**
     * Get integration status for a platform
     */
    async getIntegrationStatus(platform: Platform): Promise<IntegrationStatus> {
        const response = await this.client.get<IntegrationStatus>(
            `/v1/integrations/status/${platform}`
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
        const response = await this.client.put<Integration>(
            `/v1/integrations/${integrationId}`,
            data
        );
        return response.data;
    }

    /**
     * Delete an integration
     */
    async deleteIntegration(integrationId: string): Promise<void> {
        await this.client.delete(`/v1/integrations/${integrationId}`);
    }

    /**
     * Test connection to backend
     */
    async healthCheck(): Promise<boolean> {
        try {
            const response = await this.client.get('/v1/health');
            return response.status === 200;
        } catch (error) {
            // Log in development for debugging
            if (import.meta.env.DEV) {
                console.error('Health check failed:', error);
            }
            return false;
        }
    }
}

// Export singleton instance
export const apiClient = new ApiClient();
