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
