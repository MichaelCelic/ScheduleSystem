import pytest
from datetime import date, timedelta, time
from app.models import Employee, Location, DayOfWeek, Shift, EmployeeAvailabilityLink
from app.scheduler import (
    generate_weekly_schedule, 
    check_oncall_schedule_published, 
    can_generate_echo_lab_schedule,
    generate_echo_lab_schedule,
    generate_oncall_schedule,
    assign_thc_shifts,
    assign_txip_shifts,
    find_employee_by_name,
    find_location_by_name
)
import uuid

def make_employee(name, days, max_hours):
    employee = Employee(
        id=uuid.uuid4(),
        name=name,
        age=30,
        max_hours_per_day=max_hours
    )
    # Create availability links for the employee
    employee.availability_links = [
        EmployeeAvailabilityLink(employee_id=employee.id, day=day)
        for day in days
    ]
    return employee

def make_location(name):
    return Location(id=uuid.uuid4(), name=name)

def make_shift(employee_id, location_id, shift_date, location_name):
    shift = Shift(
        id=uuid.uuid4(),
        employee_id=employee_id,
        location_id=location_id,
        date=shift_date,
        start_time=time(8, 0),
        end_time=time(17, 0),
        published=True
    )
    # Mock the location relationship
    shift.location = Location(id=location_id, name=location_name)
    return shift

def test_echo_lab_schedule_with_business_rules():
    """Test echo lab schedule generation with business rules (M-F only)"""
    # Create test employees
    emilio = make_employee("Emilio", [DayOfWeek.MON, DayOfWeek.TUE, DayOfWeek.WED, DayOfWeek.THU], 8)
    martha = make_employee("Martha", [DayOfWeek.TUE, DayOfWeek.FRI], 8)
    other_emp = make_employee("Other", [DayOfWeek.MON, DayOfWeek.TUE, DayOfWeek.WED, DayOfWeek.THU, DayOfWeek.FRI], 8)
    
    # Create test locations
    thc = make_location("THC")
    txip = make_location("Tx-IP")
    or_inpat = make_location("OR/Inpat")
    regular = make_location("Regular")
    
    employees = [emilio, martha, other_emp]
    locations = [thc, txip, or_inpat, regular]
    
    week_start = date(2024, 1, 1)  # Monday
    published_oncall_shifts = []
    
    shifts = generate_echo_lab_schedule(week_start, employees, locations, published_oncall_shifts)
    
    # Check THC assignments (Emilio, Mon-Thu only)
    thc_shifts = [s for s in shifts if s.location_id == thc.id]
    assert len(thc_shifts) == 4  # Mon, Tue, Wed, Thu
    assert all(s.employee_id == emilio.id for s in thc_shifts)
    
    # Check Tx-IP assignments (Martha, Tue, Fri only)
    txip_shifts = [s for s in shifts if s.location_id == txip.id]
    assert len(txip_shifts) == 2  # Tue, Fri
    assert all(s.employee_id == martha.id for s in txip_shifts)
    
    # Verify no weekend shifts (Saturday/Sunday)
    weekend_dates = [week_start + timedelta(days=5), week_start + timedelta(days=6)]  # Sat, Sun
    for shift in shifts:
        assert shift.date not in weekend_dates, f"Found weekend shift on {shift.date}"

def test_oncall_dependent_shifts():
    """Test that on-call dependent shifts are created correctly (M-F only)"""
    # Create test employees
    oncall_emp = make_employee("OnCall", [DayOfWeek.MON, DayOfWeek.TUE, DayOfWeek.SAT], 8)
    
    # Create test locations
    jdch = make_location("JDCH")
    or_inpat = make_location("OR/Inpat")
    mhw = make_location("MHW")
    
    # Create published on-call shifts (including weekend)
    week_start = date(2024, 1, 1)
    monday = week_start
    tuesday = week_start + timedelta(days=1)
    saturday = week_start + timedelta(days=5)
    
    oncall_shifts = [
        make_shift(oncall_emp.id, jdch.id, monday, "JDCH"),
        make_shift(oncall_emp.id, mhw.id, tuesday, "MHW"),
        make_shift(oncall_emp.id, jdch.id, saturday, "JDCH")  # Weekend shift
    ]
    
    employees = [oncall_emp]
    locations = [or_inpat, mhw]
    
    shifts = generate_echo_lab_schedule(week_start, employees, locations, oncall_shifts)
    
    # Check that JDCH on-call creates OR/Inpat shift (weekday only)
    or_inpat_shifts = [s for s in shifts if s.location_id == or_inpat.id]
    assert len(or_inpat_shifts) == 1  # Only Monday, not Saturday
    assert or_inpat_shifts[0].employee_id == oncall_emp.id
    assert or_inpat_shifts[0].date == monday
    
    # Check that MHW on-call creates MHW regular shift
    mhw_shifts = [s for s in shifts if s.location_id == mhw.id]
    assert len(mhw_shifts) == 1
    assert mhw_shifts[0].employee_id == oncall_emp.id
    assert mhw_shifts[0].date == tuesday
    
    # Verify no weekend echo lab shifts
    weekend_dates = [saturday, week_start + timedelta(days=6)]  # Sat, Sun
    for shift in shifts:
        assert shift.date not in weekend_dates, f"Found weekend echo lab shift on {shift.date}"

