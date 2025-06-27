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

class EmployeeAvailabilityLink(SQLModel, table=True):
    employee_id: uuid.UUID = Field(foreign_key="employee.id", primary_key=True)
    day: DayOfWeek = Field(primary_key=True)
    employee: "Employee" = Relationship(back_populates="availability_links")

class Employee(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str
    age: int
    max_hours_per_day: int
    shifts: list["Shift"] = Relationship(back_populates="employee")
    availability_links: list["EmployeeAvailabilityLink"] = Relationship(back_populates="employee")

    @property
    def availability(self) -> List[DayOfWeek]:
        return [link.day for link in self.availability_links]

class Location(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str
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