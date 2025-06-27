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
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
} from '@mui/icons-material';
import { useSchedulerContext, Location as SchedulerLocation } from '../components/layout/SchedulerContext';

type Location = SchedulerLocation;

const Locations: React.FC = () => {
  const { locations, setLocations } = useSchedulerContext();
  const [openDialog, setOpenDialog] = useState(false);
  const [editingLocation, setEditingLocation] = useState<Location | null>(null);
  const [formData, setFormData] = useState<Partial<Location>>({
    name: '',
    address: '',
    requiredStaff: {
      morning: 2,
      afternoon: 2,
      night: 1,
    },
    notes: '',
  });

  const handleOpenDialog = (location?: Location) => {
    if (location) {
      setEditingLocation(location);
      setFormData(location);
    } else {
      setEditingLocation(null);
      setFormData({
        name: '',
        address: '',
        requiredStaff: {
          morning: 2,
          afternoon: 2,
          night: 1,
        },
        notes: '',
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingLocation(null);
  };

  const handleSaveLocation = () => {
    if (!formData.name || !formData.address) return;

    const newLocation: Location = {
      id: editingLocation?.id || Date.now().toString(),
      name: formData.name,
      address: formData.address,
      requiredStaff: {
        morning: formData.requiredStaff?.morning || 2,
        afternoon: formData.requiredStaff?.afternoon || 2,
        night: formData.requiredStaff?.night || 1,
      },
      notes: formData.notes,
    };

    if (editingLocation) {
      setLocations(locations.map(loc =>
        loc.id === editingLocation.id ? newLocation : loc
      ));
    } else {
      setLocations([...locations, newLocation]);
    }

    handleCloseDialog();
  };

  const handleDeleteLocation = (locationId: string) => {
    setLocations(locations.filter(loc => loc.id !== locationId));
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Locations</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Location
        </Button>
      </Box>

      <Grid container spacing={3}>
        {locations.map((location) => (
          <Grid item xs={12} sm={6} md={4} key={location.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
                    <Typography variant="h6">{location.name}</Typography>
                    <Typography color="text.secondary">{location.address || ''}</Typography>
                  </Box>
                  <Box>
                    <IconButton onClick={() => handleOpenDialog(location)}>
                      <EditIcon />
                    </IconButton>
                    <IconButton onClick={() => handleDeleteLocation(location.id)}>
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                </Box>

                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Required Staff per Shift
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={4}>
                      <Typography variant="body2" color="text.secondary">
                        Morning (6AM-2PM)
                      </Typography>
                      <Typography variant="h6">
                        {(location.requiredStaff?.morning ?? 0)}
                      </Typography>
                    </Grid>
                    <Grid item xs={4}>
                      <Typography variant="body2" color="text.secondary">
                        Afternoon (2PM-10PM)
                      </Typography>
                      <Typography variant="h6">
                        {(location.requiredStaff?.afternoon ?? 0)}
                      </Typography>
                    </Grid>
                    <Grid item xs={4}>
                      <Typography variant="body2" color="text.secondary">
                        Night (10PM-6AM)
                      </Typography>
                      <Typography variant="h6">
                        {(location.requiredStaff?.night ?? 0)}
                      </Typography>
                    </Grid>
                  </Grid>
                </Box>

                {location.notes && (
                  <Typography variant="body2" sx={{ mt: 2 }}>
                    Notes: {location.notes}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingLocation ? 'Edit Location' : 'Add Location'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label="Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              fullWidth
            />

            <TextField
              label="Address"
              value={formData.address}
              onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              fullWidth
            />

            <Typography variant="subtitle2" sx={{ mt: 1 }}>
              Required Staff per Shift
            </Typography>

            <Grid container spacing={2}>
              <Grid item xs={4}>
                <TextField
                  label="Morning"
                  type="number"
                  value={formData.requiredStaff?.morning || 2}
                  onChange={(e) => setFormData({
                    ...formData,
                    requiredStaff: {
                      ...formData.requiredStaff!,
                      morning: parseInt(e.target.value) || 2,
                    },
                  })}
                  fullWidth
                />
              </Grid>
              <Grid item xs={4}>
                <TextField
                  label="Afternoon"
                  type="number"
                  value={formData.requiredStaff?.afternoon || 2}
                  onChange={(e) => setFormData({
                    ...formData,
                    requiredStaff: {
                      ...formData.requiredStaff!,
                      afternoon: parseInt(e.target.value) || 2,
                    },
                  })}
                  fullWidth
                />
              </Grid>
              <Grid item xs={4}>
                <TextField
                  label="Night"
                  type="number"
                  value={formData.requiredStaff?.night || 1}
                  onChange={(e) => setFormData({
                    ...formData,
                    requiredStaff: {
                      ...formData.requiredStaff!,
                      night: parseInt(e.target.value) || 1,
                    },
                  })}
                  fullWidth
                />
              </Grid>
            </Grid>

            <TextField
              label="Notes"
              multiline
              rows={4}
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSaveLocation} variant="contained">
            {editingLocation ? 'Save Changes' : 'Add Location'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Locations; 