import React, { createContext, useContext, useState } from 'react';

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
}

const SchedulerContext = createContext<SchedulerContextType | undefined>(undefined);

export const SchedulerProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [employees, setEmployees] = useState<Employee[]>([
    {
      id: '1',
      name: 'Martha',
      role: 'staff',
      availability: {
        days: ['Monday', 'Tuesday', 'Thursday', 'Friday', 'Saturday'],
        maxHoursPerDay: 10.5,
        preferredShifts: ['Morning (6AM-2PM)', 'Afternoon (2PM-10PM)'],
      },
    },
    {
      id: '2',
      name: 'Grisel',
      role: 'staff',
      availability: {
        days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
        maxHoursPerDay: 8.5,
        preferredShifts: ['Morning (6AM-2PM)', 'Afternoon (2PM-10PM)'],
      },
    },
    {
      id: '3',
      name: 'Emilio',
      role: 'staff',
      availability: {
        days: ['Tuesday', 'Wednesday', 'Thursday', 'Friday'],
        maxHoursPerDay: 8.5,
        preferredShifts: ['Afternoon (2PM-10PM)', 'Night (10PM-6AM)'],
      },
    },
    {
      id: '4',
      name: 'Annie',
      role: 'staff',
      availability: {
        days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
        maxHoursPerDay: 8.5,
        preferredShifts: ['Morning (6AM-2PM)', 'Night (10PM-6AM)'],
      },
    },
    {
      id: '5',
      name: 'Angela',
      role: 'staff',
      availability: {
        days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
        maxHoursPerDay: 8.5,
        preferredShifts: ['Afternoon (2PM-10PM)', 'Night (10PM-6AM)'],
      },
    },
    {
      id: '6',
      name: 'Alexandra',
      role: 'staff',
      availability: {
        days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
        maxHoursPerDay: 8.5,
        preferredShifts: ['Morning (6AM-2PM)', 'Afternoon (2PM-10PM)'],
      },
    },
    {
      id: '7',
      name: 'Shannon',
      role: 'staff',
      availability: {
        days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
        maxHoursPerDay: 8.5,
        preferredShifts: ['Night (10PM-6AM)', 'Afternoon (2PM-10PM)'],
      },
    },
    {
      id: '8',
      name: 'Guadalupe',
      role: 'staff',
      availability: {
        days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
        maxHoursPerDay: 8.5,
        preferredShifts: ['Morning (6AM-2PM)', 'Night (10PM-6AM)'],
      },
    },
    {
      id: '9',
      name: 'William',
      role: 'student',
      availability: {
        days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday'],
        maxHoursPerDay: 8,
        preferredShifts: ['Morning (6AM-2PM)', 'Afternoon (2PM-10PM)', 'Night (10PM-6AM)'],
      },
    },
  ]);
  const [locations, setLocations] = useState<Location[]>([
    {
      id: 'location1',
      name: 'JDCH',
      address: '123 JDCH Ave',
      requiredStaff: {
        morning: 3,
        afternoon: 3,
        night: 2,
      },
      notes: '',
    },
    {
      id: 'location2',
      name: 'W/M',
      address: '456 W/M Blvd',
      requiredStaff: {
        morning: 2,
        afternoon: 2,
        night: 1,
      },
      notes: '',
    },
  ]);
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [pendingRequests, setPendingRequests] = useState<PendingRequest[]>([]);

  return (
    <SchedulerContext.Provider value={{ employees, setEmployees, locations, setLocations, schedules, setSchedules, pendingRequests, setPendingRequests }}>
      {children}
    </SchedulerContext.Provider>
  );
};

export function useSchedulerContext() {
  const ctx = useContext(SchedulerContext);
  if (!ctx) throw new Error('useSchedulerContext must be used within a SchedulerProvider');
  return ctx;
} 