import strawberry
import uuid
from datetime import date, time
from typing import List, Optional
from enum import Enum
from .models import DayOfWeek

@strawberry.enum
class DayOfWeekGQL(Enum):
    MON = "Mon"
    TUE = "Tue"
    WED = "Wed"
    THU = "Thu"
    FRI = "Fri"
    SAT = "Sat"
    SUN = "Sun"

@strawberry.type
class EmployeeType:
    id: uuid.UUID
    name: str
    age: int
    availability: List[DayOfWeekGQL]
    max_hours_per_day: int

@strawberry.type
class LocationType:
    id: uuid.UUID
    name: str

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
    availability: List[DayOfWeekGQL]
    max_hours_per_day: int 