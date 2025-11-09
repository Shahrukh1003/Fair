import {
  Box,
  Grid,
  Typography,
  Paper,
  Button,
  Stack,
  Divider,
  TextField,
  Alert,
  List,
  ListItem,
  ListItemText,
  Chip,
} from '@mui/material';
import {
  Webhook,
  Settings,
  Send,
  Check,
} from '@mui/icons-material';
import { useState } from 'react';
import apiClient from '../api/client';

export function AdminPage() {
  const [webhookUrl, setWebhookUrl] = useState('');
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);
  const [loading, setLoading] = useState(false);

  const handleTestWebhook = async () => {
    if (!webhookUrl) {
      setTestResult({ success: false, message: 'Please enter a webhook URL' });
      return;
    }

    setLoading(true);
    try {
      await apiClient.post('/webhooks/test', {
        webhook_url: webhookUrl,
      });
      setTestResult({ success: true, message: 'Webhook test successful!' });
    } catch (error: any) {
      setTestResult({
        success: false,
        message: error.response?.data?.message || 'Webhook test failed',
      });
    } finally {
      setLoading(false);
    }
  };

  const models = [
    {
      name: 'Loan Approval Model',
      version: 'v1.0',
      status: 'active',
      accuracy: '74.6%',
      lastTrained: '2025-11-09',
    },
  ];

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1, color: 'primary.main' }}>
          Administration
        </Typography>
        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
          System configuration and model management
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={6}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
              <Box
                sx={{
                  p: 1.5,
                  borderRadius: 2,
                  bgcolor: 'rgba(99, 102, 241, 0.1)',
                  display: 'flex',
                }}
              >
                <Webhook sx={{ color: 'primary.main' }} />
              </Box>
              <Typography variant="h6" sx={{ fontWeight: 700 }}>
                Webhook Configuration
              </Typography>
            </Box>

            <Stack spacing={2}>
              <TextField
                fullWidth
                label="Webhook URL"
                placeholder="https://hooks.slack.com/services/..."
                value={webhookUrl}
                onChange={(e) => setWebhookUrl(e.target.value)}
                helperText="Enter your Slack webhook URL or use webhook.site for testing"
              />
              <Button
                variant="contained"
                startIcon={<Send />}
                onClick={handleTestWebhook}
                disabled={loading}
                sx={{
                  background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
                }}
              >
                {loading ? 'Sending...' : 'Test Webhook'}
              </Button>
              {testResult && (
                <Alert severity={testResult.success ? 'success' : 'error'}>
                  {testResult.message}
                </Alert>
              )}
            </Stack>

            <Divider sx={{ my: 3 }} />

            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              <strong>How to set up webhooks:</strong>
            </Typography>
            <Typography variant="caption" color="text.secondary" component="div" sx={{ lineHeight: 1.8 }}>
              1. For Slack: Create an incoming webhook in your Slack workspace settings
              <br />
              2. For testing: Use <a href="https://webhook.site" target="_blank" rel="noopener noreferrer">webhook.site</a> to get a test URL
              <br />
              3. Paste the URL above and click "Test Webhook"
              <br />
              4. When bias is detected, alerts will be sent automatically
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} lg={6}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
              <Box
                sx={{
                  p: 1.5,
                  borderRadius: 2,
                  bgcolor: 'rgba(139, 92, 246, 0.1)',
                  display: 'flex',
                }}
              >
                <Settings sx={{ color: '#8b5cf6' }} />
              </Box>
              <Typography variant="h6" sx={{ fontWeight: 700 }}>
                Model Registry
              </Typography>
            </Box>

            <List>
              {models.map((model, idx) => (
                <ListItem
                  key={idx}
                  sx={{
                    border: '1px solid rgba(0, 0, 0, 0.08)',
                    borderRadius: 2,
                    mb: 2,
                    bgcolor: 'rgba(0, 0, 0, 0.02)',
                  }}
                >
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                        <Typography variant="body1" fontWeight={600}>
                          {model.name}
                        </Typography>
                        <Chip
                          label={model.status}
                          size="small"
                          color="success"
                          icon={<Check fontSize="small" />}
                        />
                      </Box>
                    }
                    secondary={
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="caption" color="text.secondary" display="block">
                          Version: {model.version} • Accuracy: {model.accuracy}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Last trained: {model.lastTrained}
                        </Typography>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>

            <Button
              variant="outlined"
              fullWidth
              sx={{ mt: 2 }}
              disabled
            >
              Add New Model (Coming Soon)
            </Button>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
