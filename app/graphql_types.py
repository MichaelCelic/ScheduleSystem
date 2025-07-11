import strawberry
import uuid
from datetime import date, time
from typing import List, Optional
from enum import Enum
from .models import DayOfWeek, EmployeeRole

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

@strawberry.type
class EmployeeType:
    id: uuid.UUID
    name: str
    age: int
    role: EmployeeRoleGQL
    availability: List[DayOfWeekGQL]
    max_hours_per_day: float
    preferred_shifts: List[str]

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