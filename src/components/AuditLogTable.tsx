import { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  Box,
} from '@mui/material';
import { formatPercent, formatDir, formatTimestamp } from '../utils/formatters';
import type { AuditLogEntry } from '../types/fairness';

interface AuditLogTableProps {
  entries: AuditLogEntry[];
}

export const AuditLogTable = ({ entries }: AuditLogTableProps) => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const handleChangePage = (_: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const paginatedEntries = entries.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);

  return (
    <Card elevation={3}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Compliance Audit Log
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Immutable record of all fairness checks for regulatory compliance
        </Typography>

        <TableContainer sx={{ mt: 2 }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Timestamp</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">DIR</TableCell>
                <TableCell align="right">Female Rate</TableCell>
                <TableCell align="right">Male Rate</TableCell>
                <TableCell align="right">Samples</TableCell>
                <TableCell align="right">Drift Level</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {paginatedEntries.map((entry, index) => (
                <TableRow key={`${entry.timestamp}-${index}`} hover>
                  <TableCell sx={{ fontSize: '0.75rem' }}>
                    {formatTimestamp(entry.timestamp)}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={entry.details.status}
                      color={entry.details.status === 'ALERT' ? 'error' : 'success'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Box
                      component="span"
                      sx={{ 
                        fontWeight: 'bold',
                        color: entry.details.dir < 0.8 ? 'error.main' : 'success.main'
                      }}
                    >
                      {formatDir(entry.details.dir)}
                    </Box>
                  </TableCell>
                  <TableCell align="right">{formatPercent(entry.details.female_rate)}</TableCell>
                  <TableCell align="right">{formatPercent(entry.details.male_rate)}</TableCell>
                  <TableCell align="right">{entry.details.n_samples}</TableCell>
                  <TableCell align="right">{(entry.details.drift_level * 100).toFixed(0)}%</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={entries.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </CardContent>
    </Card>
  );
};
