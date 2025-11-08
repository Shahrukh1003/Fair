import { useState } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import AssessmentIcon from '@mui/icons-material/Assessment';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import { fairnessApi, authUtils } from '../api/client';
import type { LoginRequest } from '../types/fairness';

export function Login() {
  const [role, setRole] = useState<'monitor' | 'auditor' | 'admin'>('monitor');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleLogin = async () => {
    setLoading(true);
    setError(null);

    try {
      const request: LoginRequest = { role };
      const response = await fairnessApi.login(request);
      
      authUtils.setToken(response.token);
      authUtils.setRole(response.role);
      
      navigate('/dashboard');
    } catch (err) {
      setError('Login failed. Please try again.');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        position: 'relative',
        '&::before': {
          content: '""',
          position: 'absolute',
          inset: 0,
          backgroundImage: `
            radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%)
          `,
        },
      }}
    >
      <Container maxWidth="sm">
        <Paper
          elevation={24}
          sx={{
            p: 5,
            borderRadius: 4,
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(20px)',
            boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
          }}
        >
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 4 }}>
            <Box
              sx={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                p: 2.5,
                borderRadius: 3,
                mb: 3,
                boxShadow: '0 8px 32px rgba(102, 126, 234, 0.4)',
              }}
            >
              <AssessmentIcon sx={{ fontSize: 48, color: 'white' }} />
            </Box>
            <Typography variant="h4" fontWeight={800} gutterBottom>
              FairLens
            </Typography>
            <Typography variant="subtitle1" color="text.secondary" textAlign="center">
              AI Fairness Monitoring Platform
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3, p: 2, bgcolor: 'info.light', borderRadius: 2 }}>
            <LockOutlinedIcon sx={{ color: 'info.dark' }} />
            <Typography variant="body2" color="info.dark" fontWeight={600}>
              Role-Based Access Control
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <FormControl fullWidth sx={{ mb: 3 }}>
            <InputLabel id="role-select-label">Select Role</InputLabel>
            <Select
              labelId="role-select-label"
              value={role}
              label="Select Role"
              onChange={(e) => setRole(e.target.value as 'monitor' | 'auditor' | 'admin')}
              disabled={loading}
            >
              <MenuItem value="monitor">
                <Box>
                  <Typography variant="body1" fontWeight={600}>Monitor</Typography>
                  <Typography variant="caption" color="text.secondary">
                    View fairness checks and metrics
                  </Typography>
                </Box>
              </MenuItem>
              <MenuItem value="auditor">
                <Box>
                  <Typography variant="body1" fontWeight={600}>Auditor</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Access audit history and compliance logs
                  </Typography>
                </Box>
              </MenuItem>
              <MenuItem value="admin">
                <Box>
                  <Typography variant="body1" fontWeight={600}>Administrator</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Full system access and configuration
                  </Typography>
                </Box>
              </MenuItem>
            </Select>
          </FormControl>

          <Button
            fullWidth
            variant="contained"
            size="large"
            onClick={handleLogin}
            disabled={loading}
            sx={{
              py: 1.5,
              fontSize: '1rem',
              fontWeight: 700,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #5568d3 0%, #6a4190 100%)',
                boxShadow: '0 8px 24px rgba(102, 126, 234, 0.4)',
              },
            }}
          >
            {loading ? <CircularProgress size={24} color="inherit" /> : 'Sign In'}
          </Button>

          <Box sx={{ mt: 4, pt: 3, borderTop: '1px solid', borderColor: 'divider' }}>
            <Typography variant="caption" color="text.secondary" textAlign="center" display="block">
              Production-Grade Ethical AI Monitoring
            </Typography>
            <Typography variant="caption" color="text.secondary" textAlign="center" display="block" mt={0.5}>
              EEOC 80% Rule Compliance • Blockchain Anchoring • Predictive Alerts
            </Typography>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
}
