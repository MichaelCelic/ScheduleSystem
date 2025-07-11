import { gql } from '@apollo/client';

export const GET_EMPLOYEES = gql`
  query GetEmployees {
    employees {
      id
      name
      age
      role
      maxHoursPerDay
      availability
      preferredShifts
    }
  }
`;

export const GET_LOCATIONS = gql`
  query GetLocations {
    locations {
      id
      name
      address
      requiredStaffMorning
      requiredStaffAfternoon
      requiredStaffNight
      notes
    }
  }
`;

export const GET_SCHEDULES = gql`
  query GetSchedules {
    previewSchedules(weekStart: "2025-07-14", scheduleType: "echolab") {
      id
      employeeId
      locationId
      date
      startTime
      endTime
      published
    }
  }
`; 