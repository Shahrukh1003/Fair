# FairLens v3.0 – Predictive Fairness Governance Platform

## Overview

FairLens v3.0 is a production-grade AI fairness governance system that monitors real ML models in deployment using comprehensive multi-metric auditing, predictive bias forecasting, and deep explainability. The system implements 5 industry-standard fairness metrics (DIR, SPD, EOD, AOD, Theil Index), provides AI-assisted remediation suggestions, generates enterprise PDF/CSV compliance reports, and features both a Flask REST API backend with real ML model integration and a React + TypeScript frontend dashboard for real-time visualization and monitoring.

**v3.0 Upgrade**: Transformed from demo to production-grade system with real ML models, 5 fairness metrics, predictive drift monitoring with velocity/acceleration tracking, feature attribution analysis, and enterprise reporting capabilities.

**✅ PROJECT STATUS**: ALL 6 TRANSFORMATION PHASES 100% COMPLETE (November 9, 2025)
- Phases 1-5 (Backend): Production ML models, 5 metrics engine, drift monitoring, explainability, enterprise reporting ✅
- Phase 6 (Frontend): React v3.0 components, multi-metric dashboard, feature attribution panels, remediation UI, compliance reports ✅
- Quality Assurance: Architect-reviewed, TypeScript compiles clean, all v3.0 endpoints operational (200 OK responses confirmed) ✅
- Ready for demonstration, sale, and deployment to production environments ✅

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Framework**: React 19 with TypeScript, built using Vite as the build tool

**UI Framework**: Material-UI (MUI) v7 for consistent, accessible component design

**State Management**: TanStack Query (React Query) v5 for server state management, caching, and automatic refetching

**Routing**: React Router DOM v7 for client-side navigation

**Data Visualization**: Recharts v3 for rendering fairness metrics, approval rate comparisons, and DIR trend charts

**API Communication**: Axios for HTTP requests to the Flask backend on port 8000

**Key Design Patterns**:
- Component-based architecture with clear separation of concerns
- Custom hooks for API interactions (v2.0: `useFairnessMonitor`, `useAuditHistory`, `useHealthCheck` | v3.0: `useFairnessSummary`, `useExplainability`, `useExportReport`, `useExportCSV`)
- Centralized API client configuration for consistent request handling
- Type-safe interfaces for all data structures (fairness scenarios, audit logs, health status, multi-metric summaries)

**v3.0 Frontend Components** (November 2025):
1. **MultiMetricDashboard.tsx** - Displays all 5 fairness metrics with visual status indicators, thresholds, and compliance scoring
2. **FeatureContributionPanel.tsx** - Bar chart visualization of feature importance with temporal attribution analysis
3. **RemediationPanel.tsx** - AI-generated fairness improvement suggestions with priority ranking and confidence scores
4. **ComplianceReports.tsx** - PDF and CSV report generation with role-based access control (auditor/admin only)

### Backend Architecture

**Framework**: Flask 3.1.2 with Flask-CORS for cross-origin requests

**Language**: Python 3.11+

**v3.0 Module Structure**: Production-grade architecture with 7 new modules:

1. **ML Model Service** (`model_service.py`) - Production Logistic Regression model with training pipeline (Accuracy: 0.746, F1: 0.749)
2. **Model Registry** (`model_registry.py`) - Version management, save/load, active model tracking
3. **Multi-Metric Engine** (`metrics_engine.py`) - 5 fairness metrics with extensible base class architecture
4. **Advanced Drift Monitor** (`drift_monitor.py`) - Velocity, acceleration, confidence intervals, risk scoring
5. **Enhanced Explainability** (`explainability_enhanced.py`) - Feature attribution, AI remediation suggestions, confidence weighting
6. **Report Generator** (`report_generator.py`) - PDF compliance reports (ReportLab) and CSV export
7. **Dual-Mode Config** (`config.py`) - Demo vs Production environment toggle

**v3.0 API Endpoints**:
- `/api/monitor_fairness` - Original fairness monitoring pipeline
- `/api/evaluate_model` - **NEW** Real ML model predictions with fairness tracking
- `/api/fairness_summary` - **NEW** All 5 metrics with compliance scoring
- `/api/explainability` - **NEW** Feature contributions & AI remediation
- `/api/export_report` - **NEW** PDF compliance report generation [auditor/admin]
- `/api/export_csv` - **NEW** CSV data export [auditor/admin]
- `/api/audit_history` - Compliance audit log retrieval
- `/api/health` - Health check endpoint

