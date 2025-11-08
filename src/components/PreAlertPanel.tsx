import { useQuery } from '@tanstack/react-query';
import { Box, Paper, Typography, Alert, CircularProgress, Chip } from '@mui/material';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import SpeedIcon from '@mui/icons-material/Speed';
import { fairnessApi } from '../api/client';

export function PreAlertPanel() {
  const { data: preAlert, isLoading: preAlertLoading } = useQuery({
    queryKey: ['preAlert'],
    queryFn: fairnessApi.getPreAlert,
    refetchInterval: 30000,
  });

  const { data: driftPrediction, isLoading: driftLoading } = useQuery({
    queryKey: ['driftPrediction'],
    queryFn: fairnessApi.predictDrift,
    refetchInterval: 30000,
  });

  if (preAlertLoading || driftLoading) {
    return (
      <Paper sx={{ p: 2, textAlign: 'center' }}>
        <CircularProgress size={30} />
      </Paper>
    );
  }

  if (!preAlert || !driftPrediction) return null;

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
      case 'critical':
        return 'error';
      case 'medium':
        return 'warning';
      default:
        return 'success';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'high':
      case 'critical':
        return <ErrorIcon />;
      case 'medium':
        return <WarningAmberIcon />;
      default:
        return <CheckCircleIcon />;
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {preAlert.pre_alert && (
        <Alert
          severity={getSeverityColor(preAlert.severity) as 'error' | 'warning' | 'success'}
          icon={getSeverityIcon(preAlert.severity)}
          sx={{
            borderRadius: 3,
            '& .MuiAlert-icon': {
              fontSize: 28,
            },
          }}
        >
          <Typography variant="subtitle2" fontWeight={700} gutterBottom>
            Pre-Alert: Fairness Degrading
          </Typography>
          <Typography variant="body2" sx={{ mb: 1 }}>
            {preAlert.message}
          </Typography>
          <Typography variant="caption" display="block" sx={{ mt: 1, fontStyle: 'italic' }}>
            {preAlert.recommendation}
          </Typography>
        </Alert>
      )}

      <Paper
        sx={{
          p: 2.5,
          background: `linear-gradient(135deg, ${
            driftPrediction.severity === 'high' ? 'rgba(239, 68, 68, 0.1)' : 
            driftPrediction.severity === 'medium' ? 'rgba(245, 158, 11, 0.1)' : 
            'rgba(16, 185, 129, 0.1)'
          } 0%, rgba(255, 255, 255, 0.8) 100%)`,
          border: `1px solid ${
            driftPrediction.severity === 'high' ? '#ef4444' : 
            driftPrediction.severity === 'medium' ? '#f59e0b' : 
            '#10b981'
          }`,
          borderRadius: 3,
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <SpeedIcon sx={{ color: getSeverityColor(driftPrediction.severity) + '.main' }} />
            <Typography variant="subtitle1" fontWeight={700}>
              Drift Prediction
            </Typography>
          </Box>
          <Chip
            label={driftPrediction.prediction.toUpperCase()}
            color={getSeverityColor(driftPrediction.severity)}
            size="small"
            sx={{ fontWeight: 600 }}
          />
        </Box>

        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {driftPrediction.message}
        </Typography>

        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 2 }}>
          <Box sx={{ flex: 1, minWidth: 120, p: 1.5, bgcolor: 'rgba(255, 255, 255, 0.7)', borderRadius: 2 }}>
            <Typography variant="caption" color="text.secondary" display="block">
              Current DIR
            </Typography>
            <Typography variant="h6" fontWeight={700} color={driftPrediction.current_dir < 0.8 ? 'error.main' : 'text.primary'}>
              {driftPrediction.current_dir.toFixed(3)}
            </Typography>
          </Box>
          <Box sx={{ flex: 1, minWidth: 120, p: 1.5, bgcolor: 'rgba(255, 255, 255, 0.7)', borderRadius: 2 }}>
            <Typography variant="caption" color="text.secondary" display="block">
              Velocity
            </Typography>
            <Typography variant="h6" fontWeight={700} color={driftPrediction.is_accelerating ? 'error.main' : 'text.primary'}>
              {driftPrediction.velocity > 0 ? '+' : ''}{driftPrediction.velocity.toFixed(3)}
            </Typography>
          </Box>
          <Box sx={{ flex: 1, minWidth: 120, p: 1.5, bgcolor: 'rgba(255, 255, 255, 0.7)', borderRadius: 2 }}>
            <Typography variant="caption" color="text.secondary" display="block">
              Confidence
            </Typography>
            <Typography variant="h6" fontWeight={700}>
              {(driftPrediction.confidence * 100).toFixed(0)}%
            </Typography>
          </Box>
        </Box>

        <Alert severity="info" icon={false} sx={{ fontSize: '0.85rem', py: 0.5 }}>
          {driftPrediction.recommendation}
        </Alert>
      </Paper>
    </Box>
  );
}
