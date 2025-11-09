import { Box, Paper, Typography, Chip, LinearProgress, Stack } from '@mui/material';
import LightbulbIcon from '@mui/icons-material/Lightbulb';
import PriorityHighIcon from '@mui/icons-material/PriorityHigh';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import { useExplainability } from '../hooks/useFairnessV3';

interface RemediationPanelProps {
  nSamples: number;
  driftLevel: number;
  autoRefresh?: boolean;
}

export function RemediationPanel({ nSamples, driftLevel, autoRefresh = false }: RemediationPanelProps) {
  const { data, isLoading, error } = useExplainability(nSamples, driftLevel, autoRefresh);

  if (isLoading) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>AI-Assisted Remediation</Typography>
        <LinearProgress />
      </Paper>
    );
  }

  if (error || !data) {
    return (
      <Paper sx={{ p: 3, bgcolor: 'error.light' }}>
        <Typography>Failed to load remediation suggestions</Typography>
      </Paper>
    );
  }

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'critical': return <PriorityHighIcon />;
      case 'high': return <TrendingUpIcon />;
      default: return <LightbulbIcon />;
    }
  };

  return (
    <Paper
      elevation={3}
      sx={{
        p: 4,
        background: 'linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(254,252,232,0.95) 100%)',
        borderRadius: 4,
        border: '2px solid',
        borderColor: 'warning.light',
      }}
    >
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
          <LightbulbIcon sx={{ fontSize: 32, color: 'warning.main' }} />
          <Typography variant="h5" sx={{ fontWeight: 700, color: 'primary.main' }}>
            AI-Assisted Remediation Suggestions
          </Typography>
        </Box>
        <Typography variant="body2" color="text.secondary">
          Automated recommendations to improve fairness and reduce bias
        </Typography>
      </Box>

      <Stack spacing={2}>
        {data.remediation_suggestions.map((suggestion, index) => (
          <RemediationCard
            key={index}
            suggestion={suggestion}
            priority={suggestion.priority}
            getPriorityColor={getPriorityColor}
            getPriorityIcon={getPriorityIcon}
          />
        ))}
      </Stack>

      <Box sx={{ mt: 3, p: 2, bgcolor: 'success.lighter', borderRadius: 2, border: '1px solid', borderColor: 'success.light' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <CheckCircleOutlineIcon sx={{ color: 'success.dark' }} />
          <Typography variant="subtitle2" sx={{ fontWeight: 700, color: 'success.dark' }}>
            IMPLEMENTATION GUIDANCE
          </Typography>
        </Box>
        <Typography variant="body2" sx={{ color: 'success.dark' }}>
          Implement suggestions in priority order. Monitor fairness metrics after each change.
          Re-evaluate model performance to ensure improvements don't compromise accuracy.
        </Typography>
      </Box>
    </Paper>
  );
}

interface RemediationCardProps {
  suggestion: {
    priority: string;
    action: string;
    expected_impact: string;
    confidence: number;
  };
  priority: string;
  getPriorityColor: (priority: string) => any;
  getPriorityIcon: (priority: string) => React.ReactElement;
}

function RemediationCard({ suggestion, priority, getPriorityColor, getPriorityIcon }: RemediationCardProps) {
  return (
    <Paper
      elevation={2}
      sx={{
        p: 3,
        border: '2px solid',
        borderColor: `${getPriorityColor(priority)}.light`,
        bgcolor: `${getPriorityColor(priority)}.lighter`,
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 6,
        }
      }}
    >
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
        <Chip
          icon={getPriorityIcon(priority)}
          label={`${priority.toUpperCase()} PRIORITY`}
          color={getPriorityColor(priority)}
          sx={{ fontWeight: 700 }}
        />
        <Chip
          label={`${(suggestion.confidence * 100).toFixed(0)}% Confidence`}
          size="small"
          variant="outlined"
          sx={{ fontWeight: 600 }}
        />
      </Box>

      <Typography variant="h6" sx={{ fontWeight: 700, mb: 1.5, color: 'text.primary' }}>
        {suggestion.action}
      </Typography>

      <Box sx={{ bgcolor: 'background.paper', p: 2, borderRadius: 1.5, mb: 2 }}>
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5, fontWeight: 600 }}>
          EXPECTED IMPACT
        </Typography>
        <Typography variant="body2" sx={{ color: 'text.primary' }}>
          {suggestion.expected_impact}
        </Typography>
      </Box>

      <LinearProgress
        variant="determinate"
        value={suggestion.confidence * 100}
        sx={{
          height: 6,
          borderRadius: 1,
          bgcolor: 'grey.200',
          '& .MuiLinearProgress-bar': {
            bgcolor: `${getPriorityColor(priority)}.main`,
          }
        }}
      />
    </Paper>
  );
}
