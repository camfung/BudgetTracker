/**
 * Transaction list component showing recent transactions.
 */

import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Divider,
  Alert,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
} from '@mui/material';
import { MoreVert, Delete, Receipt } from '@mui/icons-material';
import { Transaction } from '../../types/transaction';
import { PayPeriod } from '../../types/budget';
import { deleteTransaction } from '../../services/transaction.service';
import { formatCurrency, formatDate } from '../../utils/formatters';

interface TransactionListProps {
  transactions: Transaction[];
  payPeriod?: PayPeriod;
  onTransactionDeleted?: (transactionId: number) => void;
  maxItems?: number;
}

export const TransactionList: React.FC<TransactionListProps> = ({
  transactions,
  payPeriod,
  onTransactionDeleted,
  maxItems,
}) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const displayTransactions = maxItems 
    ? transactions.slice(0, maxItems) 
    : transactions;

  const getCategoryName = (categoryId: number): string => {
    if (!payPeriod?.budget_categories) return 'Unknown Category';
    const category = payPeriod.budget_categories.find(cat => cat.id === categoryId);
    return category?.name || 'Unknown Category';
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, transaction: Transaction) => {
    setAnchorEl(event.currentTarget);
    setSelectedTransaction(transaction);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedTransaction(null);
  };

  const handleDeleteClick = () => {
    setDeleteDialogOpen(true);
    handleMenuClose();
  };

  const handleDeleteConfirm = async () => {
    if (!selectedTransaction) return;

    setIsDeleting(true);
    try {
      await deleteTransaction(selectedTransaction.id);
      if (onTransactionDeleted) {
        onTransactionDeleted(selectedTransaction.id);
      }
      setDeleteDialogOpen(false);
      setSelectedTransaction(null);
    } catch (error) {
      console.error('Failed to delete transaction:', error);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setSelectedTransaction(null);
  };

  if (transactions.length === 0) {
    return (
      <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
        <Receipt sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h6" color="textSecondary">
          No transactions yet
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Add your first expense to start tracking your spending
        </Typography>
      </Paper>
    );
  }

  return (
    <>
      <Paper elevation={2} sx={{ overflow: 'hidden' }}>
        <Box sx={{ p: 2, bgcolor: 'primary.main', color: 'white' }}>
          <Typography variant="h6">
            Recent Transactions
          </Typography>
          {maxItems && transactions.length > maxItems && (
            <Typography variant="caption">
              Showing {maxItems} of {transactions.length} transactions
            </Typography>
          )}
        </Box>

        <List sx={{ py: 0 }}>
          {displayTransactions.map((transaction, index) => (
            <React.Fragment key={transaction.id}>
              <ListItem sx={{ py: 2 }}>
                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="subtitle1" component="span">
                        {transaction.description}
                      </Typography>
                      <Chip
                        label={getCategoryName(transaction.budget_category_id)}
                        size="small"
                        variant="outlined"
                        color="primary"
                      />
                      {transaction.source === 'api' && (
                        <Chip
                          label="API"
                          size="small"
                          color="info"
                          variant="outlined"
                        />
                      )}
                    </Box>
                  }
                  secondary={
                    <Typography variant="body2" color="textSecondary">
                      {formatDate(transaction.transaction_date, 'PPp')}
                    </Typography>
                  }
                />
                
                <ListItemSecondaryAction>
                  <Box display="flex" alignItems="center" gap={1}>
                    <Typography 
                      variant="h6" 
                      color="error.main"
                      sx={{ fontWeight: 'bold' }}
                    >
                      -{formatCurrency(transaction.amount)}
                    </Typography>
                    
                    <IconButton
                      size="small"
                      onClick={(e) => handleMenuOpen(e, transaction)}
                    >
                      <MoreVert />
                    </IconButton>
                  </Box>
                </ListItemSecondaryAction>
              </ListItem>
              
              {index < displayTransactions.length - 1 && <Divider />}
            </React.Fragment>
          ))}
        </List>

        {maxItems && transactions.length > maxItems && (
          <Box sx={{ p: 2, bgcolor: 'grey.50', textAlign: 'center' }}>
            <Typography variant="body2" color="textSecondary">
              {transactions.length - maxItems} more transactions...
            </Typography>
          </Box>
        )}
      </Paper>

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleDeleteClick}>
          <Delete sx={{ mr: 1 }} fontSize="small" />
          Delete
        </MenuItem>
      </Menu>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleDeleteCancel}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Delete Transaction</DialogTitle>
        <DialogContent>
          {selectedTransaction && (
            <Alert severity="warning" sx={{ mb: 2 }}>
              Are you sure you want to delete this transaction?
              <br />
              <strong>{selectedTransaction.description}</strong> - {formatCurrency(selectedTransaction.amount)}
            </Alert>
          )}
          <Typography variant="body2" color="textSecondary">
            This action will restore the amount to your budget category and cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel}>
            Cancel
          </Button>
          <Button
            onClick={handleDeleteConfirm}
            color="error"
            variant="contained"
            disabled={isDeleting}
          >
            {isDeleting ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};