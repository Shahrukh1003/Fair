import { Card, CardContent, Typography, Alert, Box, Chip, IconButton, Collapse } from '@mui/material';
import { useState } from 'react';
import LockIcon from '@mui/icons-material/Lock';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import type { FairnessScenario } from '../types/fairness';

interface AlertPanelProps {
  scenario: FairnessScenario;
}

export const AlertPanel = ({ scenario }: AlertPanelProps) => {
  const [showEncrypted, setShowEncrypted] = useState(false);

  if (!scenario.dir_alert) {
    return (
      <Alert 
        severity="success" 
        icon={false} 
        sx={{ 
          borderRadius: 4,
          border: '1px solid',
          borderColor: 'success.main',
          background: 'rgba(16, 185, 129, 0.1)',
          backdropFilter: 'blur(10px)',
          WebkitBackdropFilter: 'blur(10px)',
          boxShadow: '0 8px 32px rgba(16, 185, 129, 0.15)',
          animation: 'scaleIn 0.5s ease-out',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 12px 40px rgba(16, 185, 129, 0.2)',
          }
        }}
      >
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, color: 'success.dark' }}>
          ✓ No Bias Detected
        </Typography>
        <Typography variant="body2" sx={{ color: 'success.dark' }}>
          The system is operating fairly. The Disparate Impact Ratio ({scenario.dir.toFixed(3)}) meets or exceeds the EEOC 80% rule threshold.
        </Typography>
      </Alert>
    );
  }

  return (
    <Card 
      elevation={0}
      sx={{ 
        borderLeft: 6, 
        borderColor: 'error.main',
        borderRadius: 4,
        background: 'rgba(239, 68, 68, 0.1)',
        backdropFilter: 'blur(20px) saturate(180%)',
        WebkitBackdropFilter: 'blur(20px) saturate(180%)',
        border: '1px solid rgba(239, 68, 68, 0.3)',
        boxShadow: '0 8px 32px rgba(239, 68, 68, 0.15)',
        animation: 'scaleIn 0.5s ease-out',
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: '0 12px 40px rgba(239, 68, 68, 0.2)',
        }
      }}
    >
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
          <Typography variant="h6" color="error" sx={{ fontWeight: 700 }}>
            ⚠ Bias Alert
          </Typography>
          <Chip 
            label="Action Required" 
            color="error" 
            size="small"
            sx={{ fontWeight: 600 }}
          />
        </Box>

        {scenario.explanation && (
          <Alert severity="error" sx={{ mb: 2 }}>
            <Typography variant="body2" sx={{ whiteSpace: 'pre-line' }}>
              {scenario.explanation}
            </Typography>
          </Alert>
        )}

        {scenario.likely_causes && scenario.likely_causes.length > 0 && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Likely Causes:
            </Typography>
            <ul style={{ margin: 0, paddingLeft: 20 }}>
              {scenario.likely_causes.map((cause, index) => (
                <li key={index}>
                  <Typography variant="body2">{cause}</Typography>
                </li>
              ))}
            </ul>
          </Box>
        )}

        {scenario.encrypted_alert && (
          <Box>
            <Box 
              sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: 1, 
                cursor: 'pointer',
                '&:hover': { opacity: 0.8 }
              }}
              onClick={() => setShowEncrypted(!showEncrypted)}
            >
              <LockIcon fontSize="small" color="action" />
              <Typography variant="subtitle2">
                Encrypted Alert Token
              </Typography>
              <IconButton size="small">
                {showEncrypted ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </IconButton>
            </Box>
            <Collapse in={showEncrypted}>
              <Box 
                sx={{ 
                  mt: 1, 
                  p: 2, 
                  bgcolor: 'grey.100', 
                  borderRadius: 1,
                  fontFamily: 'monospace',
                  fontSize: '0.75rem',
                  wordBreak: 'break-all',
                  maxHeight: 100,
                  overflow: 'auto'
                }}
              >
                {scenario.encrypted_alert}
              </Box>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                This encrypted message is logged in the compliance audit trail for regulatory review.
              </Typography>
            </Collapse>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};
