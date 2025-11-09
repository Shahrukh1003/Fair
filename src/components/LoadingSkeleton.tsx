import { Skeleton, Card, CardContent, Box, Grid } from '@mui/material';

export function MetricCardSkeleton() {
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Skeleton variant="rectangular" width={56} height={56} sx={{ borderRadius: 2 }} />
        </Box>
        <Skeleton variant="text" width="60%" height={48} sx={{ mb: 1 }} />
        <Skeleton variant="text" width="80%" height={20} />
        <Skeleton variant="text" width="60%" height={16} />
      </CardContent>
    </Card>
  );
}

export function ChartSkeleton({ height = 300 }: { height?: number }) {
  return (
    <Card>
      <CardContent sx={{ p: 3 }}>
        <Skeleton variant="text" width="40%" height={32} sx={{ mb: 3 }} />
        <Skeleton variant="rectangular" width="100%" height={height} sx={{ borderRadius: 2 }} />
      </CardContent>
    </Card>
  );
}

export function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <Card>
      <CardContent sx={{ p: 3 }}>
        <Skeleton variant="text" width="30%" height={32} sx={{ mb: 3 }} />
        {Array.from({ length: rows }).map((_, i) => (
          <Skeleton
            key={i}
            variant="rectangular"
            width="100%"
            height={48}
            sx={{ borderRadius: 1, mb: 1 }}
          />
        ))}
      </CardContent>
    </Card>
  );
}

export function DashboardLoadingSkeleton() {
  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Skeleton variant="text" width="30%" height={40} sx={{ mb: 1 }} />
        <Skeleton variant="text" width="50%" height={24} />
      </Box>
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {[1, 2, 3, 4].map((i) => (
          <Grid item xs={12} sm={6} lg={3} key={i}>
            <MetricCardSkeleton />
          </Grid>
        ))}
      </Grid>
      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <ChartSkeleton height={300} />
        </Grid>
        <Grid item xs={12} lg={4}>
          <ChartSkeleton height={300} />
        </Grid>
      </Grid>
    </Box>
  );
}
