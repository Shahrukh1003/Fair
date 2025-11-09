import { useState } from 'react';
import {
  Box,
  Grid,
  Typography,
  Paper,
  Stack,
  TextField,
  InputAdornment,
} from '@mui/material';
import { Search } from '@mui/icons-material';
import { AuditLogTable } from '../components/AuditLogTable';
import { BlockchainAudit } from '../components/BlockchainAudit';
import { ComplianceReports } from '../components/ComplianceReports';
import { useAuditHistory } from '../hooks/useFairnessMonitor';

export function CompliancePage() {
  const [searchTerm, setSearchTerm] = useState('');
  const { data: auditHistory } = useAuditHistory(50, true);

  const filteredAuditHistory = auditHistory?.filter((entry: any) => {
    if (!searchTerm) return true;
    const searchLower = searchTerm.toLowerCase();
    return (
      entry.record_id?.toLowerCase().includes(searchLower) ||
      entry.model_name?.toLowerCase().includes(searchLower) ||
      entry.alert_status?.toLowerCase().includes(searchLower)
    );
  });

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1, color: 'primary.main' }}>
          Compliance & Audit
        </Typography>
        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
          Audit trails, blockchain verification, and compliance reporting
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <Stack spacing={3}>
            <Paper
              sx={{
                p: 3,
                transition: 'all 0.3s ease',
                '&:hover': {
                  boxShadow: '0 12px 40px rgba(0, 0, 0, 0.12)',
                },
              }}
            >
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  Audit Log
                </Typography>
                <TextField
                  size="small"
                  placeholder="Search logs..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Search fontSize="small" />
                      </InputAdornment>
                    ),
                  }}
                  sx={{ width: 300 }}
                />
              </Box>
              {filteredAuditHistory && filteredAuditHistory.length > 0 ? (
                <AuditLogTable entries={filteredAuditHistory} />
              ) : (
                <Box
                  sx={{
                    p: 8,
                    textAlign: 'center',
                    bgcolor: 'rgba(0, 0, 0, 0.02)',
                    borderRadius: 2,
                  }}
                >
                  <Typography variant="body2" color="text.secondary">
                    {searchTerm ? 'No matching audit logs found' : 'No audit logs available. Run a fairness check to generate logs.'}
                  </Typography>
                </Box>
              )}
            </Paper>

            <BlockchainAudit />
          </Stack>
        </Grid>

        <Grid item xs={12} lg={4}>
          <ComplianceReports nSamples={1000} driftLevel={0.5} />
        </Grid>
      </Grid>
    </Box>
  );
}
