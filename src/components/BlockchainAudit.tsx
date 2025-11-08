import { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  CircularProgress,
  Alert,
  Chip,
  Divider,
} from '@mui/material';
import VerifiedIcon from '@mui/icons-material/Verified';
import LinkIcon from '@mui/icons-material/Link';
import SearchIcon from '@mui/icons-material/Search';
import { fairnessApi } from '../api/client';
import type { BlockchainAnchor } from '../types/fairness';

export function BlockchainAudit() {
  const [hash, setHash] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BlockchainAnchor | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleVerify = async () => {
    if (!hash.trim()) {
      setError('Please enter a record hash');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const anchor = await fairnessApi.getBlockchainAnchor(hash.trim());
      setResult(anchor);
    } catch (err) {
      setError('Hash not found or verification failed');
      console.error('Verification error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper
      sx={{
        p: 3,
        background: 'rgba(255, 255, 255, 0.9)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(99, 102, 241, 0.2)',
        borderRadius: 3,
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 3 }}>
        <VerifiedIcon sx={{ fontSize: 32, color: 'primary.main' }} />
        <Box>
          <Typography variant="h6" fontWeight={700}>
            Blockchain Verification
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Verify compliance record integrity via blockchain anchoring
          </Typography>
        </Box>
      </Box>

      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <TextField
          fullWidth
          label="Record Hash"
          placeholder="Enter SHA256 hash to verify"
          value={hash}
          onChange={(e) => setHash(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleVerify()}
          disabled={loading}
          size="small"
        />
        <Button
          variant="contained"
          onClick={handleVerify}
          disabled={loading || !hash.trim()}
          startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SearchIcon />}
          sx={{ minWidth: 120 }}
        >
          Verify
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {result && (
        <Box
          sx={{
            p: 3,
            background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(255, 255, 255, 0.5) 100%)',
            border: '2px solid #10b981',
            borderRadius: 3,
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <VerifiedIcon sx={{ color: 'success.main', fontSize: 28 }} />
            <Typography variant="subtitle1" fontWeight={700} color="success.main">
              Anchor Verified ✓
            </Typography>
          </Box>

          <Divider sx={{ my: 2 }} />

          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Box>
              <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                Transaction ID
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="body2" fontWeight={600} sx={{ fontFamily: 'monospace', wordBreak: 'break-all' }}>
                  {result.tx_id}
                </Typography>
              </Box>
            </Box>

            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Box sx={{ flex: 1, minWidth: 150 }}>
                <Typography variant="caption" color="text.secondary" display="block">
                  Network
                </Typography>
                <Chip label={result.network} size="small" color="primary" sx={{ mt: 0.5 }} />
              </Box>
              <Box sx={{ flex: 1, minWidth: 150 }}>
                <Typography variant="caption" color="text.secondary" display="block">
                  Block Number
                </Typography>
                <Typography variant="body2" fontWeight={600} sx={{ mt: 0.5 }}>
                  #{result.block_number.toLocaleString()}
                </Typography>
              </Box>
              <Box sx={{ flex: 1, minWidth: 150 }}>
                <Typography variant="caption" color="text.secondary" display="block">
                  Status
                </Typography>
                <Chip label={result.status} size="small" color="success" sx={{ mt: 0.5 }} />
              </Box>
            </Box>

            <Box>
              <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                Model
              </Typography>
              <Typography variant="body2" fontWeight={600}>
                {result.model_name}
              </Typography>
            </Box>

            <Box>
              <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                Timestamp
              </Typography>
              <Typography variant="body2" fontWeight={600}>
                {new Date(result.timestamp).toLocaleString()}
              </Typography>
            </Box>

            {result.metadata.alert && (
              <Alert severity="warning" icon={<WarningAmberIcon />} sx={{ mt: 1 }}>
                This record corresponds to a fairness alert (Record ID: {result.metadata.db_record_id})
              </Alert>
            )}

            <Button
              fullWidth
              variant="outlined"
              startIcon={<LinkIcon />}
              onClick={() => window.open(result.explorer_url, '_blank')}
              sx={{ mt: 1 }}
            >
              View on Block Explorer
            </Button>
          </Box>
        </Box>
      )}

      {!result && !error && (
        <Box sx={{ textAlign: 'center', py: 3, color: 'text.secondary' }}>
          <Typography variant="body2">
            Enter a record hash from the audit log to verify its blockchain anchor
          </Typography>
        </Box>
      )}
    </Paper>
  );
}

import WarningAmberIcon from '@mui/icons-material/WarningAmber';
