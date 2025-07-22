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
import { addWeeks, format, startOfWeek, isWithinInterval, parseISO } from 'date-fns';
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
  'On Call Fetal': { [day: string]: string };
}

const DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
const ECHO_LAB_DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
const SHIFT_TYPES = ['Morning', 'Afternoon', 'Night'];
const SCHEDULE_TYPES = ['Echo Lab', 'On Call'];

const Schedules: React.FC = () => {
  const { schedules, setSchedules, employees, locations, generateSchedule, publishSchedule } = useSchedulerContext();
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

  const ON_CALL_LOCATIONS = ['JDCH', 'WM', 'On Call Fetal'];

  const ON_CALL_DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

  // Helper function to generate date labels for days of the week
  const getDateLabelsForWeek = (weekStart: Date): { [day: string]: string } => {
    const labels: { [day: string]: string } = {};
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    
    // Calculate the Monday of the selected week
    const monday = startOfWeek(weekStart, { weekStartsOn: 1 }); // 1 = Monday
    
    days.forEach((day, index) => {
      const date = new Date(monday);
      date.setDate(date.getDate() + index);
      labels[day] = `${day} (${format(date, 'M/d')})`;
    });
    
    return labels;
  };

  // Helper function to check if an employee has approved time-off for a specific date
  const hasApprovedTimeOff = (employee: any, targetDate: Date): boolean => {
    if (!employee.timeOffRequests || employee.timeOffRequests.length === 0) {
      return false;
    }

    return employee.timeOffRequests.some((timeOff: any) => {
      // Only check approved time-off requests
      if (timeOff.status !== 'approved') {
        return false;
      }

      const startDate = parseISO(timeOff.startDate);
      const endDate = parseISO(timeOff.endDate);
      
      // Check if the target date falls within the time-off period
      return isWithinInterval(targetDate, { start: startDate, end: endDate });
    });
  };

  // Helper function to get the day of week for a specific date
  const getDayOfWeek = (date: Date): string => {
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days[date.getDay()];
  };

  // Check if on-call schedule exists for the selected week
  const isOnCallSchedulePublished = (weekStart: Date): boolean => {
    const publishedOnCallSchedules = schedules.filter(s => 
      s.status === 'published' && 
      s.type === 'oncall' && 
      s.weekStart.getTime() === weekStart.getTime()
    );
    
    return publishedOnCallSchedules.length > 0;
  };

  // Check if echo lab generation is allowed
  const canGenerateEchoLab = (weekStart: Date): boolean => {
    return isOnCallSchedulePublished(weekStart);
  };

  // Get on-call status message
  const getOnCallStatusMessage = (weekStart: Date): string => {
    const publishedOnCallSchedules = schedules.filter(s => 
      s.status === 'published' && 
      s.type === 'oncall' && 
      s.weekStart.getTime() === weekStart.getTime()
    );
    
    if (publishedOnCallSchedules.length === 0) {
      return `No on-call schedule published for week of ${format(weekStart, 'MMM d, yyyy')}. Please publish an on-call schedule for this week first.`;
    }
    
    return `On-call schedule for week of ${format(weekStart, 'MMM d, yyyy')} is published. Echo lab schedule can be generated.`;
  };

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

  const NUM_DRAFT_SCHEDULES = 5; // Number of draft schedules to generate for Echo Lab
  const NUM_ONCALL_DRAFTS = 1; // Number of on-call draft schedules to generate (only 1 since it's manually editable)

  const handleGenerateSchedule = async () => {
    try {
      if (scheduleType === 'Echo Lab') {
        // Check if on-call schedule is complete before allowing echo lab generation
        if (!canGenerateEchoLab(formData.weekStart!)) {
          setError(getOnCallStatusMessage(formData.weekStart!));
          return;
        }
        
        if (!jdchLocation) {
          setError('JDCH location not found');
          return;
        }

        // Generate 5 different Echo Lab draft schedules
        const newSchedules: Schedule[] = [];
        const allDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
        
        // Business rules for assignments
        const assignmentOptions = ['Inpatients', 'Cath/Inpat.', 'OR/Inpat.', 'Sedat./Inpat.', 'MWH/MHM', 'THC', 'TX-Inpat.', 'MPG-Fetal', 'PTO', 'N/A'];
        
        // Get all staff employees (exclude students for Echo Lab)
        const staffEmployees = employees.filter(emp => emp.role === 'staff');
        
        // Find specific employees by name
        const emilio = staffEmployees.find(emp => emp.name === 'Emilio');
        const martha = staffEmployees.find(emp => emp.name === 'Martha');
        
        for (let i = 0; i < 5; i++) {
          // Create assignments for all employees
          const assignments: { [employeeName: string]: { [day: string]: string } } = {};
          
          staffEmployees.forEach(employee => {
            assignments[employee.name] = {};
            allDays.forEach((day, dayIndex) => {
              // Calculate the actual date for this day of the week
              const dayDate = new Date(formData.weekStart!);
              dayDate.setDate(dayDate.getDate() + dayIndex);
              
              // Check if employee has approved time-off for this specific date
              const hasTimeOff = hasApprovedTimeOff(employee, dayDate);
              
              // Apply business rules
              let assignment = '';
              
              // If employee has approved time-off for this date, assign PTO
              if (hasTimeOff) {
                assignment = 'PTO';
              }
              // Rule 1: Martha's assignments (respecting time-off)
              else if (employee.name === 'Martha') {
                if (day === 'Tuesday' || day === 'Friday') {
                  // Rule 2: Tx-IP on Tuesday and Friday only staffed by Martha
                  assignment = 'TX-Inpat.';
                } else {
                  // Random assignment for other days (avoid PTO for Martha on work days)
                  const workOptions = assignmentOptions.filter(opt => opt !== 'PTO');
                  assignment = workOptions[Math.floor(Math.random() * workOptions.length)];
                }
              }
              // Rule 3: THC is always staffed by Emilio (except Friday)
              else if (employee.name === 'Emilio' && day !== 'Friday') {
                assignment = 'THC';
              }
              // Rule 4: No THC clinic on Friday
              else if (day === 'Friday' && employee.name === 'Emilio') {
                assignment = assignmentOptions.filter(opt => opt !== 'THC')[Math.floor(Math.random() * (assignmentOptions.length - 1))];
              }
              else {
                // Random assignment for other employees/days (no random PTO)
                const workOptions = assignmentOptions.filter(opt => opt !== 'PTO');
                assignment = workOptions[Math.floor(Math.random() * workOptions.length)];
              }
              
              assignments[employee.name][day] = assignment;
            });
          });
          
          // Rule 5: Person assigned to JDCH call is OR/IP shift on that same assigned day
          // Get the on-call schedule for this week to apply this rule
          const onCallSchedule = schedules.find(s => 
            s.status === 'published' && 
            s.type === 'oncall' && 
            s.weekStart.getTime() === formData.weekStart!.getTime()
          );
          
          if (onCallSchedule) {
            allDays.forEach(day => {
              const jdchOnCallEmployee = onCallSchedule.assignments?.JDCH?.[day];
              if (jdchOnCallEmployee && assignments[jdchOnCallEmployee]) {
                assignments[jdchOnCallEmployee][day] = 'OR/Inpat.';
              }
            });
          }

          const newSchedule: Schedule = {
            id: Date.now().toString() + Math.random().toString(36).substring(2) + i,
            locationId: jdchLocation.id,
            locationName: jdchLocation.name,
            weekStart: formData.weekStart!,
            assignments: assignments,
            status: 'draft' as 'draft',
            type: 'echolab',
          };
          
          newSchedules.push(newSchedule);
        }

        // Add all new schedules to the state
        setSchedules(prev => [
          ...prev.filter(s => !(s.status === 'draft' && s.type === 'echolab')),
          ...newSchedules
        ]);
        setSelectedDraftTab(0); // Switch to Echo Lab tab
        handleCloseDialog();
      } else if (scheduleType === 'On Call') {
        // Call backend to generate on-call schedule
        const result = await generateSchedule({
          variables: {
            weekStart: formData.weekStart!.toISOString().split('T')[0], // Convert to YYYY-MM-DD format
            scheduleType: 'oncall'
          }
        });

        // Create on-call schedule structure
        const newOnCallSchedule = {
          id: Date.now().toString() + Math.random().toString(36).substring(2),
          locationId: 'oncall',
          locationName: 'On Call',
          weekStart: formData.weekStart!,
          assignments: { JDCH: {}, WM: {} } as any,
          status: 'draft' as 'draft',
          type: 'oncall',
        };

        // Always initialize all days for both locations
        const allDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
        const jdchAssignments: { [day: string]: string } = {};
        const wmAssignments: { [day: string]: string } = {};
        allDays.forEach(day => {
          jdchAssignments[day] = '';
          wmAssignments[day] = '';
        });

        // Don't auto-populate from backend shifts - let user manually assign
        // The backend generates the schedule but frontend should start with empty assignments
        // for manual editing

        // Assign to schedule
        newOnCallSchedule.assignments.JDCH = jdchAssignments;
        newOnCallSchedule.assignments.WM = wmAssignments;

        setSchedules(prev => [
          ...prev.filter(s => !(s.status === 'draft' && s.type === 'oncall')),
          newOnCallSchedule
        ]);
        setSelectedDraftTab(1); // Switch to On Call tab
        handleCloseDialog();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while generating the schedule');
    }
  };

  const handlePublishSchedule = async (scheduleId: string) => {
    try {
      const schedule = schedules.find(s => s.id === scheduleId);
      if (!schedule) return;

      // Call backend to publish schedule
      await publishSchedule({
        variables: {
          weekStart: schedule.weekStart.toISOString().split('T')[0] // Convert to YYYY-MM-DD format
        }
      });

      // Update local state
      setSchedules(schedules.map(s =>
        s.id === scheduleId
          ? { ...s, status: 'published' }
          : s
      ));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while publishing the schedule');
    }
  };

  const handleDeleteSchedule = (scheduleId: string) => {
    setSchedules(schedules.filter(schedule => schedule.id !== scheduleId));
  };

  // Handle manual on-call assignment
  const handleOnCallAssignment = (scheduleId: string, location: string, day: string, employeeName: string) => {
    setSchedules(schedules.map(schedule => {
      if (schedule.id === scheduleId) {
        return {
          ...schedule,
          assignments: {
            ...schedule.assignments,
            [location]: {
              ...schedule.assignments[location],
              [day]: employeeName
            }
          }
        };
      }
      return schedule;
    }));
  };

  // Handle echo lab assignment editing
  const handleEchoLabAssignment = (scheduleId: string, employeeName: string, day: string, assignment: string) => {
    setSchedules(schedules.map(schedule => {
      if (schedule.id === scheduleId) {
        return {
          ...schedule,
          assignments: {
            ...schedule.assignments,
            [employeeName]: {
              ...schedule.assignments[employeeName],
              [day]: assignment
            }
          }
        };
      }
      return schedule;
    }));
  };

  // Get list of employees assigned to on-call shifts for a specific week
  const getOnCallEmployeesForWeek = (weekStart: Date): string[] => {
    const publishedOnCallSchedules = schedules.filter(s => 
      s.status === 'published' && 
      s.type === 'oncall' && 
      s.weekStart.getTime() === weekStart.getTime()
    );
    
    if (publishedOnCallSchedules.length === 0) return [];
    
    const onCallSchedule = publishedOnCallSchedules[0];
    const assignedEmployees = new Set<string>();
    
    // Collect all unique employees assigned to on-call shifts
    for (const location of ON_CALL_LOCATIONS) {
      for (const day of ON_CALL_DAYS) {
        const employee = onCallSchedule.assignments?.[location]?.[day];
        if (employee && employee.trim() !== '') {
          assignedEmployees.add(employee);
        }
      }
    }
    
    return Array.from(assignedEmployees);
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
            <>
              {/* Show on-call dependency status */}
              <Paper sx={{ p: 2, mb: 3 }}>
                <Alert 
                  severity="info"
                  sx={{ mb: 2 }}
                >
                  <Typography variant="subtitle2" sx={{ mb: 1 }}>
                    Echo Lab Schedule Generation
                  </Typography>
                  <Typography>
                    To generate Echo Lab schedules, you must first create and publish a complete on-call schedule for the same week.
                  </Typography>
                  <Typography sx={{ mt: 1 }}>
                    Use the "Generate New Schedule" button above and select "Echo Lab" to check availability for specific weeks.
                  </Typography>
                </Alert>
                
                {/* Show published on-call schedules */}
                {schedules.filter(s => s.status === 'published' && s.type === 'oncall').length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" sx={{ mb: 1 }}>
                      Available Weeks for Echo Lab Generation:
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {schedules
                        .filter(s => s.status === 'published' && s.type === 'oncall')
                        .map((schedule) => (
                          <Chip
                            key={schedule.id}
                            label={`Week of ${format(schedule.weekStart, 'MMM d, yyyy')}`}
                            color="success"
                            variant="outlined"
                            size="small"
                          />
                        ))}
                    </Box>
                  </Box>
                )}
                
                <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
                  <Button
                    variant="outlined"
                    color="primary"
                    onClick={() => setSelectedDraftTab(1)}
                  >
                    Go to On Call Tab
                  </Button>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={() => handleOpenDialog()}
                  >
                    Generate New Schedule
                  </Button>
                </Box>
              </Paper>
              
              <Grid container spacing={3}>
                {schedules
                  .filter(schedule => schedule.status === 'draft' && schedule.type === 'echolab')
                  .map((schedule) => (
                    <Grid item xs={12} key={schedule.id}>
                      <Card>
                        <CardContent>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Box>
                                <Typography variant="h6">{schedule.locationName}</Typography>
                                <Typography color="text.secondary">
                                  Week of {format(schedule.weekStart, 'MMM d, yyyy')}
                                </Typography>
                              </Box>
                              <Chip label="Editable" color="info" size="small" />
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
                                    {ECHO_LAB_DAYS.map((day) => {
                                      const dateLabels = getDateLabelsForWeek(schedule.weekStart);
                                      return (
                                        <TableCell key={day}>{dateLabels[day] || day}</TableCell>
                                      );
                                    })}
                                  </TableRow>
                                </TableHead>
                                <TableBody>
                                  {Object.keys(schedule.assignments).map((employee) => (
                                    <TableRow key={employee}>
                                      <TableCell>{employee}</TableCell>
                                      {ECHO_LAB_DAYS.map((day) => (
                                        <TableCell key={day}>
                                          <FormControl size="small" fullWidth>
                                            <Select
                                              value={schedule.assignments[employee][day] || ''}
                                              onChange={(e) => handleEchoLabAssignment(schedule.id, employee, day, e.target.value)}
                                              displayEmpty
                                            >
                                              <MenuItem value="">
                                                <em>No Assignment</em>
                                              </MenuItem>
                                              <MenuItem value="Inpatients">Inpatients</MenuItem>
                                              <MenuItem value="Cath/Inpat.">Cath/Inpat.</MenuItem>
                                              <MenuItem value="OR/Inpat.">OR/Inpat.</MenuItem>
                                              <MenuItem value="Sedat./Inpat.">Sedat./Inpat.</MenuItem>
                                              <MenuItem value="MWH/MHM">MWH/MHM</MenuItem>
                                              <MenuItem value="THC">THC</MenuItem>
                                              <MenuItem value="TX-Inpat.">TX-Inpat.</MenuItem>
                                              <MenuItem value="MPG-Fetal">MPG-Fetal</MenuItem>
                                              <MenuItem value="PTO">PTO</MenuItem>
                                              <MenuItem value="N/A">N/A</MenuItem>
                                            </Select>
                                          </FormControl>
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
            </>
          )}
          {selectedDraftTab === 1 && (
            <Paper sx={{ p: 2, mb: 3 }}>
              {schedules.filter(s => s.status === 'draft' && s.type === 'oncall').length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    No On Call Schedule Generated Yet
                  </Typography>
                  <Typography color="text.secondary" sx={{ mb: 3 }}>
                    Generate an on-call schedule to manually assign employees to on-call shifts.
                  </Typography>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={() => handleOpenDialog()}
                  >
                    Generate On Call Schedule
                  </Button>
                </Box>
              ) : (
                schedules.filter(s => s.status === 'draft' && s.type === 'oncall').map((schedule, idx) => (
                  <Box key={schedule.id} sx={{ mb: 4 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Typography variant="subtitle1">On Call Schedule</Typography>
                      <Chip label="Editable" color="info" size="small" />
                    </Box>
                    <Typography color="text.secondary" sx={{ mb: 1 }}>
                      Week of {format(schedule.weekStart, 'MMM d, yyyy')}
                    </Typography>
                    <Box sx={{ overflow: 'hidden', borderRadius: 1 }}>
                      <Table sx={{
                        '& .MuiTableCell-root': {
                          paddingLeft: 1,
                          paddingRight: 1
                        }
                      }}>
                        <TableHead>
                          <TableRow>
                            <TableCell></TableCell>
                            {ON_CALL_DAYS.map((day) => (
                              <TableCell key={day}>{day}</TableCell>
                            ))}
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {ON_CALL_LOCATIONS.map((loc) => (
                            <TableRow key={loc}>
                              <TableCell>On Call {loc === 'WM' ? 'W/M' : loc === 'On Call Fetal' ? 'Fetal' : loc}</TableCell>
                              {ON_CALL_DAYS.map((day) => (
                                <TableCell key={day}>
                                  <FormControl size="small" fullWidth>
                                    <Select
                                      value={schedule.assignments?.[loc]?.[day] || ''}
                                      onChange={(e) => handleOnCallAssignment(schedule.id, loc, day, e.target.value)}
                                      displayEmpty
                                    >
                                      <MenuItem value="">
                                        <em>Select Employee</em>
                                      </MenuItem>
                                      {employees
                                        .filter(emp => emp.role !== 'student') // Exclude students from on-call
                                        .map((emp) => (
                                          <MenuItem key={emp.id} value={emp.name}>
                                            {emp.name}
                                          </MenuItem>
                                        ))}
                                    </Select>
                                  </FormControl>
                                </TableCell>
                              ))}
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </Box>
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
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="subtitle1">Published On Call Schedule</Typography>
                  <Chip label="Editable" color="info" size="small" />
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
              <Typography color="text.secondary" sx={{ mb: 1 }}>
                Week of {format(schedule.weekStart, 'MMM d, yyyy')}
              </Typography>
              
              {/* Show completion status */}
              <Alert 
                severity="success"
                sx={{ mb: 2 }}
              >
                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                  On-Call Schedule Status
                </Typography>
                <Typography>
                  On-call schedule for week of {format(schedule.weekStart, 'MMM d, yyyy')} is published - Echo Lab schedules can be generated for this week
                </Typography>
              </Alert>
              
              <Box sx={{ overflow: 'hidden', borderRadius: 1 }}>
                <Table sx={{
                  '& .MuiTableCell-root': {
                    paddingLeft: 1,
                    paddingRight: 1
                  }
                }}>
                  <TableHead>
                    <TableRow>
                      <TableCell></TableCell>
                      {ON_CALL_DAYS.map((day) => (
                        <TableCell key={day}>{day}</TableCell>
                      ))}
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {ON_CALL_LOCATIONS.map((loc) => (
                      <TableRow key={loc}>
                        <TableCell>On Call {loc === 'WM' ? 'W/M' : loc === 'On Call Fetal' ? 'Fetal' : loc}</TableCell>
                        {ON_CALL_DAYS.map((day) => (
                          <TableCell key={day}>
                            <FormControl size="small" fullWidth>
                              <Select
                                value={schedule.assignments?.[loc]?.[day] || ''}
                                onChange={(e) => handleOnCallAssignment(schedule.id, loc, day, e.target.value)}
                                displayEmpty
                              >
                                <MenuItem value="">
                                  <em>Select Employee</em>
                                </MenuItem>
                                {employees
                                  .filter(emp => emp.role !== 'student') // Exclude students from on-call
                                  .map((emp) => (
                                    <MenuItem key={emp.id} value={emp.name}>
                                      {emp.name}
                                    </MenuItem>
                                  ))}
                              </Select>
                            </FormControl>
                          </TableCell>
                        ))}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </Box>
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
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Box>
                            <Typography variant="h6">{schedule.locationName}</Typography>
                            <Typography color="text.secondary">
                              Week of {format(schedule.weekStart, 'MMM d, yyyy')}
                            </Typography>
                          </Box>
                          <Chip label="Editable" color="info" size="small" />
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
                                {ECHO_LAB_DAYS.map((day) => {
                                  const dateLabels = getDateLabelsForWeek(schedule.weekStart);
                                  return (
                                    <TableCell key={day}>{dateLabels[day] || day}</TableCell>
                                  );
                                })}
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {Object.keys(schedule.assignments).map((employee) => (
                                <TableRow key={employee}>
                                  <TableCell>{employee}</TableCell>
                                  {ECHO_LAB_DAYS.map((day) => (
                                    <TableCell key={day}>
                                      <FormControl size="small" fullWidth>
                                        <Select
                                          value={schedule.assignments[employee][day] || ''}
                                          onChange={(e) => handleEchoLabAssignment(schedule.id, employee, day, e.target.value)}
                                          displayEmpty
                                        >
                                          <MenuItem value="">
                                            <em>No Assignment</em>
                                          </MenuItem>
                                          <MenuItem value="Inpatients">Inpatients</MenuItem>
                                          <MenuItem value="Cath/Inpat.">Cath/Inpat.</MenuItem>
                                          <MenuItem value="OR/Inpat.">OR/Inpat.</MenuItem>
                                          <MenuItem value="Sedat./Inpat.">Sedat./Inpat.</MenuItem>
                                          <MenuItem value="MWH/MHM">MWH/MHM</MenuItem>
                                          <MenuItem value="THC">THC</MenuItem>
                                          <MenuItem value="TX-Inpat.">TX-Inpat.</MenuItem>
                                          <MenuItem value="MPG-Fetal">MPG-Fetal</MenuItem>
                                          <MenuItem value="PTO">PTO</MenuItem>
                                          <MenuItem value="N/A">N/A</MenuItem>
                                        </Select>
                                      </FormControl>
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
            
            {/* Show on-call status when Echo Lab is selected */}
            {scheduleType === 'Echo Lab' && formData.weekStart && (
              <Alert 
                severity={canGenerateEchoLab(formData.weekStart) ? 'success' : 'warning'}
                sx={{ mt: 2 }}
              >
                {getOnCallStatusMessage(formData.weekStart)}
              </Alert>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleGenerateSchedule}
            variant="contained"
            startIcon={<RefreshIcon />}
            disabled={scheduleType === 'Echo Lab' && formData.weekStart && !canGenerateEchoLab(formData.weekStart)}
          >
            Generate Schedule
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Schedules; 