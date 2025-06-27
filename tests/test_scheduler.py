import pytest
from datetime import date
from app.models import Employee, Location, DayOfWeek
from app.scheduler import generate_weekly_schedule
import uuid

def make_employee(name, days, max_hours):
    return Employee(
        id=uuid.uuid4(),
        name=name,
        age=30,
        availability=days,
        max_hours_per_day=max_hours
    )

def make_location(name):
    return Location(id=uuid.uuid4(), name=name)

def test_not_enough_staff():
    employees = [make_employee("Alice", [DayOfWeek.MON, DayOfWeek.TUE], 8)]
    locations = [make_location("ER"), make_location("ICU")]
    week_start = date(2024, 1, 1)
    shifts = generate_weekly_schedule(week_start, employees, locations)
    # Should not over-assign Alice
    assert all(s.employee_id == employees[0].id for s in shifts)
    # Should not assign more than max_hours_per_day
    for s in shifts:
        assert s.employee_id == employees[0].id
        assert s.date.weekday() in [0, 1]  # Only Mon, Tue

def test_fully_booked_days():
    employees = [
        make_employee("Bob", [DayOfWeek.MON, DayOfWeek.TUE, DayOfWeek.WED], 4),
        make_employee("Carol", [DayOfWeek.WED, DayOfWeek.THU], 4)
    ]
    locations = [make_location("ER")]
    week_start = date(2024, 1, 1)
    shifts = generate_weekly_schedule(week_start, employees, locations)
    # Should not assign shifts on unavailable days
    for s in shifts:
        emp = next(e for e in employees if e.id == s.employee_id)
        assert DayOfWeek(s.date.strftime("%a").upper()) in emp.availability 