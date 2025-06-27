import React from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
} from '@mui/material';
import {
  People as PeopleIcon,
  LocationOn as LocationIcon,
  Schedule as ScheduleIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { useSchedulerContext } from '../components/layout/SchedulerContext';

const Dashboard: React.FC = () => {
  const { employees, locations, schedules, pendingRequests } = useSchedulerContext();

  const stats = {
    totalEmployees: employees.length,
    totalLocations: locations.length,
    activeSchedules: schedules.filter(s => s.status === 'published').length,
    pendingRequests: pendingRequests.length,
  };

  const StatCard = ({ title, value, icon: Icon, color }: {
    title: string;
    value: number;
    icon: React.ElementType;
    color: string;
  }) => (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Icon sx={{ fontSize: 40, color, mr: 2 }} />
          <Typography variant="h4" component="div">
            {value}
          </Typography>
        </Box>
        <Typography color="text.secondary">
          {title}
        </Typography>
      </CardContent>
    </Card>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Employees"
            value={stats.totalEmployees}
            icon={PeopleIcon}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Locations"
            value={stats.totalLocations}
            icon={LocationIcon}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Schedules"
            value={stats.activeSchedules}
            icon={ScheduleIcon}
            color="#ed6c02"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Pending Requests"
            value={stats.pendingRequests}
            icon={WarningIcon}
            color="#d32f2f"
          />
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Welcome to Hospital Scheduler
            </Typography>
            <Typography paragraph>
              This dashboard provides an overview of your hospital's scheduling system.
              Use the navigation menu to manage employees, locations, and schedules.
            </Typography>
            <Typography>
              Get started by:
            </Typography>
            <ul>
              <li>Adding employees and their availability</li>
              <li>Setting up hospital locations and staffing requirements</li>
              <li>Generating and managing schedules</li>
            </ul>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard; 