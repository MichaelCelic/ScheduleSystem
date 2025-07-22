import strawberry
from typing import List, Optional
from datetime import date
import uuid
from sqlmodel import select, delete
from .models import Employee, Location, Shift, EmployeeAvailabilityLink, EmployeeRole, TimeOff, TimeOffStatus
from .graphql_types import EmployeeType, LocationType, ShiftType, AddEmployeeInput, AddLocationInput, DayOfWeekGQL, EmployeeRoleGQL, TimeOffType, TimeOffInput, TimeOffStatusGQL
from .database import get_session
from .scheduler import generate_weekly_schedule, can_generate_echo_lab_schedule, check_oncall_schedule_published
from .models import DayOfWeek
from .logger import logger, log_business_rule, log_schedule_generation

@strawberry.type
class Query:
    @strawberry.field
    def employees(self) -> List[EmployeeType]:
        logger.info("Fetching all employees")
        try:
            with get_session() as session:
                employees = session.exec(select(Employee)).all()
                logger.info(f"Successfully fetched {len(employees)} employees")
                return [EmployeeType(
                    id=e.id, 
                    name=e.name, 
                    age=e.age, 
                    role=EmployeeRoleGQL(e.role.value),
                    availability=[DayOfWeekGQL(day.value) for day in e.availability], 
                    max_hours_per_day=e.max_hours_per_day,
                    preferred_shifts=e.preferred_shifts,
                    time_off_requests=[TimeOffType(
                        id=to.id,
                        employee_id=to.employee_id,
                        start_date=to.start_date,
                        end_date=to.end_date,
                        status=TimeOffStatusGQL(to.status.value),
                        request_date=to.request_date,
                        employee=EmployeeType(
                            id=e.id,
                            name=e.name,
                            age=e.age,
                            role=EmployeeRoleGQL(e.role.value),
                            availability=[DayOfWeekGQL(day.value) for day in e.availability],
                            max_hours_per_day=e.max_hours_per_day,
                            preferred_shifts=e.preferred_shifts,
                            time_off_requests=[]
                        )
                    ) for to in e.time_off_requests]
                ) for e in employees]
        except Exception as e:
            logger.error(f"Failed to fetch employees: {e}")
            raise

    @strawberry.field
    def locations(self) -> List[LocationType]:
        logger.info("Fetching all locations")
        try:
            with get_session() as session:
                locations = session.exec(select(Location)).all()
                logger.info(f"Successfully fetched {len(locations)} locations")
                return [LocationType(
                    id=l.id, 
                    name=l.name,
                    address=l.address,
                    required_staff_morning=l.required_staff_morning,
                    required_staff_afternoon=l.required_staff_afternoon,
                    required_staff_night=l.required_staff_night,
                    notes=l.notes
                ) for l in locations]
        except Exception as e:
            logger.error(f"Failed to fetch locations: {e}")
            raise

    @strawberry.field
    def previewSchedules(self, weekStart: date, scheduleType: str = "echolab") -> List[ShiftType]:
        logger.info(f"Generating preview schedule for {scheduleType} starting {weekStart}")
        try:
            with get_session() as session:
                employees = session.exec(select(Employee)).all()
                locations = session.exec(select(Location)).all()
                
                # Get published on-call shifts for echo lab dependencies
                published_oncall_shifts = []
                if scheduleType == "echolab":
                    published_shifts = session.exec(select(Shift).where(Shift.published == True)).all()
                    published_oncall_shifts = [
                        shift for shift in published_shifts
                        if shift.location.name in ['JDCH', 'W/M']
                    ]
                
                shifts = generate_weekly_schedule(
                    weekStart, employees, locations, scheduleType, published_oncall_shifts
                )
                
                log_schedule_generation(
                    schedule_type=scheduleType,
                    week_start=str(weekStart),
                    employee_count=len(employees),
                    success=True
                )
                
                logger.info(f"Successfully generated {len(shifts)} preview shifts")
                return [ShiftType(
                    id=s.id, employee_id=s.employee_id, location_id=s.location_id, date=s.date,
                    start_time=s.start_time, end_time=s.end_time, published=s.published
                ) for s in shifts]
        except Exception as e:
            log_schedule_generation(
                schedule_type=scheduleType,
                week_start=str(weekStart),
                employee_count=0,
                success=False,
                error=str(e)
            )
            logger.error(f"Failed to generate preview schedule: {e}")
            raise

    @strawberry.field
    def publishedSchedules(self, weekStart: date) -> List[ShiftType]:
        logger.info(f"Fetching published schedules for week starting {weekStart}")
        try:
            with get_session() as session:
                shifts = session.exec(select(Shift).where(Shift.date >= weekStart, Shift.published == True)).all()
                logger.info(f"Successfully fetched {len(shifts)} published shifts")
                return [ShiftType(
                    id=s.id, employee_id=s.employee_id, location_id=s.location_id, date=s.date,
                    start_time=s.start_time, end_time=s.end_time, published=s.published
                ) for s in shifts]
        except Exception as e:
            logger.error(f"Failed to fetch published schedules: {e}")
            raise

    @strawberry.field
    def oncallSchedulePublished(self, weekStart: date) -> bool:
        """Check if on-call schedule is published for the given week"""
        logger.info(f"Checking if on-call schedule is published for week starting {weekStart}")
        try:
            with get_session() as session:
                published_shifts = session.exec(select(Shift).where(Shift.published == True)).all()
                result = check_oncall_schedule_published(weekStart, published_shifts)
                
                log_business_rule(
                    rule_name="oncall_schedule_published_check",
                    details={"week_start": str(weekStart), "result": result},
                    success=True
                )
                
                logger.info(f"On-call schedule published check result: {result}")
                return result
        except Exception as e:
            log_business_rule(
                rule_name="oncall_schedule_published_check",
                details={"week_start": str(weekStart), "error": str(e)},
                success=False
            )
            logger.error(f"Failed to check on-call schedule published status: {e}")
            raise

    @strawberry.field
    def canGenerateEchoLab(self, weekStart: date) -> bool:
        """Check if echo lab schedule can be generated for the given week"""
        logger.info(f"Checking if echo lab schedule can be generated for week starting {weekStart}")
        try:
            with get_session() as session:
                published_shifts = session.exec(select(Shift).where(Shift.published == True)).all()
                result = can_generate_echo_lab_schedule(weekStart, published_shifts)
                
                log_business_rule(
                    rule_name="echo_lab_generation_check",
                    details={"week_start": str(weekStart), "result": result},
                    success=True
                )
                
                logger.info(f"Echo lab generation check result: {result}")
                return result
        except Exception as e:
            log_business_rule(
                rule_name="echo_lab_generation_check",
                details={"week_start": str(weekStart), "error": str(e)},
                success=False
            )
            logger.error(f"Failed to check echo lab generation capability: {e}")
            raise

    @strawberry.field
    def timeOffRequests(self) -> List[TimeOffType]:
        """Get all time off requests"""
        logger.info("Fetching all time off requests")
        try:
            with get_session() as session:
                # Use select with join to load employee data
                from sqlmodel import select
                time_off_requests = session.exec(
                    select(TimeOff, Employee)
                    .join(Employee, TimeOff.employee_id == Employee.id)
                ).all()
                
                logger.info(f"Successfully fetched {len(time_off_requests)} time off requests")
                return [TimeOffType(
                    id=to.id,
                    employee_id=to.employee_id,
                    start_date=to.start_date,
                    end_date=to.end_date,
                    status=TimeOffStatusGQL(to.status.value),
                    request_date=to.request_date,
                    employee=EmployeeType(
                        id=emp.id,
                        name=emp.name,
                        age=emp.age,
                        role=EmployeeRoleGQL(emp.role.value),
                        availability=[],
                        max_hours_per_day=emp.max_hours_per_day,
                        preferred_shifts=[],
                        time_off_requests=[]
                    )
                ) for to, emp in time_off_requests]
        except Exception as e:
            logger.error(f"Failed to fetch time off requests: {e}")
            raise

    @strawberry.field
    def employeeTimeOff(self, employee_id: uuid.UUID) -> List[TimeOffType]:
        """Get time off requests for a specific employee"""
        logger.info(f"Fetching time off requests for employee {employee_id}")
        try:
            with get_session() as session:
                # Get employee and time off requests
                employee = session.get(Employee, employee_id)
                if not employee:
                    logger.warning(f"Employee not found: {employee_id}")
                    raise Exception("Employee not found")
                    
                time_off_requests = session.exec(
                    select(TimeOff).where(TimeOff.employee_id == employee_id)
                ).all()
                
                logger.info(f"Successfully fetched {len(time_off_requests)} time off requests for employee {employee_id}")
                return [TimeOffType(
                    id=to.id,
                    employee_id=to.employee_id,
                    start_date=to.start_date,
                    end_date=to.end_date,
                    status=TimeOffStatusGQL(to.status.value),
                    request_date=to.request_date,
                    employee=EmployeeType(
                        id=employee.id,
                        name=employee.name,
                        age=employee.age,
                        role=EmployeeRoleGQL(employee.role.value),
                        availability=[],
                        max_hours_per_day=employee.max_hours_per_day,
                        preferred_shifts=[],
                        time_off_requests=[]
                    )
                ) for to in time_off_requests]
        except Exception as e:
            logger.error(f"Failed to fetch time off requests for employee {employee_id}: {e}")
            raise

