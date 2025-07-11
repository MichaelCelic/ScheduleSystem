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
  Grid,
  IconButton,
  TextField,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Stack,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
} from '@mui/icons-material';
import { useSchedulerContext } from '../components/layout/SchedulerContext';

interface Employee {
  id: string;
  name: string;
  role: 'staff' | 'student';
  availability: {
    days: string[];
    maxHoursPerDay: number;
    preferredShifts: string[];
  };
}

const DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const SHIFT_TYPES = ['Morning (6AM-2PM)', 'Afternoon (2PM-10PM)', 'Night (10PM-6AM)'];

const Employees: React.FC = () => {
  const { 
    employees, 
    loading, 
    error, 
    addEmployee, 
    updateEmployee, 
    deleteEmployee 
  } = useSchedulerContext();
  
  const [openDialog, setOpenDialog] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState<Employee | null>(null);
  const [formData, setFormData] = useState<Partial<Employee>>({
    name: '',
    role: 'staff',
    availability: {
      days: [],
      maxHoursPerDay: 8,
      preferredShifts: [],
    },
  });
  const [saving, setSaving] = useState(false);
  
  // Confirmation dialog state
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [employeeToDelete, setEmployeeToDelete] = useState<Employee | null>(null);

  const handleOpenDialog = (employee?: Employee) => {
    if (employee) {
      setEditingEmployee(employee);
      setFormData(employee);
    } else {
      setEditingEmployee(null);
      setFormData({
        name: '',
        role: 'staff',
        availability: {
          days: [],
          maxHoursPerDay: 8,
          preferredShifts: [],
        },
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingEmployee(null);
    setSaving(false);
  };

  const handleSaveEmployee = async () => {
    if (!formData.name) return;

    setSaving(true);

    try {
      const employeeData = {
        name: formData.name!,
        age: 25, // Default age since frontend doesn't collect it
        role: formData.role?.toUpperCase() || 'STAFF',
        maxHoursPerDay: formData.availability?.maxHoursPerDay || 8,
        availability: formData.availability?.days?.map(day => {
          const dayMap: { [key: string]: string } = {
            'Monday': 'MON',
            'Tuesday': 'TUE',
            'Wednesday': 'WED',
            'Thursday': 'THU',
            'Friday': 'FRI',
            'Saturday': 'SAT',
            'Sunday': 'SUN'
          };
          return dayMap[day] || day.toUpperCase().substring(0, 3);
        }) || [],
        preferredShifts: formData.availability?.preferredShifts || []
      };

      if (editingEmployee) {
        await updateEmployee({
          variables: {
            id: editingEmployee.id,
            input: employeeData
          }
        });
      } else {
        await addEmployee({
          variables: {
            input: employeeData
          }
        });
      }

      handleCloseDialog();
    } catch (error) {
      console.error('Error saving employee:', error);
      setSaving(false);
    }
  };

  const handleDeleteEmployee = async (employeeId: string) => {
    try {
      await deleteEmployee({
        variables: { id: employeeId }
      });
    } catch (error) {
      console.error('Error deleting employee:', error);
    }
  };

  const handleDeleteClick = (employee: Employee) => {
    setEmployeeToDelete(employee);
    setDeleteConfirmOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!employeeToDelete) return;
    
    try {
      await deleteEmployee({
        variables: { id: employeeToDelete.id }
      });
      setDeleteConfirmOpen(false);
      setEmployeeToDelete(null);
    } catch (error) {
      console.error('Error deleting employee:', error);
    }
  };

  const handleCancelDelete = () => {
    setDeleteConfirmOpen(false);
    setEmployeeToDelete(null);
  };

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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Employees</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Employee
        </Button>
      </Box>

      <Grid container spacing={3}>
        {employees.map((employee) => (
          <Grid item xs={12} sm={6} md={4} key={employee.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Typography variant="h6">{employee.name}</Typography>
                  <Box>
                    <IconButton onClick={() => handleOpenDialog(employee)}>
                      <EditIcon />
                    </IconButton>
                    <IconButton onClick={() => handleDeleteClick(employee)}>
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                </Box>
                <Typography variant="subtitle2" sx={{ mt: 1 }} color="text.secondary">
                  Role: {employee.role === 'staff' ? 'Staff' : 'Student'}
                </Typography>

                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Availability
                  </Typography>
                  <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap', gap: 0.5 }}>
                    {employee.availability.days.map((day) => (
                      <Chip key={day} label={day} size="small" />
                    ))}
                  </Stack>

                  <Typography variant="subtitle2" sx={{ mt: 2 }} gutterBottom>
                    Preferred Shifts
                  </Typography>
                  <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap', gap: 0.5 }}>
                    {employee.availability.preferredShifts.map((shift) => (
                      <Chip key={shift} label={shift} size="small" />
                    ))}
                  </Stack>

                  <Typography variant="subtitle2" sx={{ mt: 2 }}>
                    Max Hours Per Day: {employee.availability.maxHoursPerDay}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingEmployee ? 'Edit Employee' : 'Add Employee'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label="Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              fullWidth
            />
            <FormControl fullWidth>
              <InputLabel>Role</InputLabel>
              <Select
                value={formData.role || 'staff'}
                label="Role"
                onChange={(e) => setFormData({ ...formData, role: e.target.value as 'staff' | 'student' })}
              >
                <MenuItem value="staff">Staff</MenuItem>
                <MenuItem value="student">Student</MenuItem>
              </Select>
            </FormControl>

            <FormControl fullWidth>
              <InputLabel>Available Days</InputLabel>
              <Select
                multiple
                value={formData.availability?.days || []}
                onChange={(e) => setFormData({
                  ...formData,
                  availability: {
                    ...formData.availability!,
                    days: e.target.value as string[],
                  },
                })}
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((value) => (
                      <Chip key={value} label={value} size="small" />
                    ))}
                  </Box>
                )}
              >
                {DAYS_OF_WEEK.map((day) => (
                  <MenuItem key={day} value={day}>
                    {day}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth>
              <InputLabel>Preferred Shifts</InputLabel>
              <Select
                multiple
                value={formData.availability?.preferredShifts || []}
                onChange={(e) => setFormData({
                  ...formData,
                  availability: {
                    ...formData.availability!,
                    preferredShifts: e.target.value as string[],
                  },
                })}
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((value) => (
                      <Chip key={value} label={value} size="small" />
                    ))}
                  </Box>
                )}
              >
                {SHIFT_TYPES.map((shift) => (
                  <MenuItem key={shift} value={shift}>
                    {shift}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              label="Max Hours Per Day"
              type="number"
              value={formData.availability?.maxHoursPerDay || 8}
              onChange={(e) => setFormData({
                ...formData,
                availability: {
                  ...formData.availability!,
                  maxHoursPerDay: parseInt(e.target.value) || 8,
                },
              })}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} disabled={saving}>
            Cancel
          </Button>
          <Button 
            onClick={handleSaveEmployee} 
            variant="contained"
            disabled={saving || !formData.name}
          >
            {saving ? (
              <CircularProgress size={20} />
            ) : (
              editingEmployee ? 'Save Changes' : 'Add Employee'
            )}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteConfirmOpen} onClose={handleCancelDelete} maxWidth="sm" fullWidth>
        <DialogTitle>
          Confirm Delete
        </DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete <strong>{employeeToDelete?.name}</strong>?
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            This action cannot be undone. All employee data including availability preferences and shift assignments will be permanently removed.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancelDelete}>
            Cancel
          </Button>
          <Button 
            onClick={handleConfirmDelete} 
            variant="contained" 
            color="error"
          >
            Delete Employee
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Employees; 