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
  mutation GenerateSchedule($locationId: UUID!, $weekStart: Date!) {
    generateSchedule(locationId: $locationId, weekStart: $weekStart) {
      id
      locationId
      locationName
      weekStart
      assignments
      status
      type
    }
  }
`;

export const PUBLISH_SCHEDULE = gql`
  mutation PublishSchedule($id: UUID!) {
    publishSchedule(id: $id) {
      id
      status
    }
  }
`; 