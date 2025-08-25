/**
 * Quick actions component for the dashboard.
 */

import React from 'react';
import { 
  Paper, 
  Typography, 
  Button, 
  Box, 
  Stack 
} from '@mui/material';
import { 
  Add, 
  AccountBalance, 
  Receipt,
  Assessment 
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { PayPeriod } from '../../types/budget';
import { ROUTES } from '../../utils/constants';

interface QuickActionsProps {
  payPeriod?: PayPeriod;
}

export const QuickActions: React.FC<QuickActionsProps> = ({ payPeriod }) => {
  const navigate = useNavigate();

  const actions = [
    {
      label: 'Add Transaction',
      icon: <Add />,
      onClick: () => navigate(ROUTES.TRANSACTIONS),
      disabled: !payPeriod,
      description: 'Record a new expense'
    },
    {
      label: 'Manage Budget',
      icon: <AccountBalance />,
      onClick: () => navigate(ROUTES.BUDGET),
      disabled: false,
      description: 'Set up budget categories'
    },
    {
      label: 'View All Transactions',
      icon: <Receipt />,
      onClick: () => navigate(ROUTES.TRANSACTIONS),
      disabled: false,
      description: 'See transaction history'
    },
    {
      label: 'View History',
      icon: <Assessment />,
      onClick: () => navigate(ROUTES.HISTORY),
      disabled: false,
      description: 'Past pay periods'
    },
  ];

  return (
    <Paper elevation={2} sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom color="primary">
        Quick Actions
      </Typography>
      
      <Stack spacing={2}>
        {actions.map((action) => (
          <Button
            key={action.label}
            variant="outlined"
            startIcon={action.icon}
            onClick={action.onClick}
            disabled={action.disabled}
            fullWidth
            sx={{ 
              justifyContent: 'flex-start',
              py: 1.5,
              textAlign: 'left'
            }}
          >
            <Box sx={{ textAlign: 'left', width: '100%' }}>
              <Typography variant="button" display="block">
                {action.label}
              </Typography>
              <Typography variant="caption" color="textSecondary" display="block">
                {action.description}
              </Typography>
            </Box>
          </Button>
        ))}
      </Stack>

      {!payPeriod && (
        <Typography 
          variant="caption" 
          color="textSecondary" 
          sx={{ mt: 2, display: 'block' }}
        >
          Some actions require an active pay period
        </Typography>
      )}
    </Paper>
  );
};