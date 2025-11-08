import { Card, CardContent, Typography, Box, Tabs, Tab } from '@mui/material';
import { useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
  ReferenceLine,
} from 'recharts';
import type { FairnessScenario, AuditLogEntry } from '../types/fairness';

interface ChartsSectionProps {
  fairScenario: FairnessScenario;
  driftedScenario: FairnessScenario;
  auditHistory: AuditLogEntry[];
}

export const ChartsSection = ({ fairScenario, driftedScenario, auditHistory }: ChartsSectionProps) => {
  const [activeTab, setActiveTab] = useState(0);

  const approvalComparisonData = [
    {
      name: 'Fair Baseline',
      Female: fairScenario.female_rate * 100,
      Male: fairScenario.male_rate * 100,
    },
    {
      name: 'Current Test',
      Female: driftedScenario.female_rate * 100,
      Male: driftedScenario.male_rate * 100,
    },
  ];

  const dirTrendData = auditHistory
    .slice(-10)
    .reverse()
    .map((entry, index) => ({
      check: `#${index + 1}`,
      DIR: entry.details.dir,
      threshold: 0.8,
      timestamp: new Date(entry.timestamp).toLocaleTimeString(),
    }));

  return (
    <Card elevation={3}>
      <CardContent>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
            <Tab label="Approval Rate Comparison" />
            <Tab label="DIR Trend" />
          </Tabs>
        </Box>

        {activeTab === 0 && (
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Approval Rates by Gender
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={approvalComparisonData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis 
                  label={{ value: 'Approval Rate (%)', angle: -90, position: 'insideLeft' }}
                  domain={[0, 100]}
                />
                <RechartsTooltip 
                  formatter={(value: number) => `${value.toFixed(1)}%`}
                />
                <Legend />
                <Bar dataKey="Female" fill="#E91E63" />
                <Bar dataKey="Male" fill="#2196F3" />
                <ReferenceLine y={80} stroke="red" strokeDasharray="3 3" label="EEOC 80%" />
              </BarChart>
            </ResponsiveContainer>
            <Typography variant="caption" color="text.secondary" display="block" textAlign="center" mt={1}>
              The EEOC 80% rule requires the female approval rate to be at least 80% of the male rate
            </Typography>
          </Box>
        )}

        {activeTab === 1 && (
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Disparate Impact Ratio Over Time
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={dirTrendData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="check" />
                <YAxis 
                  label={{ value: 'DIR Value', angle: -90, position: 'insideLeft' }}
                  domain={[0, 1.2]}
                />
                <RechartsTooltip 
                  formatter={(value: number) => value.toFixed(3)}
                  labelFormatter={(label) => `Check ${label}`}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="DIR" 
                  stroke="#8884d8" 
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                />
                <ReferenceLine 
                  y={0.8} 
                  stroke="red" 
                  strokeDasharray="3 3" 
                  label={{ value: 'EEOC Threshold (0.8)', position: 'right' }}
                />
              </LineChart>
            </ResponsiveContainer>
            <Typography variant="caption" color="text.secondary" display="block" textAlign="center" mt={1}>
              DIR values below 0.8 (red line) indicate potential bias requiring investigation
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};
