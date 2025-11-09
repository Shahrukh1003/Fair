import { Box, Paper, Typography, LinearProgress, Chip } from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import { useExplainability } from '../hooks/useFairnessV3';

interface FeatureContributionPanelProps {
  nSamples: number;
  driftLevel: number;
  autoRefresh?: boolean;
}

export function FeatureContributionPanel({ nSamples, driftLevel, autoRefresh = false }: FeatureContributionPanelProps) {
  const { data, isLoading, error } = useExplainability(nSamples, driftLevel, autoRefresh);

  if (isLoading) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>Feature Attribution Analysis</Typography>
        <LinearProgress />
      </Paper>
    );
  }

  if (error || !data) {
    return (
      <Paper sx={{ p: 3, bgcolor: 'error.light' }}>
        <Typography>Failed to load feature contributions</Typography>
      </Paper>
    );
  }

  const chartData = data.feature_contributions.map(fc => ({
    name: fc.feature.replace('_', ' ').toUpperCase(),
    importance: fc.importance_score * 100,
    confidence: fc.confidence * 100,
  }));

  const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'];

  return (
    <Paper
      elevation={3}
      sx={{
        p: 4,
        background: 'linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(249,250,251,0.95) 100%)',
        borderRadius: 4,
      }}
    >
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 700, color: 'primary.main', mb: 1 }}>
          🧠 Feature Attribution Analysis
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Understanding which features contribute most to potential bias
        </Typography>
      </Box>

      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1.4fr 1fr' }, gap: 3 }}>
        <Box>
          <Box sx={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={chartData}
                layout="vertical"
                margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis type="number" domain={[0, 100]} />
                <YAxis dataKey="name" type="category" width={90} />
                <Tooltip
                  formatter={(value: number) => `${value.toFixed(1)}%`}
                  contentStyle={{ borderRadius: 8, border: '1px solid #e5e7eb' }}
                />
                <Bar dataKey="importance" radius={[0, 8, 8, 0]}>
                  {chartData.map((_entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Box>
        </Box>

        <Box>
          <Box>
            <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 2, color: 'text.secondary' }}>
              TOP CONTRIBUTORS
            </Typography>
            {data.feature_contributions.slice(0, 5).map((fc, index) => (
              <FeatureContributionCard key={fc.feature} feature={fc} rank={index + 1} />
            ))}
          </Box>
        </Box>
      </Box>

      <Box sx={{ mt: 3, p: 2.5, bgcolor: 'primary.lighter', borderRadius: 2, border: '2px solid', borderColor: 'primary.light' }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 700, color: 'primary.dark', mb: 1 }}>
          📊 Bias Pattern Analysis
        </Typography>
        <Typography variant="body2" sx={{ color: 'primary.dark', mb: 1 }}>
          <strong>Top Contributor:</strong> {data.summary.top_contributor}
        </Typography>
        <Typography variant="body2" sx={{ color: 'primary.dark', mb: 1 }}>
          <strong>Detected Pattern:</strong> {data.summary.bias_pattern}
        </Typography>
        <Typography variant="body2" sx={{ color: 'primary.dark' }}>
          <strong>Recommended Action:</strong> {data.summary.recommended_action}
        </Typography>
      </Box>
    </Paper>
  );
}

interface FeatureContributionCardProps {
  feature: {
    feature: string;
    importance_score: number;
    contribution_to_bias: string;
    confidence: number;
  };
  rank: number;
}

function FeatureContributionCard({ feature, rank }: FeatureContributionCardProps) {
  const getRankColor = (rank: number) => {
    if (rank === 1) return '#fbbf24';
    if (rank === 2) return '#94a3b8';
    if (rank === 3) return '#cd7f32';
    return '#64748b';
  };

  const getContributionIcon = (contribution: string) => {
    return contribution.includes('INCREASES') ? <TrendingUpIcon fontSize="small" color="error" /> : <TrendingDownIcon fontSize="small" color="success" />;
  };

  return (
    <Box
      sx={{
        p: 2,
        mb: 1.5,
        bgcolor: 'background.paper',
        borderRadius: 2,
        border: '2px solid',
        borderColor: rank === 1 ? 'warning.main' : 'grey.200',
        transition: 'all 0.2s ease',
        '&:hover': {
          transform: 'translateX(8px)',
          boxShadow: 3,
        }
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box
            sx={{
              width: 28,
              height: 28,
              borderRadius: '50%',
              bgcolor: getRankColor(rank),
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 900,
              fontSize: '0.9rem',
            }}
          >
            {rank}
          </Box>
          <Typography variant="subtitle2" sx={{ fontWeight: 700, textTransform: 'uppercase' }}>
            {feature.feature.replace('_', ' ')}
          </Typography>
        </Box>
        {getContributionIcon(feature.contribution_to_bias)}
      </Box>

      <Box sx={{ mb: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
          <Typography variant="caption" color="text.secondary">Importance</Typography>
          <Typography variant="caption" sx={{ fontWeight: 700 }}>
            {(feature.importance_score * 100).toFixed(1)}%
          </Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={feature.importance_score * 100}
          sx={{
            height: 8,
            borderRadius: 1,
            bgcolor: 'grey.200',
            '& .MuiLinearProgress-bar': {
              bgcolor: getRankColor(rank),
            }
          }}
        />
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="caption" color="text.secondary">
          {feature.contribution_to_bias}
        </Typography>
        <Chip
          label={`${(feature.confidence * 100).toFixed(0)}% conf`}
          size="small"
          sx={{ height: 20, fontSize: '0.7rem' }}
        />
      </Box>
    </Box>
  );
}
