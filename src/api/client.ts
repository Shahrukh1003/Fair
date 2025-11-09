import axios from 'axios';
import type { 
  FairnessCheckResponse, 
  HealthStatus, 
  AuditLogEntry, 
  MonitorParams,
  LoginRequest,
  LoginResponse,
  FairnessTrendResponse,
  PreAlertResponse,
  DriftPrediction,
  BlockchainAnchor
} from '../types/fairness';

const getApiBaseUrl = () => {
  if (typeof window !== 'undefined') {
    const { protocol, hostname } = window.location;
    return `${protocol}//${hostname}:8000/api`;
  }
  return 'http://localhost:8000/api';
};

export const TOKEN_KEY = 'fairlens_access_token';
export const REFRESH_TOKEN_KEY = 'fairlens_refresh_token';
export const USER_KEY = 'fairlens_user';

export const authUtils = {
  getToken: (): string | null => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(TOKEN_KEY);
    }
    return null;
  },

  setToken: (token: string): void => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(TOKEN_KEY, token);
    }
  },

  getUser: (): any | null => {
    if (typeof window !== 'undefined') {
      const userStr = localStorage.getItem(USER_KEY);
      if (!userStr) return null;
      try {
        return JSON.parse(userStr);
      } catch {
        return null;
      }
    }
    return null;
  },

  setUser: (user: any): void => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    }
  },

  clearAuth: (): void => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(REFRESH_TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
    }
  },

  isAuthenticated: (): boolean => {
    return !!authUtils.getToken();
  },
};

const apiClient = axios.create({
  baseURL: getApiBaseUrl(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = authUtils.getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      authUtils.clearAuth();
      if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const fairnessApi = {
  login: async (request: LoginRequest): Promise<LoginResponse> => {
    const response = await apiClient.post<LoginResponse>('/login', request);
    return response.data;
  },

  checkHealth: async (): Promise<HealthStatus> => {
    const response = await apiClient.get<HealthStatus>('/health');
    return response.data;
  },

  monitorFairness: async (params: MonitorParams): Promise<FairnessCheckResponse> => {
    const response = await apiClient.get<FairnessCheckResponse>('/monitor_fairness', {
      params: {
        n_samples: params.n_samples,
        drift_level: params.drift_level,
      },
    });
    return response.data;
  },

  getAuditHistory: async (lastN: number = 20): Promise<AuditLogEntry[]> => {
    const response = await apiClient.get<{ entries: AuditLogEntry[]; count: number }>('/audit_history', {
      params: { last_n: lastN },
    });
    return response.data.entries;
  },

  getFairnessTrend: async (): Promise<FairnessTrendResponse> => {
    const response = await apiClient.get<FairnessTrendResponse>('/fairness_trend');
    return response.data;
  },

  getPreAlert: async (): Promise<PreAlertResponse> => {
    const response = await apiClient.get<PreAlertResponse>('/pre_alert');
    return response.data;
  },

  predictDrift: async (): Promise<DriftPrediction> => {
    const response = await apiClient.get<DriftPrediction>('/predict_fairness_drift');
    return response.data;
  },

  getBlockchainAnchor: async (hash: string): Promise<BlockchainAnchor> => {
    const response = await apiClient.get<BlockchainAnchor>(`/get_anchor/${hash}`);
    return response.data;
  },
};

export default apiClient;
