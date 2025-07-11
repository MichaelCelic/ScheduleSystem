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

@strawberry.type
class Query:
    @strawberry.field
    def employees(self) -> List[EmployeeType]:
        with get_session() as session:
            employees = session.exec(select(Employee)).all()
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

    @strawberry.field
    def locations(self) -> List[LocationType]:
        with get_session() as session:
            locations = session.exec(select(Location)).all()
            return [LocationType(
                id=l.id, 
                name=l.name,
                address=l.address,
                required_staff_morning=l.required_staff_morning,
                required_staff_afternoon=l.required_staff_afternoon,
                required_staff_night=l.required_staff_night,
                notes=l.notes
            ) for l in locations]

    @strawberry.field
    def previewSchedules(self, weekStart: date, scheduleType: str = "echolab") -> List[ShiftType]:
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
            return [ShiftType(
                id=s.id, employee_id=s.employee_id, location_id=s.location_id, date=s.date,
                start_time=s.start_time, end_time=s.end_time, published=s.published
            ) for s in shifts]

    @strawberry.field
    def publishedSchedules(self, weekStart: date) -> List[ShiftType]:
        with get_session() as session:
            shifts = session.exec(select(Shift).where(Shift.date >= weekStart, Shift.published == True)).all()
            return [ShiftType(
                id=s.id, employee_id=s.employee_id, location_id=s.location_id, date=s.date,
                start_time=s.start_time, end_time=s.end_time, published=s.published
            ) for s in shifts]

    @strawberry.field
    def oncallSchedulePublished(self, weekStart: date) -> bool:
        """Check if on-call schedule is published for the given week"""
        with get_session() as session:
            published_shifts = session.exec(select(Shift).where(Shift.published == True)).all()
            return check_oncall_schedule_published(weekStart, published_shifts)

    @strawberry.field
    def canGenerateEchoLab(self, weekStart: date) -> bool:
        """Check if echo lab schedule can be generated for the given week"""
        with get_session() as session:
            published_shifts = session.exec(select(Shift).where(Shift.published == True)).all()
            return can_generate_echo_lab_schedule(weekStart, published_shifts)

    @strawberry.field
    def timeOffRequests(self) -> List[TimeOffType]:
        """Get all time off requests"""
        with get_session() as session:
            # Use select with join to load employee data
            from sqlmodel import select
            time_off_requests = session.exec(
                select(TimeOff, Employee)
                .join(Employee, TimeOff.employee_id == Employee.id)
            ).all()
            
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
                ) if emp else None
            ) for to, emp in time_off_requests]

    @strawberry.field
    def employeeTimeOff(self, employee_id: uuid.UUID) -> List[TimeOffType]:
        """Get time off requests for a specific employee"""
        with get_session() as session:
            # Get employee and time off requests
            employee = session.get(Employee, employee_id)
            if not employee:
                raise Exception("Employee not found")
                
            time_off_requests = session.exec(
                select(TimeOff).where(TimeOff.employee_id == employee_id)
            ).all()
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

