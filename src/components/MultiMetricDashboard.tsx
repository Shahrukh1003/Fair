import { Box, Paper, Typography, Chip, LinearProgress, Tooltip } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import InfoIcon from '@mui/icons-material/Info';
import { useFairnessSummary } from '../hooks/useFairnessV3';

interface MultiMetricDashboardProps {
  nSamples: number;
  driftLevel: number;
  autoRefresh?: boolean;
}

export function MultiMetricDashboard({ nSamples, driftLevel, autoRefresh = false }: MultiMetricDashboardProps) {
  const { data, isLoading, error } = useFairnessSummary(nSamples, driftLevel, autoRefresh);

  if (isLoading) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>Multi-Metric Fairness Analysis</Typography>
        <LinearProgress />
      </Paper>
    );
  }

  if (error || !data) {
    return (
      <Paper sx={{ p: 3, bgcolor: 'error.light', color: 'error.contrastText' }}>
        <Typography>Failed to load fairness metrics</Typography>
      </Paper>
    );
  }

  const metrics = data.metrics.all_metrics;
  const summary = data.metrics.summary;

  const getComplianceColor = (level: string) => {
    switch (level) {
      case 'FULL_COMPLIANCE': return 'success';
      case 'HIGH_COMPLIANCE': return 'success';
      case 'MODERATE_COMPLIANCE': return 'warning';
      case 'LOW_COMPLIANCE': return 'error';
      case 'NON_COMPLIANT': return 'error';
      default: return 'default';
    }
  };

  return (
    <Paper 
      elevation={3}
      sx={{ 
        p: 4,
        background: 'linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(240,242,255,0.9) 100%)',
        border: '2px solid',
        borderColor: summary.overall_status === 'PASS' ? 'success.main' : 'error.main',
        borderRadius: 4,
      }}
    >
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h5" sx={{ fontWeight: 700, color: 'primary.main' }}>
            🎯 Multi-Metric Fairness Analysis
          </Typography>
          <Chip
            icon={summary.overall_status === 'PASS' ? <CheckCircleIcon /> : <CancelIcon />}
            label={summary.compliance_level.replace('_', ' ')}
            color={getComplianceColor(summary.compliance_level) as any}
            sx={{ fontWeight: 700, px: 2, py: 2.5, fontSize: '0.9rem' }}
          />
        </Box>
        
        <Box sx={{ display: 'flex', gap: 3, mb: 3 }}>
          <Box>
            <Typography variant="caption" color="text.secondary">Fairness Score</Typography>
            <Typography variant="h4" sx={{ fontWeight: 800, color: summary.fairness_score >= 0.8 ? 'success.main' : 'error.main' }}>
              {(summary.fairness_score * 100).toFixed(0)}%
            </Typography>
          </Box>
          <Box>
            <Typography variant="caption" color="text.secondary">Metrics Passed</Typography>
            <Typography variant="h4" sx={{ fontWeight: 800 }}>
              {summary.passed}/{summary.total_metrics}
            </Typography>
          </Box>
        </Box>

        <LinearProgress
          variant="determinate"
          value={summary.fairness_score * 100}
          sx={{
            height: 12,
            borderRadius: 2,
            bgcolor: 'grey.200',
            '& .MuiLinearProgress-bar': {
              background: summary.fairness_score >= 0.8 
                ? 'linear-gradient(90deg, #10b981 0%, #34d399 100%)'
                : 'linear-gradient(90deg, #ef4444 0%, #f87171 100%)',
            }
          }}
        />
      </Box>

      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2.5 }}>
        <Box>
          <MetricCard
            title="Disparate Impact Ratio (DIR)"
            description="EEOC 80% Rule Compliance"
            value={metrics.DIR.value}
            threshold={metrics.DIR.threshold}
            status={metrics.DIR.status}
            details={`Protected: ${(metrics.DIR.protected_rate * 100).toFixed(1)}% | Privileged: ${(metrics.DIR.privileged_rate * 100).toFixed(1)}%`}
            interpretation={metrics.DIR.value >= 0.8 ? 'PASS: No disparate impact detected' : 'FAIL: Significant disparate impact'}
          />
        </Box>

        <Box>
          <MetricCard
            title="Statistical Parity Difference (SPD)"
            description="Group-Level Outcome Equality"
            value={Math.abs(metrics.SPD.value)}
            threshold={metrics.SPD.threshold}
            status={metrics.SPD.status}
            details={`Difference: ${(Math.abs(metrics.SPD.value) * 100).toFixed(1)}%`}
            interpretation={metrics.SPD.is_fair ? 'PASS: Statistical parity achieved' : 'FAIL: Unequal group outcomes'}
          />
        </Box>

        <Box>
          <MetricCard
            title="Equal Opportunity Difference (EOD)"
            description="True Positive Rate Parity"
            value={Math.abs(metrics.EOD.value)}
            threshold={metrics.EOD.threshold}
            status={metrics.EOD.status}
            details={`Protected TPR: ${(metrics.EOD.protected_tpr * 100).toFixed(1)}% | Privileged TPR: ${(metrics.EOD.privileged_tpr * 100).toFixed(1)}%`}
            interpretation={metrics.EOD.is_fair ? 'PASS: Equal opportunity maintained' : 'FAIL: Unequal true positive rates'}
          />
        </Box>

        <Box>
          <MetricCard
            title="Average Odds Difference (AOD)"
            description="TPR + FPR Parity"
            value={Math.abs(metrics.AOD.value)}
            threshold={metrics.AOD.threshold}
            status={metrics.AOD.status}
            details={`TPR Diff: ${(Math.abs(metrics.AOD.tpr_difference) * 100).toFixed(1)}% | FPR Diff: ${(Math.abs(metrics.AOD.fpr_difference) * 100).toFixed(1)}%`}
            interpretation={metrics.AOD.is_fair ? 'PASS: Average odds balanced' : 'FAIL: Imbalanced error rates'}
          />
        </Box>

        <Box sx={{ gridColumn: { xs: '1', md: '1 / -1' } }}>
          <MetricCard
            title="Theil Index"
            description="Group-Level Inequality Measure"
            value={metrics.THEIL.value}
            threshold={metrics.THEIL.threshold}
            status={metrics.THEIL.status}
            details={`Inequality Level: ${metrics.THEIL.inequality_level} | Overall Rate: ${(metrics.THEIL.overall_rate * 100).toFixed(1)}%`}
            interpretation={metrics.THEIL.is_fair ? 'PASS: Low inequality detected' : 'FAIL: High group-level inequality'}
          />
        </Box>
      </Box>

      <Box sx={{ mt: 3, p: 2, bgcolor: 'info.light', borderRadius: 2 }}>
        <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'info.dark' }}>
          <InfoIcon fontSize="small" />
          Last Updated: {new Date(data.timestamp).toLocaleString()} | Samples: {data.n_samples} | Drift Level: {(data.drift_level * 100).toFixed(0)}%
        </Typography>
      </Box>
    </Paper>
  );
}

