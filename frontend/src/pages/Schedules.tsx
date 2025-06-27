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
  Paper,
  Tab,
  Tabs,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stack,
  Chip,
  Alert,
  Table,
  TableHead,
  TableBody,
  TableCell,
  TableRow,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Publish as PublishIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { addWeeks, format, startOfWeek } from 'date-fns';
import { ScheduleGenerator } from '../utils/scheduleGenerator';
import { useSchedulerContext } from '../components/layout/SchedulerContext';

interface Schedule {
  id: string;
  locationId: string;
  locationName: string;
  weekStart: Date;
  assignments: {
    [employeeName: string]: {
      [day: string]: string;
    };
  };
  status: 'draft' | 'published';
  type: string;
}

// On Call assignments type
interface OnCallAssignments {
  JDCH: { [day: string]: string };
  WM: { [day: string]: string };
}

const DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const SHIFT_TYPES = ['Morning', 'Afternoon', 'Night'];
const SCHEDULE_TYPES = ['Echo Lab', 'On Call'];

const Schedules: React.FC = () => {
  const { schedules, setSchedules, employees, locations } = useSchedulerContext();
  const [selectedTab, setSelectedTab] = useState(0);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingSchedule, setEditingSchedule] = useState<Schedule | null>(null);
  const [formData, setFormData] = useState<Partial<Schedule>>({
    locationId: '',
    locationName: '',
    weekStart: startOfWeek(new Date()),
    assignments: {},
    status: 'draft',
  });
  const [error, setError] = useState<string | null>(null);
  const [selectedDraftTab, setSelectedDraftTab] = useState(0);
  const [scheduleType, setScheduleType] = useState('Echo Lab');

  // Get JDCH location from live data
  const jdchLocation = locations.find(loc => loc.name === 'JDCH');

  const ON_CALL_LOCATIONS = ['JDCH', 'W/M'];

  const ON_CALL_DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
  };

  const handleOpenDialog = (schedule?: Schedule) => {
    if (schedule) {
      setEditingSchedule(schedule);
      setFormData(schedule);
    } else {
      setEditingSchedule(null);
      setFormData({
        locationId: '',
        locationName: '',
        weekStart: startOfWeek(new Date()),
        assignments: {},
        status: 'draft',
      });
    }
    setOpenDialog(true);
    setError(null);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingSchedule(null);
    setError(null);
    setFormData({
      locationId: '',
      locationName: '',
      weekStart: startOfWeek(new Date()),
      assignments: {},
      status: 'draft',
    });
  };

  const NUM_DRAFT_SCHEDULES = 5; // Number of draft schedules to generate

  const handleGenerateSchedule = () => {
    try {
      if (scheduleType === 'Echo Lab') {
        if (!jdchLocation) {
          setError('JDCH location not found');
          return;
        }
        const newDrafts = Array.from({ length: NUM_DRAFT_SCHEDULES }).map(() => {
          const generator = new ScheduleGenerator(
            employees,
            jdchLocation,
            formData.weekStart!,
          );
          return { ...generator.generateSchedule(), type: 'echolab' };
        });
        setSchedules(prev => [
          ...prev.filter(s => !(s.status === 'draft' && s.type === 'echolab')),
          ...newDrafts
        ]);
        setSelectedDraftTab(0); // Switch to Echo Lab tab
        handleCloseDialog();
      } else if (scheduleType === 'On Call') {
        // Exclude students from On Call
        const onCallEmployees = employees.filter(emp => emp.role !== 'student');
        const newOnCallDrafts = Array.from({ length: NUM_DRAFT_SCHEDULES }).map(() => {
          const assignments: OnCallAssignments = { JDCH: {}, WM: {} };
          const shuffledJDCH = [...onCallEmployees].sort(() => Math.random() - 0.5);
          const shuffledWM = [...onCallEmployees].sort(() => Math.random() - 0.5);
          DAYS_OF_WEEK.forEach((day, idx) => {
            assignments.JDCH[day] = shuffledJDCH[idx % shuffledJDCH.length].name;
            assignments.WM[day] = shuffledWM[idx % shuffledWM.length].name;
          });
          return {
            id: Date.now().toString() + Math.random().toString(36).substring(2),
            locationId: 'oncall',
            locationName: 'On Call',
            weekStart: formData.weekStart!,
            assignments: assignments as any,
            status: 'draft' as 'draft',
            type: 'oncall',
          };
        });
        setSchedules(prev => [
          ...prev.filter(s => !(s.status === 'draft' && s.type === 'oncall')),
          ...newOnCallDrafts
        ]);
        setSelectedDraftTab(1); // Switch to On Call tab
        handleCloseDialog();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while generating the schedule');
    }
  };

  const handlePublishSchedule = (scheduleId: string) => {
    setSchedules(schedules.map(schedule =>
      schedule.id === scheduleId
        ? { ...schedule, status: 'published' }
        : schedule
    ));
  };

  const handleDeleteSchedule = (scheduleId: string) => {
    setSchedules(schedules.filter(schedule => schedule.id !== scheduleId));
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Schedules</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Generate New Schedule
        </Button>
      </Box>

      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={selectedTab}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
        >
          <Tab label="Draft Schedules" />
          <Tab label="Published Schedules" />
        </Tabs>
      </Paper>

      {selectedTab === 0 && (
        <>
          <Paper sx={{ mb: 3 }}>
            <Tabs
              value={selectedDraftTab}
              onChange={(_, v) => setSelectedDraftTab(v)}
              indicatorColor="primary"
              textColor="primary"
            >
              <Tab label="Echo Lab" />
              <Tab label="On Call" />
            </Tabs>
          </Paper>
          {selectedDraftTab === 0 && (
            <Grid container spacing={3}>
              {schedules
                .filter(schedule => schedule.status === 'draft' && schedule.type === 'echolab')
                .map((schedule) => (
                  <Grid item xs={12} key={schedule.id}>
                    <Card>
                      <CardContent>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                          <Box>
                            <Typography variant="h6">{schedule.locationName}</Typography>
                            <Typography color="text.secondary">
                              Week of {format(schedule.weekStart, 'MMM d, yyyy')}
                            </Typography>
                          </Box>
                          <Box>
                            {schedule.status === 'draft' && (
                              <>
                                <IconButton onClick={() => handlePublishSchedule(schedule.id)}>
                                  <PublishIcon />
                                </IconButton>
                                <IconButton onClick={() => handleOpenDialog(schedule)}>
                                  <EditIcon />
                                </IconButton>
                              </>
                            )}
                            <IconButton onClick={() => handleDeleteSchedule(schedule.id)}>
                              <DeleteIcon />
                            </IconButton>
                          </Box>
                        </Box>

                        <Box sx={{ mt: 2 }}>
                          <Paper sx={{ p: 2 }}>
                            <Table>
                              <TableHead>
                                <TableRow>
                                  <TableCell>Employee</TableCell>
                                  {DAYS_OF_WEEK.map((day) => (
                                    <TableCell key={day}>{day}</TableCell>
                                  ))}
                                </TableRow>
                              </TableHead>
                              <TableBody>
                                {Object.keys(schedule.assignments).map((employee) => (
                                  <TableRow key={employee}>
                                    <TableCell>{employee}</TableCell>
                                    {DAYS_OF_WEEK.map((day) => (
                                      <TableCell key={day}>
                                        {schedule.assignments[employee][day] || ''}
                                      </TableCell>
                                    ))}
                                  </TableRow>
                                ))}
                              </TableBody>
                            </Table>
                          </Paper>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
            </Grid>
          )}
          {selectedDraftTab === 1 && (
            <Paper sx={{ p: 2, mb: 3 }}>
              {schedules.filter(s => s.status === 'draft' && s.type === 'oncall').length === 0 ? (
                <Typography>No On Call schedules generated yet.</Typography>
              ) : (
                schedules.filter(s => s.status === 'draft' && s.type === 'oncall').map((schedule, idx) => (
                  <Box key={schedule.id} sx={{ mb: 4 }}>
                    <Typography variant="subtitle1">On Call Option {idx + 1}</Typography>
                    <Typography color="text.secondary" sx={{ mb: 1 }}>
                      Week of {format(schedule.weekStart, 'MMM d, yyyy')}
                    </Typography>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell></TableCell>
                          {DAYS_OF_WEEK.map((day) => (
                            <TableCell key={day}>{day}</TableCell>
                          ))}
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {['JDCH', 'WM'].map((loc) => (
                          <TableRow key={loc}>
                            <TableCell>On Call {loc === 'WM' ? 'W/M' : loc}</TableCell>
                            {DAYS_OF_WEEK.map((day) => (
                              <TableCell key={day}>
                                {schedule.assignments?.[loc]?.[day] || ''}
                              </TableCell>
                            ))}
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                    <Box sx={{ mt: 1 }}>
                      <Button
                        variant="contained"
                        color="primary"
                        startIcon={<PublishIcon />}
                        onClick={() => handlePublishSchedule(schedule.id)}
                      >
                        Publish This On Call Schedule
                      </Button>
                      <Button
                        variant="outlined"
                        color="secondary"
                        sx={{ ml: 2 }}
                        onClick={() => handleDeleteSchedule(schedule.id)}
                      >
                        Delete
                      </Button>
                    </Box>
                  </Box>
                ))
              )}
            </Paper>
          )}
        </>
      )}

      {selectedTab === 1 && (
        <Box>
          {/* Published On Call schedules first */}
          {schedules.filter(s => s.status === 'published' && s.type === 'oncall').map((schedule, idx) => (
            <Box key={schedule.id} sx={{ mb: 4 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="subtitle1">Published On Call Schedule</Typography>
                <Button
                  variant="outlined"
                  color="secondary"
                  startIcon={<DeleteIcon />}
                  onClick={() => handleDeleteSchedule(schedule.id)}
                >
                  Delete
                </Button>
              </Box>
              <Typography color="text.secondary" sx={{ mb: 1 }}>
                Week of {format(schedule.weekStart, 'MMM d, yyyy')}
              </Typography>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell></TableCell>
                    {DAYS_OF_WEEK.map((day) => (
                      <TableCell key={day}>{day}</TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {['JDCH', 'WM'].map((loc) => (
                    <TableRow key={loc}>
                      <TableCell>On Call {loc === 'WM' ? 'W/M' : loc}</TableCell>
                      {DAYS_OF_WEEK.map((day) => (
                        <TableCell key={day}>
                          {schedule.assignments?.[loc]?.[day] || ''}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Box>
          ))}
          {/* Published Echo Lab schedules next */}
          <Grid container spacing={3}>
            {schedules
              .filter(schedule => schedule.status === 'published' && schedule.type === 'echolab')
              .map((schedule) => (
                <Grid item xs={12} key={schedule.id}>
                  <Card>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <Box>
                          <Typography variant="h6">{schedule.locationName}</Typography>
                          <Typography color="text.secondary">
                            Week of {format(schedule.weekStart, 'MMM d, yyyy')}
                          </Typography>
                        </Box>
                        <Button
                          variant="outlined"
                          color="secondary"
                          startIcon={<DeleteIcon />}
                          onClick={() => handleDeleteSchedule(schedule.id)}
                        >
                          Delete
                        </Button>
                      </Box>
                      <Box sx={{ mt: 2 }}>
                        <Paper sx={{ p: 2 }}>
                          <Table>
                            <TableHead>
                              <TableRow>
                                <TableCell>Employee</TableCell>
                                {DAYS_OF_WEEK.map((day) => (
                                  <TableCell key={day}>{day}</TableCell>
                                ))}
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {Object.keys(schedule.assignments).map((employee) => (
                                <TableRow key={employee}>
                                  <TableCell>{employee}</TableCell>
                                  {DAYS_OF_WEEK.map((day) => (
                                    <TableCell key={day}>
                                      {schedule.assignments[employee][day] || ''}
                                    </TableCell>
                                  ))}
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </Paper>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
          </Grid>
        </Box>
      )}

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingSchedule ? 'Edit Schedule' : 'Generate New Schedule'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}
            <FormControl fullWidth>
              <InputLabel>Schedule Type</InputLabel>
              <Select
                value={scheduleType}
                onChange={e => setScheduleType(e.target.value)}
              >
                {SCHEDULE_TYPES.map(type => (
                  <MenuItem key={type} value={type}>{type}</MenuItem>
                ))}
              </Select>
            </FormControl>
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Week Start Date"
                value={formData.weekStart}
                onChange={(date) => setFormData({
                  ...formData,
                  weekStart: date || new Date(),
                })}
              />
            </LocalizationProvider>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleGenerateSchedule}
            variant="contained"
            startIcon={<RefreshIcon />}
          >
            Generate Schedule
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Schedules; 