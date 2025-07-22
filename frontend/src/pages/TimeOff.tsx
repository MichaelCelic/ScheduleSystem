import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
} from '@mui/material';
import { DatePicker, LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { format } from 'date-fns';
import { useSchedulerContext } from '../components/layout/SchedulerContext';
import { useQuery } from '@apollo/client';
import { GET_TIME_OFF_REQUESTS } from '../graphql/queries';

interface TimeOffRequest {
  employeeId: string;
  startDate: Date | null;
  endDate: Date | null;
}

const TimeOff: React.FC = () => {
  const { employees, loading, error, requestTimeOff, updateTimeOff, deleteTimeOff } = useSchedulerContext();
  
  // Query for time off requests
  const { data: timeOffData, loading: timeOffLoading, error: timeOffError, refetch: refetchTimeOff } = useQuery(GET_TIME_OFF_REQUESTS);
  
  const [formData, setFormData] = useState<TimeOffRequest>({
    employeeId: '',
    startDate: null,
    endDate: null,
  });
  
  const [openDialog, setOpenDialog] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [deleteConfirmDialogOpen, setDeleteConfirmDialogOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [editingRequest, setEditingRequest] = useState<any>(null);

  const handleOpenDialog = () => {
    setOpenDialog(true);
    setSubmitError(null);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setFormData({
      employeeId: '',
      startDate: null,
      endDate: null,
    });
    setSubmitError(null);
  };

  const handleRequestTimeOff = () => {
    if (!formData.employeeId || !formData.startDate || !formData.endDate) {
      setSubmitError('Please fill in all fields');
      return;
    }
    
    if (formData.startDate > formData.endDate) {
      setSubmitError('Start date must be before or equal to end date');
      return;
    }
    
    setConfirmDialogOpen(true);
  };

  const handleConfirmRequest = async () => {
    if (!formData.employeeId || !formData.startDate || !formData.endDate) return;
    
    setSubmitting(true);
    setSubmitError(null);
    
    try {
      await requestTimeOff({
        variables: {
          input: {
            employeeId: formData.employeeId,
            startDate: formData.startDate.toISOString().split('T')[0],
            endDate: formData.endDate.toISOString().split('T')[0],
          }
        }
      });
      
      setConfirmDialogOpen(false);
      handleCloseDialog();
      refetchTimeOff(); // Refresh the time off requests list
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : 'An error occurred while requesting time off');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancelConfirm = () => {
    setConfirmDialogOpen(false);
  };

  const handleDeleteRequest = async () => {
    if (!editingRequest) return;
    
    setSubmitting(true);
    setSubmitError(null);
    
    try {
      await deleteTimeOff({
        variables: {
          id: editingRequest.id
        }
      });
      
      setDeleteConfirmDialogOpen(false);
      setEditDialogOpen(false);
      refetchTimeOff(); // Refresh the time off requests list
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : 'An error occurred while deleting the request');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancelDelete = () => {
    setDeleteConfirmDialogOpen(false);
  };

  const selectedEmployee = employees.find(emp => emp.id === formData.employeeId);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          Error loading employees: {error.message}
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3 }}>
        Request Time Off
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Submit Time Off Request
          </Typography>
          
          <Button
            variant="contained"
            onClick={handleOpenDialog}
            sx={{ mb: 2 }}
          >
            New Time Off Request
          </Button>

          <Typography variant="body2" color="text.secondary">
            Select an employee and specify the start and end dates for their time off request.
          </Typography>
        </CardContent>
      </Card>

      {/* View Requests Section */}
      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>
            View Requests
          </Typography>
          
          {timeOffLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress />
            </Box>
          ) : timeOffError ? (
            <Alert severity="error" sx={{ mb: 2 }}>
              Error loading time off requests: {timeOffError.message}
            </Alert>
          ) : (
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell><strong>Employee</strong></TableCell>
                    <TableCell><strong>Start Date</strong></TableCell>
                    <TableCell><strong>End Date</strong></TableCell>
                    <TableCell><strong>Status</strong></TableCell>
                    <TableCell><strong>Request Date</strong></TableCell>
                    <TableCell><strong>Actions</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {timeOffData?.timeOffRequests?.length > 0 ? (
                    timeOffData.timeOffRequests.map((request: any) => (
                      <TableRow key={request.id}>
                        <TableCell>
                          {request.employee?.name || 'Unknown Employee'}
                        </TableCell>
                        <TableCell>
                          {format(new Date(request.startDate), 'MMM d, yyyy')}
                        </TableCell>
                        <TableCell>
                          {format(new Date(request.endDate), 'MMM d, yyyy')}
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={request.status.charAt(0).toUpperCase() + request.status.slice(1)}
                            color={
                              request.status === 'approved' ? 'success' :
                              request.status === 'denied' ? 'error' : 'warning'
                            }
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          {format(new Date(request.requestDate), 'MMM d, yyyy')}
                        </TableCell>
                        <TableCell>
                          <Button
                            size="small"
                            variant="outlined"
                            onClick={() => {
                              setEditingRequest(request);
                              setEditDialogOpen(true);
                            }}
                          >
                            Edit
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={6} align="center">
                        No time off requests found
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Time Off Request Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          Request Time Off
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            {submitError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {submitError}
              </Alert>
            )}
            
            <FormControl fullWidth>
              <InputLabel>Select Employee</InputLabel>
              <Select
                value={formData.employeeId}
                onChange={(e) => setFormData({ ...formData, employeeId: e.target.value })}
                label="Select Employee"
              >
                {employees.map((employee) => (
                  <MenuItem key={employee.id} value={employee.id}>
                    {employee.name} ({employee.role === 'staff' ? 'Staff' : 'Student'})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Start Date"
                value={formData.startDate}
                onChange={(date) => setFormData({ ...formData, startDate: date })}
                slotProps={{
                  textField: {
                    fullWidth: true,
                    helperText: 'Select the first day of time off'
                  }
                }}
              />
              
              <DatePicker
                label="End Date"
                value={formData.endDate}
                onChange={(date) => setFormData({ ...formData, endDate: date })}
                slotProps={{
                  textField: {
                    fullWidth: true,
                    helperText: 'Select the last day of time off'
                  }
                }}
              />
            </LocalizationProvider>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>
            Cancel
          </Button>
          <Button
            onClick={handleRequestTimeOff}
            variant="contained"
            disabled={!formData.employeeId || !formData.startDate || !formData.endDate}
          >
            Request Time Off
          </Button>
        </DialogActions>
      </Dialog>

      {/* Confirmation Dialog */}
      <Dialog open={confirmDialogOpen} onClose={handleCancelConfirm} maxWidth="sm" fullWidth>
        <DialogTitle>
          Confirm Time Off Request
        </DialogTitle>
        <DialogContent>
          <Typography sx={{ mb: 2 }}>
            <strong>{selectedEmployee?.name}</strong> is requesting time off from{' '}
            <strong>{formData.startDate ? format(formData.startDate, 'MMM d, yyyy') : ''}</strong> to{' '}
            <strong>{formData.endDate ? format(formData.endDate, 'MMM d, yyyy') : ''}</strong>.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            This request will be submitted and can be reviewed by administrators.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancelConfirm} disabled={submitting}>
            Cancel
          </Button>
          <Button
            onClick={handleConfirmRequest}
            variant="contained"
            disabled={submitting}
          >
            {submitting ? <CircularProgress size={20} /> : 'Confirm'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Time Off Request Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          Edit Time Off Request
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            {submitError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {submitError}
              </Alert>
            )}
            
            <Typography variant="body1" sx={{ mb: 2 }}>
              <strong>Employee:</strong> {editingRequest?.employee?.name || 'Unknown Employee'}
            </Typography>
            
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Start Date"
                value={editingRequest ? new Date(editingRequest.startDate) : null}
                onChange={(date) => setEditingRequest({ ...editingRequest, startDate: date?.toISOString().split('T')[0] })}
                slotProps={{
                  textField: {
                    fullWidth: true,
                    helperText: 'Select the first day of time off'
                  }
                }}
              />
              
              <DatePicker
                label="End Date"
                value={editingRequest ? new Date(editingRequest.endDate) : null}
                onChange={(date) => setEditingRequest({ ...editingRequest, endDate: date?.toISOString().split('T')[0] })}
                slotProps={{
                  textField: {
                    fullWidth: true,
                    helperText: 'Select the last day of time off'
                  }
                }}
              />
            </LocalizationProvider>

            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={editingRequest?.status || 'pending'}
                onChange={(e) => setEditingRequest({ ...editingRequest, status: e.target.value })}
                label="Status"
              >
                <MenuItem value="pending">Pending</MenuItem>
                <MenuItem value="approved">Approved</MenuItem>
                <MenuItem value="denied">Denied</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>
            Cancel
          </Button>
          <Button
            color="error"
            onClick={() => setDeleteConfirmDialogOpen(true)}
            disabled={submitting}
          >
            Delete Request
          </Button>
          <Button
            onClick={async () => {
              if (!editingRequest) return;
              
              setSubmitting(true);
              setSubmitError(null);
              
              try {
                await updateTimeOff({
                  variables: {
                    id: editingRequest.id,
                    input: {
                      employeeId: editingRequest.employeeId,
                      startDate: editingRequest.startDate,
                      endDate: editingRequest.endDate,
                    },
                    status: editingRequest.status.toUpperCase(),
                  },
                });
                setEditDialogOpen(false);
                refetchTimeOff();
              } catch (error) {
                setSubmitError(error instanceof Error ? error.message : 'An error occurred while updating the request');
              } finally {
                setSubmitting(false);
              }
            }}
            variant="contained"
            disabled={submitting}
          >
            {submitting ? <CircularProgress size={20} /> : 'Save Changes'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteConfirmDialogOpen} onClose={handleCancelDelete} maxWidth="sm" fullWidth>
        <DialogTitle>
          Confirm Delete Time Off Request
        </DialogTitle>
        <DialogContent>
          <Typography sx={{ mb: 2 }}>
            Are you sure you want to delete the time off request for{' '}
            <strong>{editingRequest?.employee?.name || 'Unknown Employee'}</strong>?
          </Typography>
          <Typography variant="body2" color="text.secondary">
            This action cannot be undone. The time off request will be permanently removed.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancelDelete} disabled={submitting}>
            Cancel
          </Button>
          <Button
            onClick={handleDeleteRequest}
            variant="contained"
            color="error"
            disabled={submitting}
          >
            {submitting ? <CircularProgress size={20} /> : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TimeOff; 