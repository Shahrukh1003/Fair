import { useState, useEffect } from 'react';
import {
  Box,
  Container,
  AppBar,
  Toolbar,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Snackbar,
  Stack,
  IconButton,
  Menu,
  MenuItem,
} from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import AssessmentIcon from '@mui/icons-material/Assessment';
import LogoutIcon from '@mui/icons-material/Logout';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { ControlPanel } from './components/ControlPanel';
import { MetricsOverview } from './components/MetricsOverview';
import { AlertPanel } from './components/AlertPanel';
import { ChartsSection } from './components/ChartsSection';
import { AuditLogTable } from './components/AuditLogTable';
import { Login } from './components/Login';
import { FairnessTrend } from './components/FairnessTrend';
import { PreAlertPanel } from './components/PreAlertPanel';
import { BlockchainAudit } from './components/BlockchainAudit';
import { useMonitorMutation, useAuditHistory, useHealthCheck } from './hooks/useFairnessMonitor';
import { authUtils } from './api/client';
import type { FairnessCheckResponse } from './types/fairness';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#0f172a', // Deep slate for professional look
      light: '#334155',
      dark: '#020617',
    },
    secondary: {
      main: '#6366f1', // Indigo accent
      light: '#818cf8',
      dark: '#4f46e5',
    },
    error: {
      main: '#ef4444',
      light: '#f87171',
      dark: '#dc2626',
    },
    warning: {
      main: '#f59e0b',
      light: '#fbbf24',
      dark: '#d97706',
    },
    success: {
      main: '#10b981',
      light: '#34d399',
      dark: '#059669',
    },
    info: {
      main: '#3b82f6',
      light: '#60a5fa',
      dark: '#2563eb',
    },
    background: {
      default: '#f1f5f9',
      paper: '#ffffff',
    },
    text: {
      primary: '#0f172a',
      secondary: '#64748b',
    },
  },
  typography: {
    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif',
    h4: {
      fontWeight: 700,
      letterSpacing: '-0.02em',
    },
    h5: {
      fontWeight: 700,
      letterSpacing: '-0.01em',
    },
    h6: {
      fontWeight: 600,
      letterSpacing: '-0.01em',
    },
    subtitle1: {
      fontWeight: 500,
      letterSpacing: '-0.01em',
    },
    body1: {
      letterSpacing: '-0.01em',
    },
    button: {
      fontWeight: 600,
      textTransform: 'none',
      letterSpacing: '-0.01em',
    },
  },
  shape: {
    borderRadius: 16,
  },
  shadows: [
    'none',
    '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
    '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    '0 25px 50px -12px rgb(0 0 0 / 0.25)',
  ] as const,
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          padding: '10px 24px',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          },
        },
        contained: {
          background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
          '&:hover': {
            background: 'linear-gradient(135deg, #4f46e5 0%, #4338ca 100%)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
          border: '1px solid rgba(226, 232, 240, 0.8)',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          fontWeight: 600,
        },
      },
    },
  },
});

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
});

