import enum
import uuid
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import date, time

class DayOfWeek(enum.Enum):
    MON = "Mon"
    TUE = "Tue"
    WED = "Wed"
    THU = "Thu"
    FRI = "Fri"
    SAT = "Sat"
    SUN = "Sun"

class EmployeeRole(enum.Enum):
    STAFF = "staff"
    STUDENT = "student"

class EmployeeAvailabilityLink(SQLModel, table=True):
    employee_id: uuid.UUID = Field(foreign_key="employee.id", primary_key=True)
    day: DayOfWeek = Field(primary_key=True)
    preferred_shifts: str = Field(default="")  # Comma-separated preferred shifts
    employee: "Employee" = Relationship(back_populates="availability_links")

class Employee(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str
    age: int
    max_hours_per_day: float  # Changed to float to match frontend
    role: EmployeeRole = Field(default=EmployeeRole.STAFF)
    shifts: list["Shift"] = Relationship(back_populates="employee")
    availability_links: list["EmployeeAvailabilityLink"] = Relationship(back_populates="employee")

    @property
    def availability(self) -> List[DayOfWeek]:
        return [link.day for link in self.availability_links]

    @property
    def preferred_shifts(self) -> List[str]:
        """Get all preferred shifts from availability links"""
        shifts = set()
        for link in self.availability_links:
            if link.preferred_shifts:
                shifts.update(link.preferred_shifts.split(','))
        return list(shifts)

class Location(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str
    address: Optional[str] = None
    required_staff_morning: int = Field(default=2)
    required_staff_afternoon: int = Field(default=2)
    required_staff_night: int = Field(default=1)
    notes: Optional[str] = None
    shifts: list["Shift"] = Relationship(back_populates="location")

class Shift(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    employee_id: uuid.UUID = Field(foreign_key="employee.id")
    location_id: uuid.UUID = Field(foreign_key="location.id")
    date: date
    start_time: time
    end_time: time
    published: bool = Field(default=False)
    employee: Optional[Employee] = Relationship(back_populates="shifts")
    location: Optional[Location] = Relationship(back_populates="shifts") 