import { Box, Card, CardContent, Typography, Chip, Tooltip, Stack } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import ErrorIcon from '@mui/icons-material/Error';
import InfoIcon from '@mui/icons-material/Info';
import { formatPercent, formatDir, getAlertColor } from '../utils/formatters';
import type { FairnessScenario } from '../types/fairness';

interface MetricsOverviewProps {
  scenario: FairnessScenario;
  isFair?: boolean;
}

const MetricCard = ({ 
  title, 
  value, 
  subtitle, 
  color, 
  tooltip 
}: { 
  title: string; 
  value: string; 
  subtitle?: string; 
  color?: string;
  tooltip?: string;
}) => (
  <Card 
    elevation={0} 
    sx={{ 
      height: '100%',
      border: '1px solid',
      borderColor: 'divider',
      borderRadius: 2,
      transition: 'all 0.2s',
      '&:hover': {
        boxShadow: 2,
        borderColor: 'primary.main',
      }
    }}
  >
    <CardContent sx={{ p: 2.5 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
        <Typography variant="body2" color="text.secondary">
          {title}
        </Typography>
        {tooltip && (
          <Tooltip title={tooltip}>
            <InfoIcon fontSize="small" color="action" />
          </Tooltip>
        )}
      </Box>
      <Typography variant="h4" sx={{ color: color || 'text.primary', fontWeight: 'bold' }}>
        {value}
      </Typography>
      {subtitle && (
        <Typography variant="caption" color="text.secondary">
          {subtitle}
        </Typography>
      )}
    </CardContent>
  </Card>
);

export const MetricsOverview = ({ scenario, isFair = false }: MetricsOverviewProps) => {
  const dirColor = scenario.dir_alert ? 'error.main' : 'success.main';
  const alertIcon = scenario.dir_alert ? (
    scenario.dir < 0.7 ? <ErrorIcon /> : <WarningIcon />
  ) : (
    <CheckCircleIcon />
  );

  return (
    <Card 
      elevation={0}
      sx={{ 
        borderRadius: 4,
        background: 'rgba(255, 255, 255, 0.7)',
        backdropFilter: 'blur(20px) saturate(180%)',
        WebkitBackdropFilter: 'blur(20px) saturate(180%)',
        border: '1px solid rgba(255, 255, 255, 0.3)',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.08)',
        transition: 'all 0.3s ease',
        animation: 'fadeIn 0.6s ease-out',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: '0 12px 40px rgba(0, 0, 0, 0.12)',
        }
      }}
    >
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            {isFair ? '📊 Fair Baseline Scenario' : '📈 Current Scenario Metrics'}
          </Typography>
          <Chip
            icon={alertIcon}
            label={scenario.dir_alert ? 'Bias Detected' : 'Fair'}
            color={getAlertColor(scenario.dir_alert)}
            variant="filled"
            sx={{ fontWeight: 600 }}
          />
        </Box>

        <Stack spacing={2}>
          <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2 }}>
            <MetricCard
              title="DIR (Disparate Impact Ratio)"
              value={formatDir(scenario.dir)}
              subtitle={scenario.dir_alert ? 'Below 0.8 threshold' : 'Meets EEOC standard'}
              color={dirColor}
              tooltip="Ratio of female to male approval rates. Must be ≥ 0.8 to comply with EEOC 80% rule"
            />
            
            <MetricCard
              title="Female Approval Rate"
              value={formatPercent(scenario.female_rate)}
              subtitle={scenario.details ? `${scenario.details.female_approved} of ${scenario.details.female_count} approved` : ''}
              tooltip="Percentage of female applicants who were approved for loans"
            />
            
            <MetricCard
              title="Male Approval Rate"
              value={formatPercent(scenario.male_rate)}
              subtitle={scenario.details ? `${scenario.details.male_approved} of ${scenario.details.male_count} approved` : ''}
              tooltip="Percentage of male applicants who were approved for loans"
            />
            
            {scenario.gap !== undefined && (
              <MetricCard
                title="Approval Gap"
                value={formatPercent(scenario.gap)}
                subtitle="Difference between rates"
                color={scenario.gap > 0.2 ? 'error.main' : 'text.primary'}
                tooltip="Absolute difference between female and male approval rates"
              />
            )}
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
};
