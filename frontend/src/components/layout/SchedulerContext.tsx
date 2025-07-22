import React, { createContext, useContext, useState } from 'react';
import { useQuery, useMutation, ApolloClient, InMemoryCache, ApolloProvider } from '@apollo/client';
import { GET_EMPLOYEES, GET_LOCATIONS, GET_SCHEDULES } from '../../graphql/queries';
import { ADD_EMPLOYEE, UPDATE_EMPLOYEE, DELETE_EMPLOYEE, ADD_LOCATION, UPDATE_LOCATION, DELETE_LOCATION, GENERATE_SCHEDULE, PUBLISH_SCHEDULE, REQUEST_TIME_OFF, UPDATE_TIME_OFF_STATUS, UPDATE_TIME_OFF, DELETE_TIME_OFF } from '../../graphql/mutations';

// Create Apollo Client
const client = new ApolloClient({
  uri: 'http://localhost:8000/graphql',
  cache: new InMemoryCache(),
});

// Employee type
export interface Employee {
  id: string;
  name: string;
  role: 'staff' | 'student';
  availability: {
    days: string[];
    maxHoursPerDay: number;
    preferredShifts: string[];
  };
  timeOffRequests: {
    id: string;
    employeeId: string;
    startDate: string;
    endDate: string;
    status: 'pending' | 'approved' | 'denied';
    requestDate: string;
  }[];
}

// Location type
export interface Location {
  id: string;
  name: string;
  address?: string;
  requiredStaff?: {
    morning: number;
    afternoon: number;
    night: number;
  };
  notes?: string;
}

// Schedule type
export interface Schedule {
  id: string;
  locationId: string;
  locationName: string;
  weekStart: Date;
  assignments: any;
  status: 'draft' | 'published';
  type: string;
}

// Pending request type (placeholder)
export interface PendingRequest {
  id: string;
  employeeId: string;
  type: string;
  status: string;
}

interface SchedulerContextType {
  employees: Employee[];
  setEmployees: React.Dispatch<React.SetStateAction<Employee[]>>;
  locations: Location[];
  setLocations: React.Dispatch<React.SetStateAction<Location[]>>;
  schedules: Schedule[];
  setSchedules: React.Dispatch<React.SetStateAction<Schedule[]>>;
  pendingRequests: PendingRequest[];
  setPendingRequests: React.Dispatch<React.SetStateAction<PendingRequest[]>>;
  loading: boolean;
  error: any;
  addEmployee: any;
  updateEmployee: any;
  deleteEmployee: any;
  addLocation: any;
  updateLocation: any;
  deleteLocation: any;
  generateSchedule: any;
  publishSchedule: any;
  requestTimeOff: any;
  updateTimeOffStatus: any;
  updateTimeOff: any;
  deleteTimeOff: any;
}

const SchedulerContext = createContext<SchedulerContextType | undefined>(undefined);

