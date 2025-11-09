import type { ReactNode } from 'react';
import { Box, Grid, Paper, Typography, Card, CardContent, LinearProgress, Fade } from '@mui/material';
import {
  TrendingUp,
  Warning,
  CheckCircle,
  Assessment,
  Speed,
} from '@mui/icons-material';
import { useHealthCheck } from '../hooks/useFairnessMonitor';
import { useFairnessTrend, useDriftPrediction } from '../hooks/useFairnessV3';
import { SectionHeader } from '../components/SectionHeader';
import { MetricCardSkeleton, ChartSkeleton } from '../components/LoadingSkeleton';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  color?: string;
}

function MetricCard({ title, value, subtitle, icon, trend, color = '#6366f1' }: MetricCardProps) {
  return (
    <Card
      sx={{
        height: '100%',
        position: 'relative',
        overflow: 'hidden',
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: '0 12px 40px rgba(0, 0, 0, 0.12)',
        },
      }}
    >
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Box
            sx={{
              width: 56,
              height: 56,
              borderRadius: 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: `linear-gradient(135deg, ${color}22 0%, ${color}11 100%)`,
              border: `1px solid ${color}33`,
            }}
          >
            {icon}
          </Box>
          {trend && (
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 0.5,
                color: trend === 'up' ? 'success.main' : trend === 'down' ? 'error.main' : 'text.secondary',
              }}
            >
              <TrendingUp fontSize="small" sx={{ transform: trend === 'down' ? 'rotate(180deg)' : 'none' }} />
            </Box>
          )}
        </Box>
        <Typography variant="h3" sx={{ fontWeight: 700, mb: 0.5, color: 'primary.main' }}>
          {value}
        </Typography>
        <Typography variant="body2" sx={{ color: 'text.secondary', fontWeight: 600, mb: 0.5 }}>
          {title}
        </Typography>
        {subtitle && (
          <Typography variant="caption" sx={{ color: 'text.secondary' }}>
            {subtitle}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}

export function OverviewPage() {
  const { data: health, isLoading: healthLoading } = useHealthCheck();
  const { data: trendData, isLoading: trendLoading } = useFairnessTrend();
  const { data: driftData, isLoading: driftLoading } = useDriftPrediction();

  const isLoading = healthLoading || trendLoading || driftLoading;

  const complianceScore = trendData?.trend_data && trendData.trend_data.length > 0
    ? Math.round((trendData.trend_data.filter((d: any) => d.dir >= 0.8).length / trendData.trend_data.length) * 100)
    : 0;

  return (
    <Box>
      <SectionHeader
        title="System Overview"
        subtitle="Real-time monitoring of AI fairness across all deployed models"
        icon={<Speed sx={{ fontSize: 24, color: 'primary.main' }} />}
      />

      <Grid container spacing={3} sx={{ mb: 5 }}>
        {isLoading ? (
          <>
            {[1, 2, 3, 4].map((i) => (
              <Grid item xs={12} sm={6} lg={3} key={i}>
                <MetricCardSkeleton />
              </Grid>
            ))}
          </>
        ) : (
          <>
            <Grid item xs={12} sm={6} lg={3}>
              <Fade in timeout={300}>
                <div>
                  <MetricCard
                    title="System Status"
                    value={health?.status === 'healthy' ? 'Online' : 'Offline'}
                    subtitle="All services operational"
                    icon={<CheckCircle sx={{ fontSize: 28, color: '#10b981' }} />}
                    color="#10b981"
                    trend="neutral"
                  />
                </div>
              </Fade>
            </Grid>
            <Grid item xs={12} sm={6} lg={3}>
              <Fade in timeout={400}>
                <div>
                  <MetricCard
                    title="Compliance Score"
                    value={`${complianceScore}%`}
                    subtitle="Based on fairness metrics"
                    icon={<Assessment sx={{ fontSize: 28, color: '#6366f1' }} />}
                    color="#6366f1"
                    trend={complianceScore >= 80 ? 'up' : 'down'}
                  />
                </div>
              </Fade>
            </Grid>
            <Grid item xs={12} sm={6} lg={3}>
              <Fade in timeout={500}>
                <div>
                  <MetricCard
                    title="Active Models"
                    value="1"
                    subtitle="Loan Approval Model v1.0"
                    icon={<TrendingUp sx={{ fontSize: 28, color: '#8b5cf6' }} />}
                    color="#8b5cf6"
                  />
                </div>
              </Fade>
            </Grid>
            <Grid item xs={12} sm={6} lg={3}>
              <Fade in timeout={600}>
                <div>
                  <MetricCard
                    title="Drift Status"
                    value={driftData?.alert ? 'Warning' : 'Normal'}
                    subtitle={driftData?.message || 'No drift detected'}
                    icon={<Warning sx={{ fontSize: 28, color: driftData?.alert ? '#f59e0b' : '#10b981' }} />}
                    color={driftData?.alert ? '#f59e0b' : '#10b981'}
                    trend={driftData?.alert ? 'down' : 'neutral'}
                  />
                </div>
              </Fade>
            </Grid>
          </>
        )}
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          {isLoading ? (
            <ChartSkeleton height={300} />
          ) : (
            <Fade in timeout={700}>
              <Paper
                elevation={2}
                sx={{
                  p: 3,
                  height: '100%',
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  '&:hover': {
                    boxShadow: 4,
                    transform: 'translateY(-2px)',
                  },
                }}
              >
            <Typography variant="h6" sx={{ fontWeight: 700, mb: 3 }}>
              Compliance Status
            </Typography>
            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Overall Fairness
                </Typography>
                <Typography variant="body2" fontWeight={600} color="primary.main">
                  {complianceScore}%
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={complianceScore}
                sx={{
                  height: 12,
                  borderRadius: 6,
                  bgcolor: 'rgba(99, 102, 241, 0.1)',
                  '& .MuiLinearProgress-bar': {
                    borderRadius: 6,
                    background: complianceScore >= 80
                      ? 'linear-gradient(90deg, #10b981 0%, #34d399 100%)'
                      : 'linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%)',
                  },
                }}
              />
            </Box>
            <Grid container spacing={2}>
              {[
                { label: 'Disparate Impact Ratio', value: trendData?.current_metrics?.avg_dir?.toFixed(2) || 'N/A', threshold: '≥ 0.80' },
                { label: 'Statistical Parity Diff', value: 'Monitored', threshold: '< 0.10' },
                { label: 'Equal Opportunity Diff', value: 'Monitored', threshold: '< 0.10' },
                { label: 'Drift Velocity', value: driftData?.velocity?.toFixed(3) || 'N/A', threshold: 'Stable' },
              ].map((metric, idx) => (
                <Grid item xs={12} sm={6} key={idx}>
                  <Box
                    sx={{
                      p: 2,
                      borderRadius: 2,
                      bgcolor: 'rgba(99, 102, 241, 0.05)',
                      border: '1px solid rgba(99, 102, 241, 0.1)',
                    }}
                  >
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                      {metric.label}
                    </Typography>
                    <Typography variant="h6" sx={{ fontWeight: 700, mb: 0.5 }}>
                      {metric.value}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Threshold: {metric.threshold}
                    </Typography>
                  </Box>
                </Grid>
              ))}
            </Grid>
              </Paper>
            </Fade>
          )}
        </Grid>

        <Grid item xs={12} lg={4}>
          {isLoading ? (
            <ChartSkeleton height={300} />
          ) : (
            <Fade in timeout={800}>
              <Paper
                elevation={2}
                sx={{
                  p: 3,
                  height: '100%',
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  '&:hover': {
                    boxShadow: 4,
                    transform: 'translateY(-2px)',
                  },
                }}
              >
            <Typography variant="h6" sx={{ fontWeight: 700, mb: 3 }}>
              System Health
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {[
                { service: 'API Server', status: 'Online', color: '#10b981' },
                { service: 'PostgreSQL DB', status: 'Connected', color: '#10b981' },
                { service: 'ML Model', status: 'Active', color: '#10b981' },
                { service: 'Webhook Alerts', status: 'Configured', color: '#f59e0b' },
              ].map((item, idx) => (
                <Box
                  key={idx}
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    p: 2,
                    borderRadius: 2,
                    bgcolor: `${item.color}11`,
                    border: `1px solid ${item.color}33`,
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box
                      sx={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        bgcolor: item.color,
                        boxShadow: `0 0 8px ${item.color}`,
                      }}
                    />
                    <Typography variant="body2" fontWeight={600}>
                      {item.service}
                    </Typography>
                  </Box>
                  <Typography variant="caption" sx={{ color: item.color, fontWeight: 600 }}>
                    {item.status}
                  </Typography>
                </Box>
              ))}
            </Box>
              </Paper>
            </Fade>
          )}
        </Grid>
      </Grid>
    </Box>
  );
}
