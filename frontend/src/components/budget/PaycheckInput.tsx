/**
 * Paycheck input component for creating pay periods.
 */

import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  Grid,
  Alert,
  InputAdornment,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  SelectChangeEvent,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { AttachMoney, CalendarToday, Schedule } from '@mui/icons-material';
import { addDays, format, endOfMonth } from 'date-fns';
import { createPayPeriod } from '../../services/budget.service';
import { PayPeriodCreate, PayFrequency } from '../../types/budget';
import { formatCurrency } from '../../utils/formatters';

interface PaycheckInputProps {
  onPayPeriodCreated: (payPeriod: any) => void;
  currentPayPeriod?: any;
}

export const PaycheckInput: React.FC<PaycheckInputProps> = ({ onPayPeriodCreated }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    totalIncome: '',
    startDate: new Date(),
    frequency: 'bi_weekly' as PayFrequency,
  });

  // Calculate end date based on frequency
  const calculateEndDate = (startDate: Date, frequency: PayFrequency): Date => {
    switch (frequency) {
      case 'weekly':
        return addDays(startDate, 6); // 7-day period
      case 'bi_weekly':
        return addDays(startDate, 13); // 14-day period
      case 'monthly':
        return endOfMonth(startDate); // End of the month
      default:
        return addDays(startDate, 13);
    }
  };

  const endDate = calculateEndDate(formData.startDate, formData.frequency);

  const handleIncomeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    // Only allow numbers and decimal point
    if (value === '' || /^\d*\.?\d*$/.test(value)) {
      setFormData(prev => ({ ...prev, totalIncome: value }));
      setError(null);
    }
  };

  const handleStartDateChange = (newDate: Date | null) => {
    if (newDate) {
      setFormData(prev => ({
        ...prev,
        startDate: newDate,
      }));
    }
  };

  const handleFrequencyChange = (event: SelectChangeEvent<PayFrequency>) => {
    setFormData(prev => ({
      ...prev,
      frequency: event.target.value as PayFrequency,
    }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    
    if (!formData.totalIncome || parseFloat(formData.totalIncome) <= 0) {
      setError('Please enter a valid income amount');
      return;
    }

    // No need to validate end date since it's calculated automatically

    setIsLoading(true);

    try {
      const payPeriodData: PayPeriodCreate = {
        start_date: format(formData.startDate, 'yyyy-MM-dd'),
        frequency: formData.frequency,
        total_income: formData.totalIncome,
      };

      const newPayPeriod = await createPayPeriod(payPeriodData);
      onPayPeriodCreated(newPayPeriod);
      
      // Reset form
      setFormData({
        totalIncome: '',
        startDate: new Date(),
        frequency: 'bi_weekly' as PayFrequency,
      });
    } catch (err: any) {
      setError(err.message || 'Failed to create pay period');
    } finally {
      setIsLoading(false);
    }
  };

  const incomeValue = parseFloat(formData.totalIncome) || 0;

  return (
    <Paper elevation={2} sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom color="primary">
        New Pay Period
      </Typography>
      
      <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
        Create a new budget period with your preferred pay frequency
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <LocalizationProvider dateAdapter={AdapterDateFns}>
        <Box component="form" onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                required
                fullWidth
                label="Paycheck Amount"
                value={formData.totalIncome}
                onChange={handleIncomeChange}
                disabled={isLoading}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <AttachMoney color="action" />
                    </InputAdornment>
                  ),
                }}
                helperText={incomeValue > 0 ? `Total: ${formatCurrency(incomeValue)}` : 'Enter your total income for this period'}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <FormControl fullWidth required disabled={isLoading}>
                <InputLabel>Pay Frequency</InputLabel>
                <Select
                  value={formData.frequency}
                  label="Pay Frequency"
                  onChange={handleFrequencyChange}
                  startAdornment={
                    <InputAdornment position="start">
                      <Schedule color="action" />
                    </InputAdornment>
                  }
                >
                  <MenuItem value="weekly">Weekly (7 days)</MenuItem>
                  <MenuItem value="bi_weekly">Bi-Weekly (14 days)</MenuItem>
                  <MenuItem value="monthly">Monthly</MenuItem>
                </Select>
                <FormHelperText>
                  How often you receive your paycheck
                </FormHelperText>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <DatePicker
                label="Start Date"
                value={formData.startDate}
                onChange={handleStartDateChange}
                disabled={isLoading}
                slotProps={{
                  textField: {
                    fullWidth: true,
                    required: true,
                    InputProps: {
                      startAdornment: (
                        <InputAdornment position="start">
                          <CalendarToday color="action" />
                        </InputAdornment>
                      ),
                    },
                  },
                }}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <DatePicker
                label="End Date (Auto-calculated)"
                value={endDate}
                disabled={true}
                slotProps={{
                  textField: {
                    fullWidth: true,
                    helperText: `Period ends on ${format(endDate, 'MMM dd, yyyy')}`,
                    InputProps: {
                      style: { backgroundColor: '#f5f5f5' },
                    },
                  },
                }}
              />
            </Grid>
          </Grid>

          <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              type="submit"
              variant="contained"
              disabled={!formData.totalIncome || isLoading}
              sx={{ minWidth: 150 }}
            >
              {isLoading ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                'Create Pay Period'
              )}
            </Button>
          </Box>
        </Box>
      </LocalizationProvider>
    </Paper>
  );
};