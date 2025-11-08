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
      <Alert severity="success" icon={false} sx={{ mb: 2 }}>
        <Typography variant="h6" gutterBottom>
          ✓ No Bias Detected
        </Typography>
        <Typography variant="body2">
          The system is operating fairly. The Disparate Impact Ratio ({scenario.dir.toFixed(3)}) meets or exceeds the EEOC 80% rule threshold.
        </Typography>
      </Alert>
    );
  }

  return (
    <Card elevation={3} sx={{ borderLeft: 4, borderColor: 'error.main' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <Typography variant="h6" color="error">
            ⚠ Bias Alert
          </Typography>
          <Chip label="Action Required" color="error" size="small" />
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
