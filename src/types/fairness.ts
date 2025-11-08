export interface FairnessScenario {
  dir: number;
  dir_alert: boolean;
  female_rate: number;
  male_rate: number;
  gap?: number;
  details?: {
    female_approved: number;
    female_count: number;
    male_approved: number;
    male_count: number;
  };
  explanation?: string;
  encrypted_alert?: string;
  likely_causes?: string[];
}

export interface FairnessCheckResponse {
  fair_scenario: FairnessScenario;
  drifted_scenario: FairnessScenario;
  audit_tail: AuditLogEntry[];
}

export interface AuditLogEntry {
  timestamp: string;
  event_type: string;
  details: {
    status: string;
    dir: number;
    female_rate: number;
    male_rate: number;
    drift_level: number;
    n_samples: number;
    encrypted_alert?: string;
    explanation?: string;
  };
}

export interface HealthStatus {
  service: string;
  status: string;
  version: string;
}

export interface MonitorParams {
  n_samples: number;
  drift_level: number;
}

export interface LoginRequest {
  role: 'monitor' | 'auditor' | 'admin';
}

export interface LoginResponse {
  token: string;
  role: string;
  message: string;
  usage: string;
}

export interface FairnessTrendResponse {
  dir_values: number[];
  average_dir: number;
  median_dir: number;
  min_dir: number;
  max_dir: number;
  alert_count: number;
  data_points: number;
  trend_direction: 'up' | 'down' | 'stable';
}

export interface PreAlertResponse {
  pre_alert: boolean;
  current_avg: number;
  message: string;
  trend: string;
  severity: string;
  recommendation: string;
}

export interface DriftPrediction {
  prediction: string;
  trend: string;
  current_dir: number;
  velocity: number;
  is_accelerating: boolean;
  estimated_checks_to_threshold: number | null;
  message: string;
  severity: string;
  recommendation: string;
  confidence: number;
  details: {
    trend_direction: string;
    velocity_per_check: number;
    current_average_dir: number;
    distance_from_threshold: number;
    estimated_checks_to_threshold: number | null;
    alert_count_in_window: number;
    data_points_analyzed: number;
    is_accelerating: boolean;
  };
}

export interface BlockchainAnchor {
  tx_id: string;
  record_hash: string;
  timestamp: string;
  status: string;
  network: string;
  block_number: number;
  explorer_url: string;
  metadata: {
    alert: boolean;
    db_record_id: number;
  };
  model_name: string;
}
