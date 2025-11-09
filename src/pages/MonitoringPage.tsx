import { useState } from 'react';
import {
  Box,
  Grid,
  Typography,
  Button,
  Paper,
  Stack,
  Alert,
  Snackbar,
} from '@mui/material';
import { PlayArrow, Science } from '@mui/icons-material';
import { MultiMetricDashboard } from '../components/MultiMetricDashboard';
import { FeatureContributionPanel } from '../components/FeatureContributionPanel';
import { RemediationPanel } from '../components/RemediationPanel';
import { FairnessTrend } from '../components/FairnessTrend';
import { PreAlertPanel } from '../components/PreAlertPanel';
import { useMonitorMutation } from '../hooks/useFairnessMonitor';

export function MonitoringPage() {
  const [nSamples] = useState(1000);
  const [fairDrift, setFairDrift] = useState(0.0);
  const [biasedDrift, setBiasedDrift] = useState(0.5);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error' | 'warning',
  });

  const monitorMutation = useMonitorMutation();

  const handleRunFairCheck = () => {
    setFairDrift(0.0);
    setAutoRefresh(false);
    
    monitorMutation.mutate(
      { n_samples: nSamples, drift_level: 0.0 },
      {
        onSuccess: () => {
          setSnackbar({
            open: true,
            message: '✅ Fair check complete! All metrics within acceptable thresholds.',
            severity: 'success',
          });
        },
        onError: () => {
          setSnackbar({
            open: true,
            message: 'Error running fairness check. Please ensure backend is running.',
            severity: 'error',
          });
        },
      }
    );
  };

  const handleRunBiasedCheck = () => {
    setBiasedDrift(0.5);
    setAutoRefresh(false);
    
    monitorMutation.mutate(
      { n_samples: nSamples, drift_level: 0.5 },
      {
        onSuccess: (data) => {
          if (data.drifted_scenario.dir_alert) {
            setSnackbar({
              open: true,
              message: '⚠️ Bias detected! DIR below 0.8 threshold. Review feature attribution below.',
              severity: 'warning',
            });
          }
        },
        onError: () => {
          setSnackbar({
            open: true,
            message: 'Error running drift simulation.',
            severity: 'error',
          });
        },
      }
    );
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1, color: 'primary.main' }}>
          Live Monitoring
        </Typography>
        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
          Run fairness checks and detect bias in real-time
        </Typography>
      </Box>

      <Paper
        sx={{
          p: 3,
          mb: 3,
          background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%)',
          border: '1px solid rgba(99, 102, 241, 0.2)',
        }}
      >
        <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>
          Demo Controls
        </Typography>
        <Typography variant="body2" sx={{ color: 'text.secondary', mb: 3 }}>
          Test the fairness monitoring system with different scenarios
        </Typography>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
          <Button
            variant="contained"
            size="large"
            startIcon={<PlayArrow />}
            onClick={handleRunFairCheck}
            disabled={monitorMutation.isPending}
            sx={{
              px: 4,
              py: 1.5,
              background: 'linear-gradient(135deg, #10b981 0%, #34d399 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #059669 0%, #10b981 100%)',
              },
            }}
          >
            Run Fair Check
          </Button>
          <Button
            variant="contained"
            size="large"
            startIcon={<Science />}
            onClick={handleRunBiasedCheck}
            disabled={monitorMutation.isPending}
            sx={{
              px: 4,
              py: 1.5,
              background: 'linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #d97706 0%, #f59e0b 100%)',
              },
            }}
          >
            Trigger Drift Scenario
          </Button>
        </Stack>
        {monitorMutation.isPending && (
          <Alert severity="info" sx={{ mt: 2 }}>
            Running fairness check...
          </Alert>
        )}
      </Paper>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={4}>
          <Stack spacing={3}>
            <FairnessTrend />
            <PreAlertPanel />
          </Stack>
        </Grid>
        <Grid item xs={12} lg={8}>
          <Stack spacing={3}>
            <MultiMetricDashboard
              nSamples={nSamples}
              driftLevel={fairDrift || biasedDrift}
              autoRefresh={autoRefresh}
            />
            <FeatureContributionPanel
              nSamples={nSamples}
              driftLevel={fairDrift || biasedDrift}
              autoRefresh={autoRefresh}
            />
            <RemediationPanel
              nSamples={nSamples}
              driftLevel={fairDrift || biasedDrift}
              autoRefresh={autoRefresh}
            />
          </Stack>
        </Grid>
      </Grid>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          variant="filled"
          sx={{ boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}
