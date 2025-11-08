export const formatPercent = (value: number): string => {
  return `${(value * 100).toFixed(1)}%`;
};

export const formatDir = (value: number): string => {
  return value.toFixed(3);
};

export const formatTimestamp = (timestamp: string): string => {
  const date = new Date(timestamp);
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
};

export const getAlertStatus = (dir: number, threshold: number = 0.8): 'success' | 'warning' | 'error' => {
  if (dir >= threshold) return 'success';
  if (dir >= threshold - 0.1) return 'warning';
  return 'error';
};

export const getAlertLabel = (dirAlert: boolean): string => {
  return dirAlert ? 'Bias Detected' : 'Fair';
};

export const getAlertColor = (dirAlert: boolean): 'error' | 'success' => {
  return dirAlert ? 'error' : 'success';
};
