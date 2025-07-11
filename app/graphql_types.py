import strawberry
import uuid
from datetime import date, time
from typing import List, Optional
from enum import Enum
from .models import DayOfWeek, EmployeeRole, TimeOffStatus

@strawberry.enum
class DayOfWeekGQL(Enum):
    MON = "Mon"
    TUE = "Tue"
    WED = "Wed"
    THU = "Thu"
    FRI = "Fri"
    SAT = "Sat"
    SUN = "Sun"

@strawberry.enum
class EmployeeRoleGQL(Enum):
    STAFF = "staff"
    STUDENT = "student"

@strawberry.enum
class TimeOffStatusGQL(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"

@strawberry.type
class EmployeeType:
    id: uuid.UUID
    name: str
    age: int
    role: EmployeeRoleGQL
    availability: List[DayOfWeekGQL]
    max_hours_per_day: float
    preferred_shifts: List[str]
    time_off_requests: List["TimeOffType"]

@strawberry.type
class LocationType:
    id: uuid.UUID
    name: str
    address: Optional[str]
    required_staff_morning: int
    required_staff_afternoon: int
    required_staff_night: int
    notes: Optional[str]

@strawberry.type
class ShiftType:
    id: uuid.UUID
    employee_id: uuid.UUID
    location_id: uuid.UUID
    date: date
    start_time: time
    end_time: time
    published: bool

@strawberry.type
class TimeOffType:
    id: uuid.UUID
    employee_id: uuid.UUID
    start_date: date
    end_date: date
    status: TimeOffStatusGQL
    request_date: date
    employee: Optional[EmployeeType]

@strawberry.input
class TimeOffInput:
    employee_id: uuid.UUID
    start_date: date
    end_date: date

@strawberry.input
class AddEmployeeInput:
    name: str
    age: int
    role: EmployeeRoleGQL
    availability: List[DayOfWeekGQL]
    max_hours_per_day: float
    preferred_shifts: List[str]

@strawberry.input
class AddLocationInput:
    name: str
    address: Optional[str]
    required_staff_morning: int
    required_staff_afternoon: int
    required_staff_night: int
    notes: Optional[str] 