interface MetricCardProps {
  title: string;
  description: string;
  value: number;
  threshold: number;
  status: string;
  details: string;
  interpretation: string;
}

function MetricCard({ title, description, value, threshold, status, details, interpretation }: MetricCardProps) {
  const isPassing = status === 'PASS';
  
  return (
    <Paper
      elevation={2}
      sx={{
        p: 2.5,
        height: '100%',
        border: '2px solid',
        borderColor: isPassing ? 'success.light' : 'error.light',
        bgcolor: isPassing ? 'success.lighter' : 'error.lighter',
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 6,
        }
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 2 }}>
        <Box sx={{ flex: 1 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 700, color: 'text.primary', mb: 0.5 }}>
            {title}
          </Typography>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1.5 }}>
            {description}
          </Typography>
        </Box>
        <Chip
          icon={isPassing ? <CheckCircleIcon /> : <CancelIcon />}
          label={status}
          size="small"
          color={isPassing ? 'success' : 'error'}
          sx={{ fontWeight: 700 }}
        />
      </Box>

      <Box sx={{ mb: 1.5 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', mb: 0.5 }}>
          <Typography variant="caption" color="text.secondary">Value</Typography>
          <Typography variant="h6" sx={{ fontWeight: 800, color: isPassing ? 'success.dark' : 'error.dark' }}>
            {value.toFixed(4)}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
          <Typography variant="caption" color="text.secondary">Threshold</Typography>
          <Typography variant="body2" sx={{ fontWeight: 600 }}>
            {threshold}
          </Typography>
        </Box>
      </Box>

      <Box sx={{ bgcolor: 'background.paper', p: 1.5, borderRadius: 1, mb: 1 }}>
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
          Details
        </Typography>
        <Typography variant="body2" sx={{ fontWeight: 600, fontSize: '0.8rem' }}>
          {details}
        </Typography>
      </Box>

      <Tooltip title={interpretation} arrow>
        <Typography 
          variant="caption" 
          sx={{ 
            display: 'block',
            color: isPassing ? 'success.dark' : 'error.dark',
            fontWeight: 700,
            fontSize: '0.75rem'
          }}
        >
          {interpretation.split(':')[0]}: {interpretation.split(':')[1]?.substring(0, 40)}...
        </Typography>
      </Tooltip>
    </Paper>
  );
}
