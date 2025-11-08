import { useState, useEffect } from 'react';
import {
  Box,
  Container,
  AppBar,
  Toolbar,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Snackbar,
} from '@mui/material';
import Grid2 from '@mui/material/Unstable_Grid2';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import AssessmentIcon from '@mui/icons-material/Assessment';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ControlPanel } from './components/ControlPanel';
import { MetricsOverview } from './components/MetricsOverview';
import { AlertPanel } from './components/AlertPanel';
import { ChartsSection } from './components/ChartsSection';
import { AuditLogTable } from './components/AuditLogTable';
import { useMonitorMutation, useAuditHistory, useHealthCheck } from './hooks/useFairnessMonitor';
import type { FairnessCheckResponse } from './types/fairness';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
});

function DashboardContent() {
  const [lastResult, setLastResult] = useState<FairnessCheckResponse | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [nSamples, setNSamples] = useState(1000);
  const [driftLevel, setDriftLevel] = useState(0.5);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });

  const monitorMutation = useMonitorMutation();
  const { data: auditHistory, refetch: refetchAudit } = useAuditHistory(20);
  const { data: health } = useHealthCheck();

  const handleRunCheck = (samples: number, drift: number) => {
    setNSamples(samples);
    setDriftLevel(drift);
    
    monitorMutation.mutate(
      { n_samples: samples, drift_level: drift },
      {
        onSuccess: (data) => {
          setLastResult(data);
          refetchAudit();
          setSnackbar({
            open: true,
            message: data.drifted_scenario.dir_alert 
              ? 'Bias detected! Check the alert details below.' 
              : 'Check complete. System is operating fairly.',
            severity: data.drifted_scenario.dir_alert ? 'error' : 'success',
          });
        },
        onError: (error) => {
          setSnackbar({
            open: true,
            message: `Error: ${error.message}. Make sure the Flask API is running on port 8000.`,
            severity: 'error',
          });
        },
      }
    );
  };

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        handleRunCheck(nSamples, driftLevel);
      }, 10000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, nSamples, driftLevel]);

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', bgcolor: 'grey.50' }}>
      <AppBar position="static" elevation={2}>
        <Toolbar>
          <AssessmentIcon sx={{ mr: 2 }} />
          <Typography variant="h5" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
            FairLens Fairness Drift Alert System
          </Typography>
          {health && (
            <Typography variant="body2" sx={{ 
              bgcolor: 'success.dark', 
              px: 2, 
              py: 0.5, 
              borderRadius: 1 
            }}>
              ● API Online
            </Typography>
          )}
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4, flexGrow: 1 }}>
        <Paper elevation={0} sx={{ p: 2, mb: 3, bgcolor: 'info.50', borderLeft: 4, borderColor: 'info.main' }}>
          <Typography variant="body2" color="text.secondary">
            <strong>For Non-Technical Administrators:</strong> This dashboard helps you monitor fairness in loan approval decisions. 
            A <strong>DIR (Disparate Impact Ratio)</strong> below 0.8 means there may be unfair bias against female applicants. 
            The system automatically checks for bias and alerts you when action is needed.
          </Typography>
        </Paper>

        <Grid2 container spacing={3}>
          <Grid2 size={{ xs: 12, lg: 4 }}>
            <ControlPanel
              onRunCheck={handleRunCheck}
              isLoading={monitorMutation.isPending}
              autoRefresh={autoRefresh}
              onAutoRefreshToggle={setAutoRefresh}
            />
          </Grid2>

          <Grid2 size={{ xs: 12, lg: 8 }}>
            {monitorMutation.isPending && (
              <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 200 }}>
                <CircularProgress size={60} />
                <Typography variant="h6" sx={{ ml: 2 }}>
                  Running fairness check...
                </Typography>
              </Box>
            )}

            {monitorMutation.isError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                <Typography variant="body2">
                  Failed to connect to the API. Please ensure the Flask backend is running on port 8000.
                </Typography>
              </Alert>
            )}

            {lastResult && !monitorMutation.isPending && (
              <Box>
                <AlertPanel scenario={lastResult.drifted_scenario} />
                <Box sx={{ mt: 3 }}>
                  <MetricsOverview scenario={lastResult.drifted_scenario} />
                </Box>
                {lastResult.fair_scenario && (
                  <Box sx={{ mt: 3 }}>
                    <MetricsOverview scenario={lastResult.fair_scenario} isFair />
                  </Box>
                )}
              </Box>
            )}
          </Grid2>

          {lastResult && auditHistory && auditHistory.length > 0 && (
            <>
              <Grid2 size={{ xs: 12 }}>
                <ChartsSection
                  fairScenario={lastResult.fair_scenario}
                  driftedScenario={lastResult.drifted_scenario}
                  auditHistory={auditHistory}
                />
              </Grid2>

              <Grid2 size={{ xs: 12 }}>
                <AuditLogTable entries={auditHistory} />
              </Grid2>
            </>
          )}

          {!lastResult && (
            <Grid2 size={{ xs: 12 }}>
              <Paper sx={{ p: 4, textAlign: 'center', bgcolor: 'grey.50' }}>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  No fairness check has been run yet
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Use the controls on the left to configure and run your first fairness check
                </Typography>
              </Paper>
            </Grid2>
          )}
        </Grid2>
      </Container>

      <Box
        component="footer"
        sx={{
          py: 2,
          px: 2,
          mt: 'auto',
          bgcolor: 'grey.200',
          borderTop: 1,
          borderColor: 'divider',
        }}
      >
        <Typography variant="body2" color="text.secondary" align="center">
          FairLens v1.0.0 | Ensuring Fair Lending Practices | EEOC 80% Rule Compliance
        </Typography>
      </Box>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={() => setSnackbar({ ...snackbar, open: false })} 
          severity={snackbar.severity}
          variant="filled"
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <DashboardContent />
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
