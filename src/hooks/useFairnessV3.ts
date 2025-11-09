import { useQuery, useMutation } from '@tanstack/react-query';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface FairnessSummaryResponse {
  n_samples: number;
  drift_level: number;
  timestamp: string;
  metrics: {
    all_metrics: {
      DIR: {
        name: string;
        value: number;
        is_fair: boolean;
        status: string;
        threshold: number;
        privileged_rate: number;
        protected_rate: number;
        gap: number;
      };
      SPD: {
        name: string;
        value: number;
        is_fair: boolean;
        status: string;
        threshold: number;
        privileged_rate: number;
        protected_rate: number;
        absolute_difference: number;
      };
      EOD: {
        name: string;
        value: number;
        is_fair: boolean;
        status: string;
        threshold: number;
        privileged_tpr: number;
        protected_tpr: number;
        absolute_difference: number;
      };
      AOD: {
        name: string;
        value: number;
        is_fair: boolean;
        status: string;
        threshold: number;
        privileged_tpr: number;
        protected_tpr: number;
        privileged_fpr: number;
        protected_fpr: number;
        tpr_difference: number;
        fpr_difference: number;
      };
      THEIL: {
        name: string;
        value: number;
        is_fair: boolean;
        status: string;
        threshold: number;
        privileged_rate: number;
        protected_rate: number;
        overall_rate: number;
        inequality_level: string;
      };
    };
    summary: {
      overall_status: string;
      fairness_score: number;
      passed: number;
      failed: number;
      total_metrics: number;
      compliance_level: string;
    };
  };
}

export interface ExplainabilityResponse {
  timestamp: string;
  feature_contributions: Array<{
    feature: string;
    importance_score: number;
    contribution_to_bias: string;
    confidence: number;
  }>;
  remediation_suggestions: Array<{
    priority: string;
    action: string;
    expected_impact: string;
    confidence: number;
  }>;
  summary: {
    top_contributor: string;
    bias_pattern: string;
    recommended_action: string;
  };
}

export function useFairnessSummary(nSamples: number = 1000, driftLevel: number = 0.5, enabled: boolean = true) {
  return useQuery({
    queryKey: ['fairness-summary', nSamples, driftLevel],
    queryFn: async () => {
      const { data } = await axios.get<FairnessSummaryResponse>(
        `${API_BASE}/api/fairness_summary`,
        { params: { n_samples: nSamples, drift_level: driftLevel } }
      );
      return data;
    },
    refetchInterval: 30000,
    enabled,
  });
}

export function useExplainability(nSamples: number = 1000, driftLevel: number = 0.5, enabled: boolean = true) {
  return useQuery({
    queryKey: ['explainability', nSamples, driftLevel],
    queryFn: async () => {
      const { data } = await axios.get<ExplainabilityResponse>(
        `${API_BASE}/api/explainability`,
        { params: { n_samples: nSamples, drift_level: driftLevel } }
      );
      return data;
    },
    refetchInterval: 30000,
    enabled,
  });
}

export function useExportReport() {
  return useMutation({
    mutationFn: async ({ nSamples, driftLevel }: { nSamples: number; driftLevel: number }) => {
      const response = await axios.post(
        `${API_BASE}/api/export_report`,
        { n_samples: nSamples, drift_level: driftLevel },
        { responseType: 'blob' }
      );
      
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `fairness_report_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      return response.data;
    },
  });
}

export function useExportCSV() {
  return useMutation({
    mutationFn: async ({ nSamples, driftLevel }: { nSamples: number; driftLevel: number }) => {
      const response = await axios.post(
        `${API_BASE}/api/export_csv`,
        { n_samples: nSamples, drift_level: driftLevel },
        { responseType: 'blob' }
      );
      
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `fairness_data_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      return response.data;
    },
  });
}
