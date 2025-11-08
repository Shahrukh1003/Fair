import { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Slider,
  Button,
  Stack,
  FormControlLabel,
  Switch,
  Tooltip,
  IconButton,
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import RefreshIcon from '@mui/icons-material/Refresh';
import InfoIcon from '@mui/icons-material/Info';

interface ControlPanelProps {
  onRunCheck: (nSamples: number, driftLevel: number) => void;
  isLoading: boolean;
  autoRefresh: boolean;
  onAutoRefreshToggle: (enabled: boolean) => void;
}

export const ControlPanel = ({ onRunCheck, isLoading, autoRefresh, onAutoRefreshToggle }: ControlPanelProps) => {
  const [nSamples, setNSamples] = useState(1000);
  const [driftLevel, setDriftLevel] = useState(0.5);

  const handleRunCheck = () => {
    onRunCheck(nSamples, driftLevel);
  };

  return (
    <Card elevation={3}>
      <CardContent>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <PlayArrowIcon color="primary" />
          Fairness Check Controls
        </Typography>
        
        <Stack spacing={3} sx={{ mt: 2 }}>
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <Typography variant="body2" fontWeight="medium">
                Number of Loan Applications: {nSamples}
              </Typography>
              <Tooltip title="How many synthetic loan applications to generate for testing">
                <IconButton size="small">
                  <InfoIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
            <Slider
              value={nSamples}
              onChange={(_, value) => setNSamples(value as number)}
              min={100}
              max={2000}
              step={100}
              marks={[
                { value: 100, label: '100' },
                { value: 1000, label: '1000' },
                { value: 2000, label: '2000' },
              ]}
              valueLabelDisplay="auto"
              disabled={isLoading}
            />
          </Box>

          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <Typography variant="body2" fontWeight="medium">
                Bias Drift Level: {(driftLevel * 100).toFixed(0)}%
              </Typography>
              <Tooltip title="How much bias to inject into the data. 0% = fair, 100% = maximum bias">
                <IconButton size="small">
                  <InfoIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
            <Slider
              value={driftLevel}
              onChange={(_, value) => setDriftLevel(value as number)}
              min={0}
              max={1}
              step={0.1}
              marks={[
                { value: 0, label: 'Fair' },
                { value: 0.5, label: 'Moderate' },
                { value: 1, label: 'High' },
              ]}
              valueLabelDisplay="auto"
              valueLabelFormat={(value) => `${(value * 100).toFixed(0)}%`}
              disabled={isLoading}
              sx={{
                '& .MuiSlider-markLabel': { fontSize: '0.75rem' },
              }}
            />
          </Box>

          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <Button
              variant="contained"
              size="large"
              startIcon={<PlayArrowIcon />}
              onClick={handleRunCheck}
              disabled={isLoading}
              fullWidth
              sx={{ flexGrow: 1 }}
            >
              {isLoading ? 'Running Check...' : 'Run Fairness Check'}
            </Button>
            
            <Tooltip title="Automatically refresh every 10 seconds">
              <FormControlLabel
                control={
                  <Switch
                    checked={autoRefresh}
                    onChange={(e) => onAutoRefreshToggle(e.target.checked)}
                    icon={<RefreshIcon />}
                    checkedIcon={<RefreshIcon />}
                  />
                }
                label="Auto"
                labelPlacement="bottom"
              />
            </Tooltip>
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
};
