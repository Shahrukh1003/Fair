import { Box, Paper, Typography, Button, Stack, CircularProgress, Alert } from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import TableChartIcon from '@mui/icons-material/TableChart';
import VerifiedIcon from '@mui/icons-material/Verified';
import { useExportReport, useExportCSV } from '../hooks/useFairnessV3';
import { useState } from 'react';

interface ComplianceReportsProps {
  nSamples: number;
  driftLevel: number;
}

export function ComplianceReports({ nSamples, driftLevel }: ComplianceReportsProps) {
  const exportReport = useExportReport();
  const exportCSV = useExportCSV();
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  const handleExportPDF = async () => {
    try {
      setMessage(null);
      await exportReport.mutateAsync({ nSamples, driftLevel });
      setMessage({ type: 'success', text: 'PDF compliance report downloaded successfully!' });
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to generate PDF report. Ensure you have auditor/admin access.' });
    }
  };

  const handleExportCSV = async () => {
    try {
      setMessage(null);
      await exportCSV.mutateAsync({ nSamples, driftLevel });
      setMessage({ type: 'success', text: 'CSV data export downloaded successfully!' });
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to export CSV data. Ensure you have auditor/admin access.' });
    }
  };

  return (
    <Paper
      elevation={3}
      sx={{
        p: 4,
        background: 'linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(243,244,246,0.95) 100%)',
        borderRadius: 4,
        border: '2px solid',
        borderColor: 'primary.light',
      }}
    >
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
          <VerifiedIcon sx={{ fontSize: 32, color: 'primary.main' }} />
          <Typography variant="h5" sx={{ fontWeight: 700, color: 'primary.main' }}>
            Enterprise Compliance Reports
          </Typography>
        </Box>
        <Typography variant="body2" color="text.secondary">
          Generate regulatory compliance reports and export fairness data
        </Typography>
      </Box>

      {message && (
        <Alert severity={message.type} sx={{ mb: 3 }} onClose={() => setMessage(null)}>
          {message.text}
        </Alert>
      )}

      <Stack spacing={2.5}>
        <ReportCard
          title="PDF Compliance Report"
          description="Comprehensive fairness audit report with all 5 metrics, visualizations, and regulatory compliance summary. Suitable for regulators and stakeholders."
          icon={<PictureAsPdfIcon sx={{ fontSize: 48, color: 'error.main' }} />}
          buttonText="Download PDF Report"
          buttonColor="error"
          isLoading={exportReport.isPending}
          onDownload={handleExportPDF}
        />

        <ReportCard
          title="CSV Data Export"
          description="Raw fairness metrics data in CSV format for further analysis, integration with BI tools, or custom reporting workflows."
          icon={<TableChartIcon sx={{ fontSize: 48, color: 'success.main' }} />}
          buttonText="Export CSV Data"
          buttonColor="success"
          isLoading={exportCSV.isPending}
          onDownload={handleExportCSV}
        />
      </Stack>

      <Box sx={{ mt: 3, p: 2, bgcolor: 'info.lighter', borderRadius: 2, border: '1px solid', borderColor: 'info.light' }}>
        <Typography variant="caption" sx={{ color: 'info.dark', display: 'block', fontWeight: 600 }}>
          📋 REPORT CONTENTS
        </Typography>
        <Typography variant="body2" sx={{ color: 'info.dark', mt: 1 }}>
          • All 5 fairness metrics (DIR, SPD, EOD, AOD, Theil Index)<br />
          • Compliance scoring and risk assessment<br />
          • Feature attribution analysis<br />
          • AI-assisted remediation recommendations<br />
          • Audit trail and timestamp verification
        </Typography>
      </Box>
    </Paper>
  );
}

interface ReportCardProps {
  title: string;
  description: string;
  icon: React.ReactElement;
  buttonText: string;
  buttonColor: 'error' | 'success';
  isLoading: boolean;
  onDownload: () => void;
}

function ReportCard({ title, description, icon, buttonText, buttonColor, isLoading, onDownload }: ReportCardProps) {
  return (
    <Paper
      elevation={2}
      sx={{
        p: 3,
        border: '2px solid',
        borderColor: `${buttonColor}.light`,
        bgcolor: 'background.paper',
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 6,
        }
      }}
    >
      <Box sx={{ display: 'flex', gap: 3, alignItems: 'flex-start' }}>
        <Box sx={{
          p: 2,
          bgcolor: `${buttonColor}.lighter`,
          borderRadius: 3,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}>
          {icon}
        </Box>

        <Box sx={{ flex: 1 }}>
          <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>
            {title}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {description}
          </Typography>

          <Button
            variant="contained"
            color={buttonColor}
            startIcon={isLoading ? <CircularProgress size={20} color="inherit" /> : <DownloadIcon />}
            onClick={onDownload}
            disabled={isLoading}
            sx={{
              fontWeight: 700,
              px: 3,
              py: 1.5,
            }}
          >
            {isLoading ? 'Generating...' : buttonText}
          </Button>
        </Box>
      </Box>
    </Paper>
  );
}
