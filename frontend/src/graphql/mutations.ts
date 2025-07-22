import { gql } from '@apollo/client';

export const ADD_EMPLOYEE = gql`
  mutation AddEmployee($input: AddEmployeeInput!) {
    addEmployee(input: $input) {
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

export const UPDATE_EMPLOYEE = gql`
  mutation UpdateEmployee($id: UUID!, $input: AddEmployeeInput!) {
    updateEmployee(id: $id, input: $input) {
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

export const DELETE_EMPLOYEE = gql`
  mutation DeleteEmployee($id: UUID!) {
    deleteEmployee(id: $id)
  }
`;

export const ADD_LOCATION = gql`
  mutation AddLocation($input: AddLocationInput!) {
    addLocation(input: $input) {
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

export const UPDATE_LOCATION = gql`
  mutation UpdateLocation($id: UUID!, $input: AddLocationInput!) {
    updateLocation(id: $id, input: $input) {
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

export const DELETE_LOCATION = gql`
  mutation DeleteLocation($id: UUID!) {
    deleteLocation(id: $id)
  }
`;

export const GENERATE_SCHEDULE = gql`
  mutation GenerateSchedule($weekStart: Date!, $scheduleType: String!) {
    generateSchedule(weekStart: $weekStart, scheduleType: $scheduleType) {
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

export const PUBLISH_SCHEDULE = gql`
  mutation PublishSchedule($weekStart: Date!) {
    publishSchedule(weekStart: $weekStart) {
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

export const REQUEST_TIME_OFF = gql`
  mutation RequestTimeOff($input: TimeOffInput!) {
    requestTimeOff(input: $input) {
      id
      employeeId
      startDate
      endDate
      status
      requestDate
    }
  }
`;

export const UPDATE_TIME_OFF_STATUS = gql`
  mutation UpdateTimeOffStatus($id: UUID!, $status: TimeOffStatusGQL!) {
    updateTimeOffStatus(id: $id, status: $status) {
      id
      employeeId
      startDate
      endDate
      status
      requestDate
    }
  }
`;

export const UPDATE_TIME_OFF = gql`
  mutation UpdateTimeOff($id: UUID!, $input: TimeOffInput!, $status: TimeOffStatusGQL) {
    updateTimeOff(id: $id, input: $input, status: $status) {
      id
      employeeId
      startDate
      endDate
      status
      requestDate
    }
  }
`;

export const DELETE_TIME_OFF = gql`
  mutation DeleteTimeOff($id: UUID!) {
    deleteTimeOff(id: $id)
  }
`; 