@strawberry.type
class Mutation:
    @strawberry.mutation
    def addEmployee(self, input: AddEmployeeInput) -> EmployeeType:
        logger.info(f"Adding new employee: {input.name}")
        try:
            with get_session() as session:
                employee = Employee(
                    name=input.name,
                    age=input.age,
                    role=EmployeeRole(input.role.value),
                    max_hours_per_day=input.max_hours_per_day
                )
                session.add(employee)
                session.commit()
                session.refresh(employee)
                
                # Add availability links
                for day in input.availability:
                    availability_link = EmployeeAvailabilityLink(
                        employee_id=employee.id,
                        day=DayOfWeek(day.value),
                        preferred_shifts=",".join(input.preferred_shifts)
                    )
                    session.add(availability_link)
                
                session.commit()
                session.refresh(employee)
                
                # Get availability for return
                availability_links = session.exec(
                    select(EmployeeAvailabilityLink).where(EmployeeAvailabilityLink.employee_id == employee.id)
                ).all()
                
                logger.info(f"Successfully added employee {input.name} with ID {employee.id}")
                return EmployeeType(
                    id=employee.id, 
                    name=employee.name, 
                    age=employee.age,
                    role=EmployeeRoleGQL(employee.role.value),
                    availability=[DayOfWeekGQL(link.day.value) for link in availability_links], 
                    max_hours_per_day=employee.max_hours_per_day,
                    preferred_shifts=input.preferred_shifts,
                    time_off_requests=[]
                )
        except Exception as e:
            logger.error(f"Failed to add employee {input.name}: {e}")
            raise

    @strawberry.mutation
    def updateEmployee(self, id: uuid.UUID, input: AddEmployeeInput) -> EmployeeType:
        logger.info(f"Updating employee {id}: {input.name}")
        try:
            with get_session() as session:
                employee = session.get(Employee, id)
                if not employee:
                    logger.warning(f"Employee not found for update: {id}")
                    raise Exception("Employee not found")
                
                employee.name = input.name
                employee.age = input.age
                employee.role = EmployeeRole(input.role.value)
                employee.max_hours_per_day = input.max_hours_per_day
                
                # Remove existing availability links
                session.exec(delete(EmployeeAvailabilityLink).where(EmployeeAvailabilityLink.employee_id == id))
                
                # Add new availability links
                for day in input.availability:
                    availability_link = EmployeeAvailabilityLink(
                        employee_id=employee.id,
                        day=DayOfWeek(day.value),
                        preferred_shifts=",".join(input.preferred_shifts)
                    )
                    session.add(availability_link)
                
                session.commit()
                session.refresh(employee)
                
                # Get availability for return
                availability_links = session.exec(
                    select(EmployeeAvailabilityLink).where(EmployeeAvailabilityLink.employee_id == employee.id)
                ).all()
                
                logger.info(f"Successfully updated employee {input.name} with ID {id}")
                return EmployeeType(
                    id=employee.id, 
                    name=employee.name, 
                    age=employee.age,
                    role=EmployeeRoleGQL(employee.role.value),
                    availability=[DayOfWeekGQL(link.day.value) for link in availability_links], 
                    max_hours_per_day=employee.max_hours_per_day,
                    preferred_shifts=input.preferred_shifts,
                    time_off_requests=[TimeOffType(
                        id=to.id,
                        employee_id=to.employee_id,
                        start_date=to.start_date,
                        end_date=to.end_date,
                        status=TimeOffStatusGQL(to.status.value),
                        request_date=to.request_date,
                        employee=EmployeeType(
                            id=employee.id,
                            name=employee.name,
                            age=employee.age,
                            role=EmployeeRoleGQL(employee.role.value),
                            availability=[],
                            max_hours_per_day=employee.max_hours_per_day,
                            preferred_shifts=[],
                            time_off_requests=[]
                        )
                    ) for to in employee.time_off_requests]
                )
        except Exception as e:
            logger.error(f"Failed to update employee {id}: {e}")
            raise

    @strawberry.mutation
    def deleteEmployee(self, id: uuid.UUID) -> bool:
        logger.info(f"Deleting employee {id}")
        try:
            with get_session() as session:
                employee = session.get(Employee, id)
                if not employee:
                    logger.warning(f"Employee not found for deletion: {id}")
                    return False
                
                # Delete related EmployeeAvailabilityLink records first
                session.exec(delete(EmployeeAvailabilityLink).where(EmployeeAvailabilityLink.employee_id == id))
                
                # Delete related Shift records
                session.exec(delete(Shift).where(Shift.employee_id == id))
                
                # Now delete the employee
                session.delete(employee)
                session.commit()
                
                logger.info(f"Successfully deleted employee {id}")
                return True
        except Exception as e:
            logger.error(f"Failed to delete employee {id}: {e}")
            raise

    @strawberry.mutation
    def addLocation(self, input: AddLocationInput) -> LocationType:
        logger.info(f"Adding new location: {input.name}")
        try:
            with get_session() as session:
                location = Location(
                    name=input.name,
                    address=input.address,
                    required_staff_morning=input.required_staff_morning,
                    required_staff_afternoon=input.required_staff_afternoon,
                    required_staff_night=input.required_staff_night,
                    notes=input.notes
                )
                session.add(location)
                session.commit()
                session.refresh(location)
                
                logger.info(f"Successfully added location {input.name} with ID {location.id}")
                return LocationType(
                    id=location.id,
                    name=location.name,
                    address=location.address,
                    required_staff_morning=location.required_staff_morning,
                    required_staff_afternoon=location.required_staff_afternoon,
                    required_staff_night=location.required_staff_night,
                    notes=location.notes
                )
        except Exception as e:
            logger.error(f"Failed to add location {input.name}: {e}")
            raise

    @strawberry.mutation
    def updateLocation(self, id: uuid.UUID, input: AddLocationInput) -> LocationType:
        logger.info(f"Updating location {id}: {input.name}")
        try:
            with get_session() as session:
                location = session.get(Location, id)
                if not location:
                    logger.warning(f"Location not found for update: {id}")
                    raise Exception("Location not found")
                
                location.name = input.name
                location.address = input.address
                location.required_staff_morning = input.required_staff_morning
                location.required_staff_afternoon = input.required_staff_afternoon
                location.required_staff_night = input.required_staff_night
                location.notes = input.notes
                
                session.commit()
                session.refresh(location)
                
                logger.info(f"Successfully updated location {input.name} with ID {id}")
                return LocationType(
                    id=location.id,
                    name=location.name,
                    address=location.address,
                    required_staff_morning=location.required_staff_morning,
                    required_staff_afternoon=location.required_staff_afternoon,
                    required_staff_night=location.required_staff_night,
                    notes=location.notes
                )
        except Exception as e:
            logger.error(f"Failed to update location {id}: {e}")
            raise

    @strawberry.mutation
    def deleteLocation(self, id: uuid.UUID) -> bool:
        logger.info(f"Deleting location {id}")
        try:
            with get_session() as session:
                location = session.get(Location, id)
                if not location:
                    logger.warning(f"Location not found for deletion: {id}")
                    return False
                session.delete(location)
                session.commit()
                
                logger.info(f"Successfully deleted location {id}")
                return True
        except Exception as e:
            logger.error(f"Failed to delete location {id}: {e}")
            raise

    @strawberry.mutation
    def generateSchedule(self, weekStart: date, scheduleType: str = "echolab") -> List[ShiftType]:
        logger.info(f"Generating schedule for {scheduleType} starting {weekStart}")
        try:
            with get_session() as session:
                # For echo lab schedules, check if on-call is complete first
                if scheduleType == "echolab":
                    published_shifts = session.exec(select(Shift).where(Shift.published == True)).all()
                    if not can_generate_echo_lab_schedule(weekStart, published_shifts):
                        logger.warning(f"Cannot generate echo lab schedule - on-call schedule not complete for week {weekStart}")
                        raise Exception("On-call schedule must be complete before generating echo lab schedule")
                    
                    # Get published on-call shifts for dependencies
                    published_oncall_shifts = [
                        shift for shift in published_shifts
                        if shift.location.name in ['JDCH', 'W/M']
                    ]
                else:
                    published_oncall_shifts = []
                
                employees = session.exec(select(Employee)).all()
                locations = session.exec(select(Location)).all()
                shifts = generate_weekly_schedule(
                    weekStart, employees, locations, scheduleType, published_oncall_shifts
                )
                
                # Optionally, store these shifts in DB with published=False
                for s in shifts:
                    session.add(s)
                session.commit()
                
                log_schedule_generation(
                    schedule_type=scheduleType,
                    week_start=str(weekStart),
                    employee_count=len(employees),
                    success=True
                )
                
                logger.info(f"Successfully generated {len(shifts)} shifts for {scheduleType}")
                return [ShiftType(
                    id=s.id, employee_id=s.employee_id, location_id=s.location_id, date=s.date,
                    start_time=s.start_time, end_time=s.end_time, published=s.published
                ) for s in shifts]
        except Exception as e:
            log_schedule_generation(
                schedule_type=scheduleType,
                week_start=str(weekStart),
                employee_count=0,
                success=False,
                error=str(e)
            )
            logger.error(f"Failed to generate schedule for {scheduleType}: {e}")
            raise

    @strawberry.mutation
    def publishSchedule(self, weekStart: date) -> List[ShiftType]:
        logger.info(f"Publishing schedule for week starting {weekStart}")
        try:
            with get_session() as session:
                shifts = session.exec(select(Shift).where(Shift.date >= weekStart)).all()
                for s in shifts:
                    s.published = True
                    session.add(s)
                session.commit()
                
                logger.info(f"Successfully published {len(shifts)} shifts for week starting {weekStart}")
                return [ShiftType(
                    id=s.id, employee_id=s.employee_id, location_id=s.location_id, date=s.date,
                    start_time=s.start_time, end_time=s.end_time, published=s.published
                ) for s in shifts]
        except Exception as e:
            logger.error(f"Failed to publish schedule for week {weekStart}: {e}")
            raise

    @strawberry.mutation
    def requestTimeOff(self, input: TimeOffInput) -> TimeOffType:
        """Request time off for an employee"""
        logger.info(f"Requesting time off for employee {input.employee_id} from {input.start_date} to {input.end_date}")
        try:
            with get_session() as session:
                # Validate that the employee exists
                employee = session.get(Employee, input.employee_id)
                if not employee:
                    logger.warning(f"Employee not found for time off request: {input.employee_id}")
                    raise Exception("Employee not found")
                
                # Validate date range
                if input.start_date > input.end_date:
                    logger.warning(f"Invalid date range for time off request: {input.start_date} to {input.end_date}")
                    raise Exception("Start date must be before or equal to end date")
                
                # Create time off request
                time_off = TimeOff(
                    employee_id=input.employee_id,
                    start_date=input.start_date,
                    end_date=input.end_date,
                    status=TimeOffStatus.PENDING
                )
                
                session.add(time_off)
                session.commit()
                session.refresh(time_off)
                
                logger.info(f"Successfully created time off request {time_off.id} for employee {input.employee_id}")
                return TimeOffType(
                    id=time_off.id,
                    employee_id=time_off.employee_id,
                    start_date=time_off.start_date,
                    end_date=time_off.end_date,
                    status=TimeOffStatusGQL(time_off.status.value),
                    request_date=time_off.request_date,
                    employee=EmployeeType(
                        id=employee.id,
                        name=employee.name,
                        age=employee.age,
                        role=EmployeeRoleGQL(employee.role.value),
                        availability=[],
                        max_hours_per_day=employee.max_hours_per_day,
                        preferred_shifts=[],
                        time_off_requests=[]
                    )
                )
        except Exception as e:
            logger.error(f"Failed to request time off for employee {input.employee_id}: {e}")
            raise

    @strawberry.mutation
    def updateTimeOffStatus(self, id: uuid.UUID, status: TimeOffStatusGQL) -> TimeOffType:
        """Update the status of a time off request (approve/deny)"""
        logger.info(f"Updating time off request {id} status to {status.value}")
        try:
            with get_session() as session:
                time_off = session.get(TimeOff, id)
                if not time_off:
                    logger.warning(f"Time off request not found: {id}")
                    raise Exception("Time off request not found")
                
                # Get the employee for the time off request
                employee = session.get(Employee, time_off.employee_id)
                if not employee:
                    logger.warning(f"Employee not found for time off request {id}: {time_off.employee_id}")
                    raise Exception("Employee not found")
                
                time_off.status = TimeOffStatus(status.value)
                session.add(time_off)
                session.commit()
                session.refresh(time_off)
                
                logger.info(f"Successfully updated time off request {id} status to {status.value}")
                return TimeOffType(
                    id=time_off.id,
                    employee_id=time_off.employee_id,
                    start_date=time_off.start_date,
                    end_date=time_off.end_date,
                    status=TimeOffStatusGQL(time_off.status.value),
                    request_date=time_off.request_date,
                    employee=EmployeeType(
                        id=employee.id,
                        name=employee.name,
                        age=employee.age,
                        role=EmployeeRoleGQL(employee.role.value),
                        availability=[],
                        max_hours_per_day=employee.max_hours_per_day,
                        preferred_shifts=[],
                        time_off_requests=[]
                    )
                )
        except Exception as e:
            logger.error(f"Failed to update time off request {id} status: {e}")
            raise

    @strawberry.mutation
    def updateTimeOff(self, id: uuid.UUID, input: TimeOffInput, status: Optional[TimeOffStatusGQL] = None) -> TimeOffType:
        """Update a time off request (dates and optionally status)"""
        logger.info(f"Updating time off request {id} with new data")
        try:
            with get_session() as session:
                time_off = session.get(TimeOff, id)
                if not time_off:
                    logger.warning(f"Time off request not found: {id}")
                    raise Exception("Time off request not found")
                
                # Get the employee for the time off request
                employee = session.get(Employee, time_off.employee_id)
                if not employee:
                    logger.warning(f"Employee not found for time off request {id}: {time_off.employee_id}")
                    raise Exception("Employee not found")
                
                # Validate date range
                if input.start_date > input.end_date:
                    logger.warning(f"Invalid date range for time off update: {input.start_date} to {input.end_date}")
                    raise Exception("Start date must be before or equal to end date")
                
                # Update the time off request
                time_off.start_date = input.start_date
                time_off.end_date = input.end_date
                
                # Update status if provided
                if status is not None:
                    time_off.status = TimeOffStatus(status.value)
                    logger.info(f"Also updating status to {status.value}")
                
                session.add(time_off)
                session.commit()
                session.refresh(time_off)
                
                logger.info(f"Successfully updated time off request {id}")
                return TimeOffType(
                    id=time_off.id,
                    employee_id=time_off.employee_id,
                    start_date=time_off.start_date,
                    end_date=time_off.end_date,
                    status=TimeOffStatusGQL(time_off.status.value),
                    request_date=time_off.request_date,
                    employee=EmployeeType(
                        id=employee.id,
                        name=employee.name,
                        age=employee.age,
                        role=EmployeeRoleGQL(employee.role.value),
                        availability=[],
                        max_hours_per_day=employee.max_hours_per_day,
                        preferred_shifts=[],
                        time_off_requests=[]
                    )
                )
        except Exception as e:
            logger.error(f"Failed to update time off request {id}: {e}")
            raise

    @strawberry.mutation
    def deleteTimeOff(self, id: uuid.UUID) -> bool:
        """Delete a time off request"""
        logger.info(f"Deleting time off request {id}")
        try:
            with get_session() as session:
                time_off = session.get(TimeOff, id)
                if not time_off:
                    logger.warning(f"Time off request not found for deletion: {id}")
                    return False
                
                session.delete(time_off)
                session.commit()
                
                logger.info(f"Successfully deleted time off request {id}")
                return True
        except Exception as e:
            logger.error(f"Failed to delete time off request {id}: {e}")
            raise

schema = strawberry.Schema(query=Query, mutation=Mutation) 