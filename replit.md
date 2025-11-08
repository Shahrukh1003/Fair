# FairLens – Fairness Drift Alert System

## Overview

FairLens is a production-ready fairness monitoring system that detects bias in automated loan decisions using the EEOC 80% rule (Disparate Impact Ratio). The system generates synthetic loan application data with controllable bias levels, computes fairness metrics, triggers encrypted alerts when bias is detected, maintains an immutable compliance audit log, and provides statistical explanations for detected bias. The application features both a Flask REST API backend and a React + TypeScript frontend dashboard for real-time visualization and monitoring.

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
- Custom hooks for API interactions (`useFairnessMonitor`, `useAuditHistory`, `useHealthCheck`)
- Centralized API client configuration for consistent request handling
- Type-safe interfaces for all data structures (fairness scenarios, audit logs, health status)

### Backend Architecture

**Framework**: Flask 3.1.2 with Flask-CORS for cross-origin requests

**Language**: Python 3.11+

**Module Structure**: The backend follows a pipeline architecture with six distinct stages:
1. **Data Generation** (`data_simulator.py`) - Creates synthetic loan data with controllable bias
2. **Metrics Calculation** (`fairness_metrics.py`) - Computes Disparate Impact Ratio using EEOC 80% rule
3. **Alert Detection** - Triggers alerts when DIR < 0.8
4. **Security** (`security_utils.py`) - Encrypts sensitive alert messages using Fernet symmetric encryption
5. **Compliance Logging** (`compliance_logger.py`) - Maintains append-only JSONL audit trail
6. **Explainability** (`explainability_module.py`) - Generates statistical analysis of bias causes

**API Endpoints**:
- `/api/monitor_fairness` - Orchestrates the entire pipeline, generates data, computes metrics, triggers alerts
- `/api/audit_history` - Retrieves compliance audit log entries
- `/api/health` - Health check endpoint for monitoring backend availability

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