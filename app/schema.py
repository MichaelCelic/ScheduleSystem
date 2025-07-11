import strawberry
from typing import List, Optional
from datetime import date
import uuid
from sqlmodel import select
from .models import Employee, Location, Shift
from .graphql_types import EmployeeType, LocationType, ShiftType, AddEmployeeInput, DayOfWeekGQL
from .database import get_session
from .scheduler import generate_weekly_schedule, can_generate_echo_lab_schedule, check_oncall_schedule_published

@strawberry.type
class Query:
    @strawberry.field
    def employees(self) -> List[EmployeeType]:
        with get_session() as session:
            employees = session.exec(select(Employee)).all()
            return [EmployeeType(
                id=e.id, name=e.name, age=e.age, availability=e.availability, max_hours_per_day=e.max_hours_per_day
            ) for e in employees]

    @strawberry.field
    def locations(self) -> List[LocationType]:
        with get_session() as session:
            locations = session.exec(select(Location)).all()
            return [LocationType(id=l.id, name=l.name) for l in locations]

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

@strawberry.type
class Mutation:
    @strawberry.mutation
    def addEmployee(self, input: AddEmployeeInput) -> EmployeeType:
        with get_session() as session:
            employee = Employee(
                name=input.name,
                age=input.age,
                availability=input.availability,
                max_hours_per_day=input.max_hours_per_day
            )
            session.add(employee)
            session.commit()
            session.refresh(employee)
            return EmployeeType(
                id=employee.id, name=employee.name, age=employee.age,
                availability=employee.availability, max_hours_per_day=employee.max_hours_per_day
            )

    @strawberry.mutation
    def removeEmployee(self, id: uuid.UUID) -> bool:
        with get_session() as session:
            employee = session.get(Employee, id)
            if not employee:
                return False
            session.delete(employee)
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

schema = strawberry.Schema(query=Query, mutation=Mutation) 