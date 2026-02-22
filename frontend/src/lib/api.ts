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
    organization_link?: string;
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

        /**
         * REQUEST INTERCEPTOR
         * Adds Supabase access token to every request
         */
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
            (error) => Promise.reject(error)
        );

        /**
         * RESPONSE INTERCEPTOR
         * Handles global API errors
         */
        this.client.interceptors.response.use(
            (response) => response,
            async (error) => {
                const status = error.response?.status;
                const currentPath = window.location.pathname;

                if (status === 401 && !currentPath.includes('/login')) {
                    console.warn('🔒 Session expired. Logging out...');

                    try {
                        await supabase.auth.signOut();
                    } catch (signOutError) {
                        console.error('Error during signOut:', signOutError);
                    }

                    // Optional: Clear any remaining storage
                    localStorage.clear();
                    sessionStorage.clear();

                    // Redirect to login page
                    window.location.href = '/login';
                }

                return Promise.reject(error);
            }
        );
    }

    async createIntegration(
        data: IntegrationCreateRequest
    ): Promise<Integration> {
        const response = await this.client.post<Integration>(
            '/v1/integrations/',
            data
        );
        return response.data;
    }

    async getIntegrations(): Promise<Integration[]> {
        const response = await this.client.get<{
            integrations: Integration[];
            total: number;
        }>('/v1/integrations/');
        return response.data.integrations;
    }

    async getIntegration(integrationId: string): Promise<Integration> {
        const response = await this.client.get<Integration>(
            `/v1/integrations/${integrationId}`
        );
        return response.data;
    }

    async getIntegrationStatus(platform: Platform): Promise<IntegrationStatus> {
        const response = await this.client.get<IntegrationStatus>(
            `/v1/integrations/status/${platform}`
        );
        return response.data;
    }

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

    async deleteIntegration(integrationId: string): Promise<void> {
        await this.client.delete(`/v1/integrations/${integrationId}`);
    }

    async healthCheck(): Promise<boolean> {
        try {
            const response = await this.client.get('/v1/health');
            return response.status === 200;
        } catch (error) {
            console.error('Backend health check failed:', error);
            return false;
        }
    }
}

export const apiClient = new ApiClient();