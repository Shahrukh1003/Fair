import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fairnessApi } from '../api/client';
import type { MonitorParams } from '../types/fairness';

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

export const useAuditHistory = (lastN: number = 20) => {
  return useQuery({
    queryKey: ['audit-history', lastN],
    queryFn: () => fairnessApi.getAuditHistory(lastN),
    refetchInterval: false,
  });
};

export const useHealthCheck = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => fairnessApi.checkHealth(),
    refetchInterval: 30000,
  });
};