function DashboardContent() {
  const [lastResult, setLastResult] = useState<FairnessCheckResponse | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [nSamples, setNSamples] = useState(1000);
  const [driftLevel, setDriftLevel] = useState(0.5);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' | 'warning' | 'info' });
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const navigate = useNavigate();

  const monitorMutation = useMonitorMutation();
  const { data: health } = useHealthCheck();
  const userRole = authUtils.getRole();
  
  const isAuditorOrAdmin = userRole === 'auditor' || userRole === 'admin';
  const { data: auditHistory, refetch: refetchAudit } = useAuditHistory(20, isAuditorOrAdmin);

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    authUtils.clearAuth();
    navigate('/login');
    handleMenuClose();
  };

  const handleRunCheck = (samples: number, drift: number) => {
    setNSamples(samples);
    setDriftLevel(drift);

    monitorMutation.mutate(
      { n_samples: samples, drift_level: drift },
      {
        onSuccess: (data) => {
          setLastResult(data);
          if (isAuditorOrAdmin) {
            refetchAudit();
          }
          setSnackbar({
            open: true,
            message: data.drifted_scenario.dir_alert
              ? '🚨 Bias detected! Check the alert details below.'
              : '✅ Check complete. System is operating fairly.',
            severity: data.drifted_scenario.dir_alert ? 'error' : 'success',
          });
        },
        onError: (error) => {
          setSnackbar({
            open: true,
            message: `Error: ${error.message}. Make sure the Flask API is running on port 8000.`,
            severity: 'error',
          });
        },
      }
    );
  };

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        handleRunCheck(nSamples, driftLevel);
      }, 10000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, nSamples, driftLevel]);

  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column', 
      minHeight: '100vh', 
      bgcolor: 'background.default',
      backgroundImage: `
        radial-gradient(circle at 20% 50%, rgba(99, 102, 241, 0.08) 0%, transparent 50%),
        radial-gradient(circle at 80% 80%, rgba(16, 185, 129, 0.08) 0%, transparent 50%),
        radial-gradient(circle at 40% 20%, rgba(139, 92, 246, 0.05) 0%, transparent 40%)
      `,
      position: 'relative',
      '&::before': {
        content: '""',
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '400px',
        background: 'linear-gradient(180deg, rgba(99, 102, 241, 0.03) 0%, transparent 100%)',
        pointerEvents: 'none',
      }
    }}>
      <AppBar 
        position="static" 
        elevation={0} 
        sx={{ 
          background: 'rgba(15, 23, 42, 0.8)',
          backdropFilter: 'blur(20px) saturate(180%)',
          WebkitBackdropFilter: 'blur(20px) saturate(180%)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
          animation: 'slideInLeft 0.6s ease-out',
        }}
      >
        <Toolbar sx={{ py: 1.5, px: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexGrow: 1 }}>
            <Box sx={{ 
              background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
              p: 1.5, 
              borderRadius: 3,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 20px rgba(99, 102, 241, 0.5), 0 0 40px rgba(99, 102, 241, 0.2)',
              animation: 'float 3s ease-in-out infinite, glow 2s ease-in-out infinite',
              position: 'relative',
              '&::after': {
                content: '""',
                position: 'absolute',
                inset: -2,
                borderRadius: 3,
                background: 'linear-gradient(135deg, #6366f1, #8b5cf6, #6366f1)',
                backgroundSize: '200% 200%',
                animation: 'gradientShift 3s ease infinite',
                opacity: 0.3,
                filter: 'blur(8px)',
                zIndex: -1,
              }
            }}>
              <AssessmentIcon sx={{ fontSize: 32, color: 'white' }} />
            </Box>
            <Box>
              <Typography 
                variant="h5" 
                component="div" 
                sx={{ 
                  fontWeight: 900, 
                  letterSpacing: '-0.03em',
                  background: 'linear-gradient(135deg, #ffffff 0%, #a5b4fc 100%)',
                  backgroundSize: '200% 200%',
                  animation: 'gradientShift 4s ease infinite',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                  textShadow: '0 0 30px rgba(255, 255, 255, 0.3)',
                }}
              >
                FairLens
              </Typography>
              <Typography 
                variant="caption" 
                sx={{ 
                  color: 'rgba(255, 255, 255, 0.7)', 
                  display: 'block', 
                  mt: -0.5,
                  fontWeight: 500,
                  letterSpacing: '0.05em',
                  textTransform: 'uppercase',
                  fontSize: '0.7rem',
                }}
              >
                AI Fairness Monitoring Platform
              </Typography>
            </Box>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {health && (
              <Box sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1.5,
                background: 'rgba(16, 185, 129, 0.15)',
                backdropFilter: 'blur(10px)',
                WebkitBackdropFilter: 'blur(10px)',
                px: 3,
                py: 1,
                borderRadius: 3,
                boxShadow: '0 4px 20px rgba(16, 185, 129, 0.3)',
                border: '1px solid rgba(16, 185, 129, 0.3)',
                animation: 'slideInRight 0.6s ease-out',
                transition: 'all 0.3s ease',
                '&:hover': {
                  background: 'rgba(16, 185, 129, 0.25)',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 6px 25px rgba(16, 185, 129, 0.4)',
                }
              }}>
                <Box sx={{ 
                  width: 10, 
                  height: 10, 
                  borderRadius: '50%', 
                  bgcolor: '#10b981',
                  boxShadow: '0 0 15px rgba(16, 185, 129, 0.8), 0 0 30px rgba(16, 185, 129, 0.4)',
                  animation: 'pulse 2s infinite'
                }} />
                <Typography variant="body2" sx={{ fontWeight: 700, color: 'white', letterSpacing: '-0.01em' }}>
                  System Online
                </Typography>
              </Box>
            )}
            <IconButton
              onClick={handleMenuClick}
              sx={{
                color: 'white',
                bgcolor: 'rgba(255, 255, 255, 0.1)',
                '&:hover': {
                  bgcolor: 'rgba(255, 255, 255, 0.2)',
                },
              }}
            >
              <AccountCircleIcon />
            </IconButton>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleMenuClose}
              transformOrigin={{ horizontal: 'right', vertical: 'top' }}
              anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            >
              <MenuItem disabled>
                <Typography variant="caption" color="text.secondary">
                  Role: {userRole?.toUpperCase() || 'UNKNOWN'}
                </Typography>
              </MenuItem>
              <MenuItem onClick={handleLogout}>
                <LogoutIcon sx={{ mr: 1, fontSize: 20 }} />
                Logout
              </MenuItem>
            </Menu>
          </Box>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4, flexGrow: 1 }}>
        <Paper 
          elevation={0} 
          sx={{ 
            p: 3.5, 
            mb: 4, 
            background: 'rgba(255, 255, 255, 0.7)',
            backdropFilter: 'blur(20px) saturate(180%)',
            WebkitBackdropFilter: 'blur(20px) saturate(180%)',
            border: '1px solid rgba(99, 102, 241, 0.2)',
            borderRadius: 4,
            position: 'relative',
            overflow: 'hidden',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.08)',
            animation: 'fadeIn 0.8s ease-out',
            transition: 'all 0.3s ease',
            '&:hover': {
              transform: 'translateY(-4px)',
              boxShadow: '0 12px 40px rgba(0, 0, 0, 0.12)',
              border: '1px solid rgba(99, 102, 241, 0.4)',
            },
            '&::before': {
              content: '""',
              position: 'absolute',
              left: 0,
              top: 0,
              bottom: 0,
              width: '6px',
              background: 'linear-gradient(180deg, #6366f1 0%, #8b5cf6 100%)',
              boxShadow: '0 0 20px rgba(99, 102, 241, 0.5)',
            }
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
            <Box sx={{
              background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%)',
              p: 1.5,
              borderRadius: 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '1px solid rgba(99, 102, 241, 0.2)',
              boxShadow: '0 4px 12px rgba(99, 102, 241, 0.15)',
              animation: 'scaleIn 0.5s ease-out',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'scale(1.1) rotate(5deg)',
                boxShadow: '0 6px 20px rgba(99, 102, 241, 0.25)',
              }
            }}>
              <Typography sx={{ fontSize: '2rem', filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))' }}>⚖️</Typography>
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography 
                variant="subtitle1" 
                sx={{ 
                  fontWeight: 700, 
                  color: 'primary.main',
                  mb: 1,
                  letterSpacing: '-0.01em',
                }}
              >
                Ethical AI Monitoring Dashboard
              </Typography>
              <Typography 
                variant="body2" 
                sx={{ 
                  lineHeight: 1.8, 
                  color: 'text.secondary',
                  letterSpacing: '-0.01em',
                }}
              >
                This platform continuously monitors AI fairness in loan approval decisions using the <strong>EEOC 80% rule</strong>.
                A <strong>DIR (Disparate Impact Ratio)</strong> below 0.8 indicates potential bias.
                The system provides predictive alerts, tamper-proof audit trails, and actionable insights for compliance teams.
              </Typography>
            </Box>
          </Box>
        </Paper>

        <Box sx={{ 
          display: 'flex', 
          flexDirection: { xs: 'column', lg: 'row' }, 
          gap: 3,
          animation: 'fadeIn 1s ease-out',
        }}>
          <Box sx={{ 
            width: { xs: '100%', lg: '350px' }, 
            flexShrink: 0,
            animation: 'slideInLeft 0.8s ease-out',
          }}>
            <Stack spacing={3}>
              <ControlPanel
                onRunCheck={handleRunCheck}
                isLoading={monitorMutation.isPending}
                autoRefresh={autoRefresh}
                onAutoRefreshToggle={setAutoRefresh}
              />
              <FairnessTrend />
            </Stack>
          </Box>

          <Box sx={{ 
            flexGrow: 1,
            animation: 'slideInRight 0.8s ease-out',
          }}>
            <Stack spacing={3}>
              <PreAlertPanel />

              {monitorMutation.isPending && (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 200 }}>
                  <CircularProgress size={60} />
                  <Typography variant="h6" sx={{ ml: 2 }}>
                    Running fairness check...
                  </Typography>
                </Box>
              )}

              {monitorMutation.isError && (
                <Alert severity="error">
                  <Typography variant="body2">
                    Failed to connect to the API. Please ensure the Flask backend is running on port 8000.
                  </Typography>
                </Alert>
              )}

              {lastResult && !monitorMutation.isPending && (
                <>
                  <AlertPanel scenario={lastResult.drifted_scenario} />
                  <MetricsOverview scenario={lastResult.drifted_scenario} />
                  {lastResult.fair_scenario && (
                    <MetricsOverview scenario={lastResult.fair_scenario} isFair />
                  )}
                </>
              )}

              {!lastResult && !monitorMutation.isPending && (
                <Paper sx={{ p: 4, textAlign: 'center', bgcolor: 'grey.50' }}>
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    No fairness check has been run yet
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Use the controls on the left to configure and run your first fairness check
                  </Typography>
                </Paper>
              )}
            </Stack>
          </Box>
        </Box>

        {lastResult && (
          <Stack spacing={3} sx={{ mt: 3 }}>
            {isAuditorOrAdmin && auditHistory && auditHistory.length > 0 && (
              <>
                <ChartsSection
                  fairScenario={lastResult.fair_scenario}
                  driftedScenario={lastResult.drifted_scenario}
                  auditHistory={auditHistory}
                />
                <AuditLogTable entries={auditHistory} />
                <BlockchainAudit />
              </>
            )}
          </Stack>
        )}
      </Container>

      <Box
        component="footer"
        sx={{
          py: 4,
          px: 2,
          mt: 'auto',
          background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
          borderTop: '1px solid rgba(255, 255, 255, 0.1)',
        }}
      >
        <Container maxWidth="xl">
          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center', 
            flexWrap: 'wrap', 
            gap: 3 
          }}>
            <Box>
              <Typography 
                variant="body2" 
                sx={{ 
                  color: 'rgba(255, 255, 255, 0.9)',
                  fontWeight: 600,
                  mb: 0.5,
                }}
              >
                FairLens v2.0.0
              </Typography>
              <Typography 
                variant="caption" 
                sx={{ 
                  color: 'rgba(255, 255, 255, 0.6)',
                  display: 'block',
                }}
              >
                Ensuring Fair Lending Practices Through AI Monitoring
              </Typography>
            </Box>
            <Box sx={{ textAlign: 'right' }}>
              <Typography 
                variant="caption" 
                sx={{ 
                  color: 'rgba(255, 255, 255, 0.7)',
                  display: 'block',
                  mb: 0.5,
                }}
              >
                EEOC 80% Rule Compliance | Predictive Monitoring Active
              </Typography>
              <Typography 
                variant="caption" 
                sx={{ 
                  color: 'rgba(255, 255, 255, 0.5)',
                }}
              >
                © 2025 FairLens. Built for Ethical AI in Banking.
              </Typography>
            </Box>
          </Box>
        </Container>
      </Box>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          variant="filled"
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = authUtils.isAuthenticated();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardContent />
                </ProtectedRoute>
              }
            />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
