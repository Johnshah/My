/**
 * API Client for Universal AI App Generator
 * Handles all backend communication with axios
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

// API Base URL - defaults to localhost for development
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth tokens
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response) {
      // Server responded with error
      console.error('API Error:', error.response.status, error.response.data);
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// ============================================================================
// Generation API
// ============================================================================

export interface GenerateTextPromptRequest {
  prompt: string;
  app_type?: string;
  platform?: string[];
  source_repo?: string;
  source_project_id?: string;
  app_complexity?: 'basic' | 'standard' | 'advanced';
}

export interface GenerationResponse {
  task_id: string;
  project_id: number;
  status: string;
  estimated_time?: string;
  message: string;
}

export interface ProjectStatus {
  project_id: number;
  name: string;
  status: string;
  progress: number;
  current_phase?: string;
  error_message?: string;
  output_path?: string;
  download_url?: string;
  file_count?: number;
  line_count?: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

/**
 * Generate app from text prompt
 */
export const generateFromTextPrompt = async (
  data: GenerateTextPromptRequest
): Promise<GenerationResponse> => {
  const response = await apiClient.post('/api/v1/generate/text-prompt', data);
  return response.data;
};

/**
 * Generate app using Deep Mode
 */
export const generateDeepMode = async (
  data: GenerateTextPromptRequest
): Promise<GenerationResponse> => {
  const response = await apiClient.post('/api/v1/generate/deep-mode', data);
  return response.data;
};

/**
 * Generate app from GitHub repository
 */
export const generateFromGitHub = async (repoUrl: string): Promise<GenerationResponse> => {
  const response = await apiClient.post('/api/v1/generate/github', {
    repo_url: repoUrl,
  });
  return response.data;
};

/**
 * Generate app from uploaded files
 */
export const generateFromUpload = async (formData: FormData): Promise<GenerationResponse> => {
  const response = await apiClient.post('/api/v1/generate/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 300000, // 5 minutes for file upload
  });
  return response.data;
};

/**
 * Get project status
 */
export const getProjectStatus = async (projectId: number): Promise<ProjectStatus> => {
  const response = await apiClient.get(`/api/v1/projects/${projectId}`);
  return response.data;
};

/**
 * Get user's projects
 */
export const getUserProjects = async (
  limit = 50,
  offset = 0
): Promise<ProjectStatus[]> => {
  const response = await apiClient.get('/api/v1/projects', {
    params: { limit, offset },
  });
  return response.data;
};

/**
 * Download generated project
 */
export const downloadProject = async (projectId: number): Promise<Blob> => {
  const response = await apiClient.get(`/api/v1/projects/${projectId}/download`, {
    responseType: 'blob',
  });
  return response.data;
};

// ============================================================================
// Model API
// ============================================================================

export interface ModelInfo {
  id: number;
  name: string;
  display_name: string;
  description: string;
  model_type: string;
  backend: string;
  is_available: boolean;
  is_downloaded: boolean;
  download_progress: number;
  min_ram_gb?: number;
  disk_size_gb?: number;
  requires_gpu: boolean;
}

/**
 * Get available AI models
 */
export const getAvailableModels = async (modelType?: string): Promise<ModelInfo[]> => {
  const response = await apiClient.get('/api/v1/models', {
    params: { model_type: modelType },
  });
  return response.data;
};

/**
 * Download AI model
 */
export const downloadModel = async (modelName: string): Promise<void> => {
  await apiClient.post(`/api/v1/models/${modelName}/download`);
};

/**
 * Get model download status
 */
export const getModelStatus = async (modelName: string): Promise<ModelInfo> => {
  const response = await apiClient.get(`/api/v1/models/${modelName}/status`);
  return response.data;
};

// ============================================================================
// Voice API
// ============================================================================

/**
 * Convert speech to text
 */
export const speechToText = async (audioFile: File, language = 'en'): Promise<string> => {
  const formData = new FormData();
  formData.append('audio_file', audioFile);
  formData.append('language', language);
  
  const response = await apiClient.post('/api/v1/voice/speech-to-text', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data.text;
};

/**
 * Convert text to speech
 */
export const textToSpeech = async (
  text: string,
  voice = 'default',
  language = 'en'
): Promise<Blob> => {
  const response = await apiClient.post(
    '/api/v1/voice/text-to-speech',
    { text, voice, language },
    { responseType: 'blob' }
  );
  
  return response.data;
};

// ============================================================================
// GitHub API
// ============================================================================

/**
 * Analyze GitHub repository
 */
export const analyzeGitHubRepo = async (repoUrl: string): Promise<any> => {
  const response = await apiClient.post('/api/v1/github/analyze', {
    repo_url: repoUrl,
  });
  return response.data;
};

// ============================================================================
// API Keys API
// ============================================================================

export interface APIKeyInfo {
  id: number;
  service: string;
  key_name: string;
  masked_key: string;
  is_active: boolean;
  created_at: string;
}

/**
 * Add API key
 */
export const addAPIKey = async (
  service: string,
  keyName: string,
  apiKey: string
): Promise<APIKeyInfo> => {
  const response = await apiClient.post('/api/v1/api-keys', {
    service,
    key_name: keyName,
    api_key: apiKey,
  });
  return response.data;
};

/**
 * Get user's API keys
 */
export const getAPIKeys = async (service?: string): Promise<APIKeyInfo[]> => {
  const response = await apiClient.get('/api/v1/api-keys', {
    params: { service },
  });
  return response.data;
};

/**
 * Delete API key
 */
export const deleteAPIKey = async (keyId: number): Promise<void> => {
  await apiClient.delete(`/api/v1/api-keys/${keyId}`);
};

// ============================================================================
// System API
// ============================================================================

/**
 * Get system health status
 */
export const getSystemHealth = async (): Promise<any> => {
  const response = await apiClient.get('/health');
  return response.data;
};

/**
 * Get system info
 */
export const getSystemInfo = async (): Promise<any> => {
  const response = await apiClient.get('/api/v1/system/info');
  return response.data;
};

export default apiClient;