@strawberry.type
class Mutation:
    @strawberry.mutation
    def addEmployee(self, input: AddEmployeeInput) -> EmployeeType:
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

    @strawberry.mutation
    def updateEmployee(self, id: uuid.UUID, input: AddEmployeeInput) -> EmployeeType:
        with get_session() as session:
            employee = session.get(Employee, id)
            if not employee:
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

    @strawberry.mutation
    def deleteEmployee(self, id: uuid.UUID) -> bool:
        with get_session() as session:
            employee = session.get(Employee, id)
            if not employee:
                return False
            
            # Delete related EmployeeAvailabilityLink records first
            session.exec(delete(EmployeeAvailabilityLink).where(EmployeeAvailabilityLink.employee_id == id))
            
            # Delete related Shift records
            session.exec(delete(Shift).where(Shift.employee_id == id))
            
            # Now delete the employee
            session.delete(employee)
            session.commit()
            return True

    @strawberry.mutation
    def addLocation(self, input: AddLocationInput) -> LocationType:
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
            return LocationType(
                id=location.id,
                name=location.name,
                address=location.address,
                required_staff_morning=location.required_staff_morning,
                required_staff_afternoon=location.required_staff_afternoon,
                required_staff_night=location.required_staff_night,
                notes=location.notes
            )

    @strawberry.mutation
    def updateLocation(self, id: uuid.UUID, input: AddLocationInput) -> LocationType:
        with get_session() as session:
            location = session.get(Location, id)
            if not location:
                raise Exception("Location not found")
            
            location.name = input.name
            location.address = input.address
            location.required_staff_morning = input.required_staff_morning
            location.required_staff_afternoon = input.required_staff_afternoon
            location.required_staff_night = input.required_staff_night
            location.notes = input.notes
            
            session.commit()
            session.refresh(location)
            
            return LocationType(
                id=location.id,
                name=location.name,
                address=location.address,
                required_staff_morning=location.required_staff_morning,
                required_staff_afternoon=location.required_staff_afternoon,
                required_staff_night=location.required_staff_night,
                notes=location.notes
            )

    @strawberry.mutation
    def deleteLocation(self, id: uuid.UUID) -> bool:
        with get_session() as session:
            location = session.get(Location, id)
            if not location:
                return False
            session.delete(location)
            session.commit()
            return True

    @strawberry.mutation
    def generateSchedule(self, weekStart: date, scheduleType: str = "echolab") -> List[ShiftType]:
        with get_session() as session:
            # For echo lab schedules, check if on-call is complete first
            if scheduleType == "echolab":
                published_shifts = session.exec(select(Shift).where(Shift.published == True)).all()
                if not can_generate_echo_lab_schedule(weekStart, published_shifts):
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
            return [ShiftType(
                id=s.id, employee_id=s.employee_id, location_id=s.location_id, date=s.date,
                start_time=s.start_time, end_time=s.end_time, published=s.published
            ) for s in shifts]

    @strawberry.mutation
    def publishSchedule(self, weekStart: date) -> List[ShiftType]:
        with get_session() as session:
            shifts = session.exec(select(Shift).where(Shift.date >= weekStart)).all()
            for s in shifts:
                s.published = True
                session.add(s)
            session.commit()
            return [ShiftType(
                id=s.id, employee_id=s.employee_id, location_id=s.location_id, date=s.date,
                start_time=s.start_time, end_time=s.end_time, published=s.published
            ) for s in shifts]

    @strawberry.mutation
    def requestTimeOff(self, input: TimeOffInput) -> TimeOffType:
        """Request time off for an employee"""
        with get_session() as session:
            # Validate that the employee exists
            employee = session.get(Employee, input.employee_id)
            if not employee:
                raise Exception("Employee not found")
            
            # Validate date range
            if input.start_date > input.end_date:
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

    @strawberry.mutation
    def updateTimeOffStatus(self, id: uuid.UUID, status: TimeOffStatusGQL) -> TimeOffType:
        """Update the status of a time off request (approve/deny)"""
        with get_session() as session:
            time_off = session.get(TimeOff, id)
            if not time_off:
                raise Exception("Time off request not found")
            
            # Get the employee for the time off request
            employee = session.get(Employee, time_off.employee_id)
            if not employee:
                raise Exception("Employee not found")
            
            time_off.status = TimeOffStatus(status.value)
            session.add(time_off)
            session.commit()
            session.refresh(time_off)
            
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

    @strawberry.mutation
    def deleteTimeOff(self, id: uuid.UUID) -> bool:
        """Delete a time off request"""
        with get_session() as session:
            time_off = session.get(TimeOff, id)
            if not time_off:
                return False
            
            session.delete(time_off)
            session.commit()
            return True

schema = strawberry.Schema(query=Query, mutation=Mutation) 