def test_oncall_schedule_generation():
    """Test on-call schedule generation"""
    employees = [
        make_employee("Alice", [DayOfWeek.MON, DayOfWeek.TUE], 8),
        make_employee("Bob", [DayOfWeek.WED, DayOfWeek.THU], 8)
    ]
    locations = [
        make_location("JDCH"),
        make_location("W/M")
    ]
    
    week_start = date(2024, 1, 1)
    shifts = generate_oncall_schedule(week_start, employees, locations)
    
    # Should have on-call shifts for each day
    assert len(shifts) > 0
    
    # All shifts should be for on-call locations
    oncall_location_names = ["JDCH", "W/M"]
    for shift in shifts:
        location = next(loc for loc in locations if loc.id == shift.location_id)
        assert location.name in oncall_location_names

def test_employee_finding():
    """Test finding employees by name"""
    employees = [
        make_employee("Emilio", [DayOfWeek.MON], 8),
        make_employee("Martha", [DayOfWeek.TUE], 8),
        make_employee("John", [DayOfWeek.WED], 8)
    ]
    
    emilio = find_employee_by_name(employees, "Emilio")
    martha = find_employee_by_name(employees, "Martha")
    not_found = find_employee_by_name(employees, "NotExist")
    
    assert emilio is not None
    assert emilio.name == "Emilio"
    assert martha is not None
    assert martha.name == "Martha"
    assert not_found is None

def test_location_finding():
    """Test finding locations by name"""
    locations = [
        make_location("THC"),
        make_location("Tx-IP"),
        make_location("OR/Inpat")
    ]
    
    thc = find_location_by_name(locations, "THC")
    txip = find_location_by_name(locations, "Tx-IP")
    not_found = find_location_by_name(locations, "NotExist")
    
    assert thc is not None
    assert thc.name == "THC"
    assert txip is not None
    assert txip.name == "Tx-IP"
    assert not_found is None

def test_thc_shift_assignment():
    """Test THC shift assignment to Emilio (Mon-Thu only)"""
    emilio = make_employee("Emilio", [DayOfWeek.MON, DayOfWeek.TUE, DayOfWeek.WED, DayOfWeek.THU, DayOfWeek.FRI], 8)
    thc_location = make_location("THC")
    
    week_start = date(2024, 1, 1)  # Monday
    shifts = assign_thc_shifts(week_start, emilio, thc_location)
    
    # Should have 4 shifts (Mon, Tue, Wed, Thu)
    assert len(shifts) == 4
    
    # All shifts should be assigned to Emilio
    assert all(s.employee_id == emilio.id for s in shifts)
    
    # All shifts should be at THC location
    assert all(s.location_id == thc_location.id for s in shifts)
    
    # Should not have Friday shift
    friday = week_start + timedelta(days=4)
    assert not any(s.date == friday for s in shifts)
    
    # Should not have weekend shifts
    weekend_dates = [week_start + timedelta(days=5), week_start + timedelta(days=6)]  # Sat, Sun
    for shift in shifts:
        assert shift.date not in weekend_dates

def test_txip_shift_assignment():
    """Test Tx-IP shift assignment to Martha (Tue, Fri only, M-F only)"""
    martha = make_employee("Martha", [DayOfWeek.MON, DayOfWeek.TUE, DayOfWeek.WED, DayOfWeek.THU, DayOfWeek.FRI], 8)
    txip_location = make_location("Tx-IP")
    
    week_start = date(2024, 1, 1)  # Monday
    shifts = assign_txip_shifts(week_start, martha, txip_location)
    
    # Should have 2 shifts (Tue, Fri)
    assert len(shifts) == 2
    
    # All shifts should be assigned to Martha
    assert all(s.employee_id == martha.id for s in shifts)
    
    # All shifts should be at Tx-IP location
    assert all(s.location_id == txip_location.id for s in shifts)
    
    # Should be on Tuesday and Friday
    tuesday = week_start + timedelta(days=1)
    friday = week_start + timedelta(days=4)
    shift_dates = [s.date for s in shifts]
    assert tuesday in shift_dates
    assert friday in shift_dates
    
    # Should not have weekend shifts
    weekend_dates = [week_start + timedelta(days=5), week_start + timedelta(days=6)]  # Sat, Sun
    for shift in shifts:
        assert shift.date not in weekend_dates

def test_oncall_schedule_published():
    """Test that on-call schedule publication is correctly detected"""
    week_start = date(2024, 1, 1)
    employee_id = uuid.uuid4()
    jdch_location_id = uuid.uuid4()
    
    # Create on-call schedule with just one shift
    shifts = []
    day = week_start + timedelta(days=0)  # Just Monday
    shifts.append(make_shift(employee_id, jdch_location_id, day, "JDCH"))
    
    assert check_oncall_schedule_published(week_start, shifts) == True

def test_oncall_schedule_not_published():
    """Test that unpublished on-call schedule is correctly detected"""
    week_start = date(2024, 1, 1)
    
    # No shifts at all
    shifts = []
    
    assert check_oncall_schedule_published(week_start, shifts) == False

def test_can_generate_echo_lab():
    """Test that echo lab generation is allowed when on-call is published"""
    week_start = date(2024, 1, 1)
    employee_id = uuid.uuid4()
    jdch_location_id = uuid.uuid4()
    
    # Create on-call schedule with just one shift
    shifts = []
    day = week_start + timedelta(days=0)  # Just Monday
    shifts.append(make_shift(employee_id, jdch_location_id, day, "JDCH"))
    
    assert can_generate_echo_lab_schedule(week_start, shifts) == True

def test_cannot_generate_echo_lab():
    """Test that echo lab generation is blocked when on-call is not published"""
    week_start = date(2024, 1, 1)
    
    # No shifts at all
    shifts = []
    
    assert can_generate_echo_lab_schedule(week_start, shifts) == False 