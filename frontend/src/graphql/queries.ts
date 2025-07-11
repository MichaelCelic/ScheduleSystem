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
      timeOffRequests {
        id
        employeeId
        startDate
        endDate
        status
        requestDate
      }
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
    employees {
      id
      name
      role
      timeOffRequests {
        id
        employeeId
        startDate
        endDate
        status
        requestDate
      }
    }
    locations {
      id
      name
    }
    publishedSchedules(weekStart: "2025-01-01") {
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

export const GET_TIME_OFF_REQUESTS = gql`
  query GetTimeOffRequests {
    timeOffRequests {
      id
      employeeId
      startDate
      endDate
      status
      requestDate
      employee {
        id
        name
      }
    }
  }
`;

export const GET_EMPLOYEE_TIME_OFF = gql`
  query GetEmployeeTimeOff($employeeId: UUID!) {
    employeeTimeOff(employeeId: $employeeId) {
      id
      employeeId
      startDate
      endDate
      status
      requestDate
    }
  }
`; 