export const SchedulerProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Queries
  const { data: employeesData, loading: employeesLoading, error: employeesError, refetch: refetchEmployees } = useQuery(GET_EMPLOYEES);
  const { data: locationsData, loading: locationsLoading, error: locationsError, refetch: refetchLocations } = useQuery(GET_LOCATIONS);
  const { data: schedulesData, loading: schedulesLoading, error: schedulesError, refetch: refetchSchedules } = useQuery(GET_SCHEDULES);

  // Local state for schedules (to allow frontend to manage draft schedules)
  const [localSchedules, setLocalSchedules] = useState<Schedule[]>([]);

  // Mutations
  const [addEmployee] = useMutation(ADD_EMPLOYEE, {
    onCompleted: () => refetchEmployees(),
  });
  const [updateEmployee] = useMutation(UPDATE_EMPLOYEE, {
    onCompleted: () => refetchEmployees(),
  });
  const [deleteEmployee] = useMutation(DELETE_EMPLOYEE, {
    onCompleted: () => refetchEmployees(),
  });
  const [addLocation] = useMutation(ADD_LOCATION, {
    onCompleted: () => refetchLocations(),
  });
  const [updateLocation] = useMutation(UPDATE_LOCATION, {
    onCompleted: () => refetchLocations(),
  });
  const [deleteLocation] = useMutation(DELETE_LOCATION, {
    onCompleted: () => refetchLocations(),
  });
  const [generateSchedule] = useMutation(GENERATE_SCHEDULE, {
    onCompleted: () => refetchSchedules(),
  });
  const [publishSchedule] = useMutation(PUBLISH_SCHEDULE, {
    onCompleted: () => refetchSchedules(),
  });

  const [requestTimeOff] = useMutation(REQUEST_TIME_OFF);
  const [updateTimeOffStatus] = useMutation(UPDATE_TIME_OFF_STATUS);
  const [updateTimeOff] = useMutation(UPDATE_TIME_OFF);
  const [deleteTimeOff] = useMutation(DELETE_TIME_OFF);

  // Transform backend data to frontend format
  const transformEmployees = (backendEmployees: any[]): Employee[] => {
    if (!backendEmployees) return [];
    
    return backendEmployees.map(emp => ({
      id: emp.id,
      name: emp.name,
      role: emp.role.toLowerCase() as 'staff' | 'student',
      availability: {
        days: emp.availability?.map((day: any) => {
          // Convert enum values back to full day names
          const dayMap: { [key: string]: string } = {
            'MON': 'Monday',
            'TUE': 'Tuesday', 
            'WED': 'Wednesday',
            'THU': 'Thursday',
            'FRI': 'Friday',
            'SAT': 'Saturday',
            'SUN': 'Sunday'
          };
          return dayMap[day] || day;
        }) || [],
        maxHoursPerDay: emp.maxHoursPerDay || 8,
        preferredShifts: emp.preferredShifts || [],
      },
      timeOffRequests: emp.timeOffRequests?.map((to: any) => ({
        id: to.id,
        employeeId: to.employeeId,
        startDate: to.startDate,
        endDate: to.endDate,
        status: to.status.toLowerCase() as 'pending' | 'approved' | 'denied',
        requestDate: to.requestDate,
      })) || [],
    }));
  };

  const transformLocations = (backendLocations: any[]): Location[] => {
    if (!backendLocations) return [];
    
    return backendLocations.map(loc => ({
      id: loc.id,
      name: loc.name,
      address: loc.address,
      requiredStaff: {
        morning: loc.requiredStaffMorning || 2,
        afternoon: loc.requiredStaffAfternoon || 2,
        night: loc.requiredStaffNight || 1,
      },
      notes: loc.notes,
    }));
  };

  const transformSchedules = (backendSchedules: any[]): Schedule[] => {
    if (!backendSchedules) return [];
    
    return backendSchedules.map(sched => ({
      id: sched.id,
      locationId: sched.locationId,
      locationName: sched.locationName,
      weekStart: new Date(sched.weekStart),
      assignments: sched.assignments,
      status: sched.status,
      type: sched.type,
    }));
  };

  // State
  const employees = transformEmployees(employeesData?.employees || []);
  const locations = transformLocations(locationsData?.locations || []);
  const backendSchedules = transformSchedules(schedulesData?.schedules || []);
  const pendingRequests: PendingRequest[] = []; // Placeholder for now

  // Combine backend schedules (published) with local schedules (drafts)
  const schedules = [...backendSchedules, ...localSchedules];

  const loading = employeesLoading || locationsLoading || schedulesLoading;
  const error = employeesError || locationsError || schedulesError;

  // Proper setter functions for local state management
  const setEmployees = () => {}; // Will be replaced with mutations
  const setLocations = () => {}; // Will be replaced with mutations
  const setSchedules = setLocalSchedules; // Use local state setter
  const setPendingRequests = () => {}; // Placeholder

  return (
    <SchedulerContext.Provider value={{ 
      employees, 
      setEmployees, 
      locations, 
      setLocations, 
      schedules, 
      setSchedules, 
      pendingRequests, 
      setPendingRequests,
      loading,
      error,
      addEmployee,
      updateEmployee,
      deleteEmployee,
      addLocation,
      updateLocation,
      deleteLocation,
      generateSchedule,
      publishSchedule,
      requestTimeOff,
      updateTimeOffStatus,
      updateTimeOff,
      deleteTimeOff,
    }}>
      {children}
    </SchedulerContext.Provider>
  );
};

export function useSchedulerContext() {
  const ctx = useContext(SchedulerContext);
  if (!ctx) throw new Error('useSchedulerContext must be used within a SchedulerProvider');
  return ctx;
}

// Export Apollo Provider wrapper
export const ApolloWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ApolloProvider client={client}>
    <SchedulerProvider>
      {children}
    </SchedulerProvider>
  </ApolloProvider>
); 