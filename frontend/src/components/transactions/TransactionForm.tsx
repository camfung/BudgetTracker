/**
 * Transaction form component for adding expenses.
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
} from '@mui/material';
import { AttachMoney, Description } from '@mui/icons-material';
import { createTransaction } from '../../services/transaction.service';
import { TransactionCreate } from '../../types/transaction';
import { PayPeriod } from '../../types/budget';
import { formatCurrency } from '../../utils/formatters';

interface TransactionFormProps {
  payPeriod: PayPeriod;
  onTransactionCreated: (transaction: any) => void;
}

export const TransactionForm: React.FC<TransactionFormProps> = ({
  payPeriod,
  onTransactionCreated,
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    budget_category_id: '',
    amount: '',
    description: '',
  });

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError(null);
  };

  const handleAmountChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    // Only allow numbers and decimal point
    if (value === '' || /^\d*\.?\d*$/.test(value)) {
      handleChange('amount', value);
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);

    if (!formData.budget_category_id || !formData.amount || !formData.description) {
      setError('Please fill in all fields');
      return;
    }

    if (parseFloat(formData.amount) <= 0) {
      setError('Amount must be greater than zero');
      return;
    }

    // Check if amount exceeds remaining budget
    const selectedCategory = payPeriod.budget_categories.find(
      cat => cat.id.toString() === formData.budget_category_id
    );
    
    if (selectedCategory) {
      const remainingAmount = parseFloat(selectedCategory.remaining_amount);
      const transactionAmount = parseFloat(formData.amount);
      
      if (transactionAmount > remainingAmount) {
        setError(
          `Amount exceeds remaining budget for ${selectedCategory.name}. Available: ${formatCurrency(remainingAmount)}`
        );
        return;
      }
    }

    setIsLoading(true);

    try {
      const transactionData: TransactionCreate = {
        budget_category_id: parseInt(formData.budget_category_id),
        amount: formData.amount,
        description: formData.description,
        source: 'manual',
      };

      const newTransaction = await createTransaction(transactionData);
      onTransactionCreated(newTransaction);
      
      // Reset form
      setFormData({
        budget_category_id: '',
        amount: '',
        description: '',
      });
    } catch (err: any) {
      setError(err.message || 'Failed to create transaction');
    } finally {
      setIsLoading(false);
    }
  };

  const selectedCategory = payPeriod.budget_categories.find(
    cat => cat.id.toString() === formData.budget_category_id
  );

  if (!payPeriod.budget_categories || payPeriod.budget_categories.length === 0) {
    return (
      <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h6" color="textSecondary">
          No Budget Categories
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Please create budget categories before adding transactions
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper elevation={2} sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom color="primary">
        Add Expense
      </Typography>
      
      <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
        Record a new expense from your budget
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Box component="form" onSubmit={handleSubmit}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <FormControl fullWidth required>
              <InputLabel>Budget Category</InputLabel>
              <Select
                value={formData.budget_category_id}
                label="Budget Category"
                onChange={(e) => handleChange('budget_category_id', e.target.value)}
                disabled={isLoading}
              >
                {payPeriod.budget_categories.map((category) => (
                  <MenuItem key={category.id} value={category.id.toString()}>
                    <Box>
                      <Typography variant="body1">
                        {category.name}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        Available: {formatCurrency(category.remaining_amount)}
                      </Typography>
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              required
              fullWidth
              label="Amount"
              value={formData.amount}
              onChange={handleAmountChange}
              disabled={isLoading}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <AttachMoney color="action" />
                  </InputAdornment>
                ),
              }}
              helperText={
                selectedCategory 
                  ? `Available: ${formatCurrency(selectedCategory.remaining_amount)}`
                  : 'Select a category to see available budget'
              }
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              required
              fullWidth
              label="Description"
              value={formData.description}
              onChange={(e) => handleChange('description', e.target.value)}
              disabled={isLoading}
              placeholder="e.g., Grocery shopping, Gas, etc."
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Description color="action" />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
        </Grid>

        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            type="submit"
            variant="contained"
            disabled={!formData.budget_category_id || !formData.amount || !formData.description || isLoading}
            sx={{ minWidth: 150 }}
          >
            {isLoading ? (
              <CircularProgress size={24} color="inherit" />
            ) : (
              'Add Transaction'
            )}
          </Button>
        </Box>
      </Box>
    </Paper>
  );
};