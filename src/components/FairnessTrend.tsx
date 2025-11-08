import { useQuery } from '@tanstack/react-query';
import { Box, Paper, Typography, Chip, CircularProgress, Alert } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import TrendingFlatIcon from '@mui/icons-material/TrendingFlat';
import { fairnessApi } from '../api/client';

export function FairnessTrend() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['fairnessTrend'],
    queryFn: fairnessApi.getFairnessTrend,
    refetchInterval: 30000,
  });

  if (isLoading) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <CircularProgress size={40} />
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          Loading trend data...
        </Typography>
      </Paper>
    );
  }

  if (error) {
    return (
      <Paper sx={{ p: 3 }}>
        <Alert severity="error">
          Failed to load trend data. {(error as Error).message}
        </Alert>
      </Paper>
    );
  }

  if (!data) return null;

  const chartData = data.dir_values.map((value, index) => ({
    check: index + 1,
    dir: value,
  }));

  const getTrendIcon = () => {
    switch (data.trend_direction) {
      case 'up':
        return <TrendingUpIcon />;
      case 'down':
        return <TrendingDownIcon />;
      default:
        return <TrendingFlatIcon />;
    }
  };

  const getTrendColor = () => {
    if (data.average_dir < 0.8) return 'error';
    if (data.trend_direction === 'down') return 'warning';
    return 'success';
  };

  return (
    <Paper
      sx={{
        p: 3,
        background: 'rgba(255, 255, 255, 0.8)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(99, 102, 241, 0.2)',
        borderRadius: 3,
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)',
      }}
    >
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6" fontWeight={700}>
          Fairness Trend Analysis
        </Typography>
        <Chip
          icon={getTrendIcon()}
          label={data.trend_direction.toUpperCase()}
          color={getTrendColor()}
          size="small"
          sx={{ fontWeight: 600 }}
        />
      </Box>

      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 2, mb: 3 }}>
        <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'grey.50', borderRadius: 2 }}>
          <Typography variant="caption" color="text.secondary" fontWeight={600}>
            Average DIR
          </Typography>
          <Typography variant="h6" fontWeight={700} color={data.average_dir < 0.8 ? 'error.main' : 'success.main'}>
            {data.average_dir.toFixed(3)}
          </Typography>
        </Box>
        <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'grey.50', borderRadius: 2 }}>
          <Typography variant="caption" color="text.secondary" fontWeight={600}>
            Min DIR
          </Typography>
          <Typography variant="h6" fontWeight={700}>
            {data.min_dir.toFixed(3)}
          </Typography>
        </Box>
        <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'grey.50', borderRadius: 2 }}>
          <Typography variant="caption" color="text.secondary" fontWeight={600}>
            Max DIR
          </Typography>
          <Typography variant="h6" fontWeight={700}>
            {data.max_dir.toFixed(3)}
          </Typography>
        </Box>
        <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'grey.50', borderRadius: 2 }}>
          <Typography variant="caption" color="text.secondary" fontWeight={600}>
            Alerts
          </Typography>
          <Typography variant="h6" fontWeight={700} color="error.main">
            {data.alert_count}/{data.data_points}
          </Typography>
        </Box>
      </Box>

      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis
            dataKey="check"
            label={{ value: 'Check Number', position: 'insideBottom', offset: -5 }}
            stroke="#666"
          />
          <YAxis
            label={{ value: 'DIR Value', angle: -90, position: 'insideLeft' }}
            domain={[0, 1]}
            stroke="#666"
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              border: '1px solid #ddd',
              borderRadius: 8,
            }}
            formatter={(value: number) => [value.toFixed(3), 'DIR']}
          />
          <ReferenceLine
            y={0.8}
            stroke="#ef4444"
            strokeDasharray="5 5"
            label={{ value: 'EEOC 80% Rule', position: 'right', fill: '#ef4444', fontWeight: 600 }}
          />
          <Line
            type="monotone"
            dataKey="dir"
            stroke="#6366f1"
            strokeWidth={3}
            dot={{ fill: '#6366f1', r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>

      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2, textAlign: 'center' }}>
        Last {data.data_points} fairness checks • Auto-refreshes every 30 seconds
      </Typography>
    </Paper>
  );
}