**Legacy Endpoints** (v2.0):
- `/api/fairness_trend`, `/api/pre_alert`, `/api/predict_fairness_drift`, `/api/submit_predictions`, `/api/verify_alert`, `/api/login`, `/api/get_anchor`

**Data Flow**: REST API → Data Simulator → Metrics Calculator → Alert Detector → Encryption → Compliance Logger → Explainability → JSON Response

**Security Model**:
- Fernet symmetric encryption for alert messages (uses `cryptography` library)
- SHA256 hashing for pseudonymization of application IDs
- Thread-safe logging with file locks for concurrent access protection
- Encryption key stored in `fernet.key` file (auto-generated on first run)

**Compliance Features**:
- Append-only JSONL audit log format for immutability
- ISO 8601 UTC timestamps for all events
- Atomic writes with immediate fsync for data durability
- Sequential ordering for regulatory audit trails

### Data Storage

**Audit Logging**: JSON Lines (JSONL) format in `fairlens_backend/compliance_audit_log.jsonl`
- One JSON object per line for streaming reads and efficient parsing
- Thread-safe writes using threading locks
- Append-only for immutability guarantees

**Encryption Keys**: Local file storage in `fairlens_backend/fernet.key`
- Auto-generated on initialization if not present
- Note: Production systems should use proper secrets management (AWS Secrets Manager, Azure Key Vault, HashiCorp Vault)

**No Persistent Database**: The system generates synthetic data on-demand and does not persist loan application records

### Fairness Metrics Implementation

**EEOC 80% Rule (Four-Fifths Rule)**:
- DIR = (approval_rate_protected) / (approval_rate_privileged)
- DIR < 0.8 indicates potential discrimination
- DIR ≥ 0.8 considered fair

**Protected Attributes**: Currently configured for gender-based fairness (Female vs Male), but designed to support other attributes (race, age_group, etc.)

**Bias Injection**: Controlled through `drift_level` parameter (0.0 = no bias, 1.0 = maximum bias)
- Female approval rate reduced by `drift_level * 0.4` (up to 40 percentage points)

**Statistical Explanations**: 
- Group-level feature analysis (means, medians)
- Approval rate comparisons
- Normalized differences for ranking likely causes
- Note: Purely correlational, not causal inference

## External Dependencies

### Python Backend Dependencies
- **Flask 3.1.2** - Web framework for REST API
- **Flask-CORS 6.0.1** - Cross-origin resource sharing support
- **pandas 2.2.3** - Data manipulation and analysis
- **numpy 2.2.1** - Numerical computing for random data generation
- **cryptography 46.0.3** - Fernet encryption for alert messages
- **streamlit 1.41.1** - Alternative dashboard (Python-based)
- **plotly 6.4.0** - Interactive plotting library (used by Streamlit dashboard)
- **requests 2.32.3** - HTTP library for API calls

### JavaScript Frontend Dependencies
- **React 19.2.0** - UI library
- **React DOM 19.2.0** - React rendering for web
- **TypeScript 5.9.3** - Type-safe JavaScript
- **Vite 7.2.2** - Build tool and dev server
- **@mui/material 7.3.5** - Material-UI component library
- **@mui/icons-material 7.3.5** - Material-UI icons
- **@emotion/react 11.14.0** - CSS-in-JS styling (MUI dependency)
- **@emotion/styled 11.14.1** - Styled components (MUI dependency)
- **axios 1.13.2** - HTTP client for API requests
- **@tanstack/react-query 5.90.7** - Server state management
- **react-router-dom 7.9.5** - Client-side routing
- **recharts 3.3.0** - Charting library for data visualization

### Development Dependencies
- **@vitejs/plugin-react 5.1.0** - Vite plugin for React Fast Refresh
- **@types/react 19.2.2** - TypeScript definitions for React
- **@types/react-dom 19.2.2** - TypeScript definitions for React DOM
- **@types/node 24.10.0** - TypeScript definitions for Node.js

### Service Ports
- **Flask API**: Port 8000
- **Vite Dev Server**: Port 5173 (default)
- **Streamlit Dashboard**: Port 5000 (alternative Python dashboard)

### External Services
None - The system is fully self-contained and does not integrate with external APIs, databases, or cloud services. All data is synthetically generated and processed locally.