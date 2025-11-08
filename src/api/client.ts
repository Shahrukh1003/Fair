import axios from 'axios';
import type { FairnessCheckResponse, HealthStatus, AuditLogEntry, MonitorParams } from '../types/fairness';

const getApiBaseUrl = () => {
  if (typeof window !== 'undefined') {
    const { protocol, hostname } = window.location;
    return `${protocol}//${hostname}:8000/api`;
  }
  return 'http://localhost:8000/api';
};

const apiClient = axios.create({
  baseURL: getApiBaseUrl(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fairnessApi = {
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
};

export default apiClient;
