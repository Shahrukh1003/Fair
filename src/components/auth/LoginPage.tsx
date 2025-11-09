import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  InputAdornment,
  IconButton,
  Checkbox,
  FormControlLabel,
  Stack,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Assessment,
  Security,
  Analytics,
  VerifiedUser,
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';

export function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(username, password);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Invalid username or password');
    } finally {
      setLoading(false);
    }
  };

  const demoCredentials = [
    { username: 'admin', password: 'admin123', role: 'Admin', desc: 'Full system access' },
    { username: 'auditor', password: 'auditor123', role: 'Auditor', desc: 'Audit logs & reports' },
    { username: 'monitor', password: 'monitor123', role: 'Monitor', desc: 'View-only access' },
  ];

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)',
        position: 'relative',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: '-50%',
          left: '-50%',
          width: '200%',
          height: '200%',
          background: `
            radial-gradient(circle at 20% 50%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 40% 80%, rgba(16, 185, 129, 0.15) 0%, transparent 50%)
          `,
          animation: 'gradientFloat 20s ease infinite',
        },
      }}
    >
      <Container maxWidth="lg">
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
            gap: 4,
            alignItems: 'center',
          }}
        >
          <Box
            sx={{
              display: { xs: 'none', md: 'block' },
              position: 'relative',
              zIndex: 1,
            }}
          >
            <Box sx={{ mb: 6 }}>
              <Box
                sx={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 2,
                  mb: 3,
                }}
              >
                <Box
                  sx={{
                    background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                    p: 2,
                    borderRadius: 3,
                    display: 'flex',
                    boxShadow: '0 8px 32px rgba(99, 102, 241, 0.4)',
                  }}
                >
                  <Assessment sx={{ fontSize: 40, color: 'white' }} />
                </Box>
                <Typography
                  variant="h3"
                  sx={{
                    fontWeight: 900,
                    background: 'linear-gradient(135deg, #ffffff 0%, #a5b4fc 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    letterSpacing: '-0.03em',
                  }}
                >
                  BiasCheck
                </Typography>
              </Box>
              <Typography
                variant="h5"
                sx={{
                  color: 'rgba(255, 255, 255, 0.9)',
                  fontWeight: 600,
                  mb: 2,
                  letterSpacing: '-0.02em',
                }}
              >
                Enterprise AI Fairness Governance
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  color: 'rgba(255, 255, 255, 0.7)',
                  lineHeight: 1.8,
                  mb: 4,
                }}
              >
                Production-grade monitoring with real ML models, predictive drift detection,
                and comprehensive compliance reporting for regulated industries.
              </Typography>
            </Box>

            <Stack spacing={3}>
              {[
                { icon: Security, text: 'JWT Authentication & Role-Based Access' },
                { icon: Analytics, text: '5 Fairness Metrics + Drift Prediction' },
                { icon: VerifiedUser, text: 'Blockchain-Verified Audit Trail' },
              ].map((item, idx) => (
                <Box
                  key={idx}
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 2,
                    p: 2,
                    background: 'rgba(255, 255, 255, 0.05)',
                    backdropFilter: 'blur(10px)',
                    borderRadius: 2,
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                  }}
                >
                  <Box
                    sx={{
                      bgcolor: 'rgba(99, 102, 241, 0.2)',
                      p: 1.5,
                      borderRadius: 2,
                      display: 'flex',
                    }}
                  >
                    <item.icon sx={{ color: '#818cf8' }} />
                  </Box>
                  <Typography
                    variant="body2"
                    sx={{
                      color: 'rgba(255, 255, 255, 0.9)',
                      fontWeight: 500,
                    }}
                  >
                    {item.text}
                  </Typography>
                </Box>
              ))}
            </Stack>
          </Box>

          <Paper
            elevation={24}
            sx={{
              p: 5,
              borderRadius: 4,
              background: 'rgba(255, 255, 255, 0.98)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(99, 102, 241, 0.1)',
              position: 'relative',
              zIndex: 1,
            }}
          >
            <Typography
              variant="h4"
              sx={{
                fontWeight: 700,
                mb: 1,
                color: 'primary.main',
                letterSpacing: '-0.02em',
              }}
            >
              Welcome Back
            </Typography>
            <Typography
              variant="body2"
              sx={{
                color: 'text.secondary',
                mb: 4,
              }}
            >
              Sign in to access your fairness monitoring dashboard
            </Typography>

            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit}>
              <TextField
                fullWidth
                label="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                margin="normal"
                required
                autoFocus
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="Password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                margin="normal"
                required
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowPassword(!showPassword)}
                        edge="end"
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
                sx={{ mb: 2 }}
              />

              <FormControlLabel
                control={
                  <Checkbox
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                  />
                }
                label="Remember me"
                sx={{ mb: 3 }}
              />

              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                disabled={loading}
                sx={{
                  py: 1.5,
                  mb: 3,
                  background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #4f46e5 0%, #4338ca 100%)',
                  },
                }}
              >
                {loading ? 'Signing in...' : 'Sign In'}
              </Button>

              <Box
                sx={{
                  p: 3,
                  bgcolor: 'rgba(99, 102, 241, 0.05)',
                  borderRadius: 2,
                  border: '1px solid rgba(99, 102, 241, 0.1)',
                }}
              >
                <Typography
                  variant="caption"
                  sx={{
                    color: 'text.secondary',
                    fontWeight: 600,
                    mb: 1.5,
                    display: 'block',
                  }}
                >
                  DEMO CREDENTIALS
                </Typography>
                <Stack spacing={1}>
                  {demoCredentials.map((cred, idx) => (
                    <Box
                      key={idx}
                      sx={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        p: 1.5,
                        bgcolor: 'white',
                        borderRadius: 1,
                        border: '1px solid rgba(0, 0, 0, 0.05)',
                      }}
                    >
                      <Box>
                        <Typography
                          variant="caption"
                          sx={{
                            fontWeight: 700,
                            color: 'primary.main',
                            display: 'block',
                          }}
                        >
                          {cred.role}
                        </Typography>
                        <Typography
                          variant="caption"
                          sx={{
                            color: 'text.secondary',
                            fontSize: '0.7rem',
                          }}
                        >
                          {cred.desc}
                        </Typography>
                      </Box>
                      <Typography
                        variant="caption"
                        sx={{
                          fontFamily: 'monospace',
                          bgcolor: 'rgba(0, 0, 0, 0.05)',
                          px: 1.5,
                          py: 0.5,
                          borderRadius: 1,
                          fontSize: '0.75rem',
                        }}
                      >
                        {cred.username} / {cred.password}
                      </Typography>
                    </Box>
                  ))}
                </Stack>
              </Box>
            </Box>
          </Paper>
        </Box>
      </Container>

      <style>
        {`
          @keyframes gradientFloat {
            0%, 100% { transform: translate(0, 0) rotate(0deg); }
            33% { transform: translate(50px, -50px) rotate(120deg); }
            66% { transform: translate(-50px, 50px) rotate(240deg); }
          }
        `}
      </style>
    </Box>
  );
}
