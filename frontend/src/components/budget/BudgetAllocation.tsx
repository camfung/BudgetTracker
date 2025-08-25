/**
 * Budget allocation component for distributing income across categories.
 */

import React, { useState, useEffect } from 'react';
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
  Chip,
  IconButton,
  Autocomplete,
} from '@mui/material';
import { Add, Delete, AttachMoney } from '@mui/icons-material';
import { allocateBudget } from '../../services/budget.service';
import { PayPeriod, BudgetAllocation as BudgetAllocationData } from '../../types/budget';
import { formatCurrency } from '../../utils/formatters';
import { DEFAULT_BUDGET_CATEGORIES } from '../../utils/constants';

interface BudgetAllocationProps {
  payPeriod: PayPeriod;
  onAllocationComplete?: (categories: any[]) => void;
  onBudgetUpdated?: () => void;
}

interface CategoryAllocation {
  name: string;
  allocated_amount: string;
}

export const BudgetAllocation: React.FC<BudgetAllocationProps> = ({
  payPeriod,
  onAllocationComplete,
  onBudgetUpdated,
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [allocations, setAllocations] = useState<CategoryAllocation[]>([
    { name: '', allocated_amount: '' },
  ]);

  const totalIncome = parseFloat(payPeriod.total_income);
  const totalAllocated = allocations.reduce((sum, allocation) => {
    return sum + (parseFloat(allocation.allocated_amount) || 0);
  }, 0);
  const remaining = totalIncome - totalAllocated;

  useEffect(() => {
    // If there are existing categories, populate them
    if (payPeriod.budget_categories && payPeriod.budget_categories.length > 0) {
      const existingAllocations = payPeriod.budget_categories.map(cat => ({
        name: cat.name,
        allocated_amount: cat.allocated_amount,
      }));
      setAllocations(existingAllocations);
    }
  }, [payPeriod.budget_categories]);

  const handleAllocationChange = (index: number, field: keyof CategoryAllocation, value: string) => {
    setAllocations(prev => {
      const newAllocations = [...prev];
      newAllocations[index] = { ...newAllocations[index], [field]: value };
      return newAllocations;
    });
    setError(null);
  };

  const addCategory = () => {
    setAllocations(prev => [...prev, { name: '', allocated_amount: '' }]);
  };

  const removeCategory = (index: number) => {
    if (allocations.length > 1) {
      setAllocations(prev => prev.filter((_, i) => i !== index));
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);

    // Validate all categories have names and amounts
    const validAllocations = allocations.filter(
      allocation => allocation.name && parseFloat(allocation.allocated_amount) > 0
    );

    if (validAllocations.length === 0) {
      setError('Please add at least one budget category');
      return;
    }

    if (totalAllocated > totalIncome) {
      setError(`Total allocation (${formatCurrency(totalAllocated)}) exceeds income (${formatCurrency(totalIncome)})`);
      return;
    }

    setIsLoading(true);

    try {
      const allocationData: BudgetAllocationData = {
        pay_period_id: payPeriod.id,
        allocations: validAllocations,
      };

      const categories = await allocateBudget(allocationData);
      if (onAllocationComplete) {
        onAllocationComplete(categories);
      }
      if (onBudgetUpdated) {
        onBudgetUpdated();
      }
    } catch (err: any) {
      setError(err.message || 'Failed to allocate budget');
    } finally {
      setIsLoading(false);
    }
  };

  const autoAllocateRemainder = () => {
    if (remaining > 0 && allocations.length > 0) {
      const lastEmptyIndex = allocations.findIndex(
        allocation => !allocation.allocated_amount || parseFloat(allocation.allocated_amount) === 0
      );
      
      if (lastEmptyIndex !== -1) {
        handleAllocationChange(lastEmptyIndex, 'allocated_amount', remaining.toString());
      }
    }
  };

  return (
    <Paper elevation={2} sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom color="primary">
        Budget Allocation
      </Typography>
      
      <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
        Distribute your {formatCurrency(totalIncome)} across budget categories
      </Typography>

      <Box sx={{ mb: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={4}>
            <Chip 
              label={`Income: ${formatCurrency(totalIncome)}`} 
              color="primary" 
              variant="outlined" 
            />
          </Grid>
          <Grid item xs={4}>
            <Chip 
              label={`Allocated: ${formatCurrency(totalAllocated)}`} 
              color="info" 
              variant="outlined" 
            />
          </Grid>
          <Grid item xs={4}>
            <Chip 
              label={`Remaining: ${formatCurrency(remaining)}`} 
              color={remaining < 0 ? 'error' : remaining > 0 ? 'warning' : 'success'}
              variant="outlined" 
            />
          </Grid>
        </Grid>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Box component="form" onSubmit={handleSubmit}>
        {allocations.map((allocation, index) => (
          <Grid container spacing={2} key={index} sx={{ mb: 2 }}>
            <Grid item xs={12} sm={6}>
              <Autocomplete
                freeSolo
                options={DEFAULT_BUDGET_CATEGORIES}
                value={allocation.name}
                onChange={(_, value) => handleAllocationChange(index, 'name', value || '')}
                onInputChange={(_, value) => handleAllocationChange(index, 'name', value)}
                disabled={isLoading}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Category Name"
                    required
                    fullWidth
                    placeholder="e.g., Groceries, Rent, etc."
                  />
                )}
              />
            </Grid>
            
            <Grid item xs={12} sm={5}>
              <TextField
                required
                fullWidth
                label="Amount"
                value={allocation.allocated_amount}
                onChange={(e) => {
                  const value = e.target.value;
                  if (value === '' || /^\d*\.?\d*$/.test(value)) {
                    handleAllocationChange(index, 'allocated_amount', value);
                  }
                }}
                disabled={isLoading}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <AttachMoney color="action" />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            
            <Grid item xs={12} sm={1}>
              <IconButton
                onClick={() => removeCategory(index)}
                disabled={allocations.length === 1 || isLoading}
                color="error"
              >
                <Delete />
              </IconButton>
            </Grid>
          </Grid>
        ))}

        <Box sx={{ mb: 3 }}>
          <Button
            startIcon={<Add />}
            onClick={addCategory}
            disabled={isLoading}
            sx={{ mr: 2 }}
          >
            Add Category
          </Button>
          
          {remaining > 0 && (
            <Button
              variant="outlined"
              onClick={autoAllocateRemainder}
              disabled={isLoading}
            >
              Allocate Remaining ({formatCurrency(remaining)})
            </Button>
          )}
        </Box>

        <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            type="submit"
            variant="contained"
            disabled={totalAllocated === 0 || isLoading}
            sx={{ minWidth: 150 }}
          >
            {isLoading ? (
              <CircularProgress size={24} color="inherit" />
            ) : (
              'Save Budget'
            )}
          </Button>
        </Box>
      </Box>
    </Paper>
  );
};