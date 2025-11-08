import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fairnessApi } from '../api/client';
import type { MonitorParams, LoginRequest } from '../types/fairness';

export const useFairnessMonitor = (params: MonitorParams, enabled: boolean = false) => {
  return useQuery({
    queryKey: ['fairness-monitor', params],
    queryFn: () => fairnessApi.monitorFairness(params),
    enabled,
    refetchOnWindowFocus: false,
  });
};

export const useMonitorMutation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (params: MonitorParams) => fairnessApi.monitorFairness(params),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['audit-history'] });
    },
  });
};

export const useAuditHistory = (lastN: number = 20, enabled: boolean = true) => {
  return useQuery({
    queryKey: ['audit-history', lastN],
    queryFn: () => fairnessApi.getAuditHistory(lastN),
    refetchInterval: false,
    enabled,
  });
};

export const useHealthCheck = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => fairnessApi.checkHealth(),
    refetchInterval: 30000,
  });
};

export const useLoginMutation = () => {
  return useMutation({
    mutationFn: (request: LoginRequest) => fairnessApi.login(request),
  });
};

export const useFairnessTrend = () => {
  return useQuery({
    queryKey: ['fairnessTrend'],
    queryFn: fairnessApi.getFairnessTrend,
    refetchInterval: 30000,
  });
};

export const usePreAlert = () => {
  return useQuery({
    queryKey: ['preAlert'],
    queryFn: fairnessApi.getPreAlert,
    refetchInterval: 30000,
  });
};

export const useDriftPrediction = () => {
  return useQuery({
    queryKey: ['driftPrediction'],
    queryFn: fairnessApi.predictDrift,
    refetchInterval: 30000,
  });
};
