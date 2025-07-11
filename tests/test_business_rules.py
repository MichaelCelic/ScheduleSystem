import pytest
from datetime import datetime, timedelta, time
from app.models import Employee, Location, Shift, EmployeeAvailabilityLink, DayOfWeek
from app.scheduler import generate_echo_lab_schedule, generate_weekly_schedule
from app.database import get_session
from sqlmodel import Session, create_engine, SQLModel
import uuid


@pytest.fixture
def engine():
    """Create a test database engine"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    """Create a test database session"""
    with Session(engine) as session:
        yield session


@pytest.fixture
def sample_employees(session):
    """Create sample employees for testing"""
    employees = []
    
    # Create employees with specific names for business rules
    employee_data = [
        ("Emilio", 32, 8.5),
        ("Martha", 35, 10.5),
        ("Grisel", 28, 8.5),
        ("Annie", 29, 8.5),
        ("Angela", 31, 8.5),
        ("Alexandra", 27, 8.5),
        ("Shannon", 33, 8.5),
        ("Guadalupe", 30, 8.5),
        ("William", 24, 8.0),
    ]
    
    for name, age, max_hours in employee_data:
        employee = Employee(
            id=uuid.uuid4(),
            name=name,
            age=age,
            max_hours_per_day=max_hours
        )
        session.add(employee)
        employees.append(employee)
        
        # Add availability for all weekdays
        for day in [DayOfWeek.MON, DayOfWeek.TUE, DayOfWeek.WED, 
                   DayOfWeek.THU, DayOfWeek.FRI]:
            availability = EmployeeAvailabilityLink(
                employee_id=employee.id,
                day=day
            )
            session.add(availability)
    
    session.commit()
    return employees


@pytest.fixture
def sample_locations(session):
    """Create sample locations for testing"""
    locations = []
    
    location_data = [
        ("JDCH", "Main Hospital"),
        ("W/M", "On-Call Location"),
        ("THC", "THC Location"),
        ("Tx-IP", "Tx-IP Location"),
        ("MHW", "MHW Location"),
        ("MHM", "MHM Location"),
        ("OR/Inpat", "Operating Room/Inpatient"),
    ]
    
    for name, description in location_data:
        location = Location(
            id=uuid.uuid4(),
            name=name,
            description=description
        )
        session.add(location)
        locations.append(location)
    
    session.commit()
    return locations


@pytest.fixture
def published_oncall_schedule(session, sample_employees, sample_locations):
    """Create a published on-call schedule for the test week"""
    # Find all relevant on-call locations
    wm_location = next(loc for loc in sample_locations if loc.name == "W/M")
    jdch_location = next(loc for loc in sample_locations if loc.name == "JDCH")
    mhw_location = next(loc for loc in sample_locations if loc.name == "MHW")
    mhm_location = next(loc for loc in sample_locations if loc.name == "MHM")

    # Create on-call shifts for the test week (Monday to Friday)
    week_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    # Adjust to Monday
    while week_start.weekday() != 0:  # Monday is 0
        week_start += timedelta(days=1)

    oncall_shifts = []
    for i in range(5):  # Monday to Friday
        shift_date = week_start + timedelta(days=i)
        # Assign different employees to each location for variety
        emp_jdch = sample_employees[i % len(sample_employees)]
        emp_wm = sample_employees[(i+1) % len(sample_employees)]
        emp_mhw = sample_employees[(i+2) % len(sample_employees)]
        emp_mhm = sample_employees[(i+3) % len(sample_employees)]
        # JDCH
        shift_jdch = Shift(
            id=uuid.uuid4(),
            employee_id=emp_jdch.id,
            location_id=jdch_location.id,
            date=shift_date.date(),
            start_time=time(8, 0),
            end_time=time(17, 0),
            published=True
        )
        session.add(shift_jdch)
        oncall_shifts.append(shift_jdch)
        # W/M
        shift_wm = Shift(
            id=uuid.uuid4(),
            employee_id=emp_wm.id,
            location_id=wm_location.id,
            date=shift_date.date(),
            start_time=time(8, 0),
            end_time=time(17, 0),
            published=True
        )
        session.add(shift_wm)
        oncall_shifts.append(shift_wm)
        # MHW
        shift_mhw = Shift(
            id=uuid.uuid4(),
            employee_id=emp_mhw.id,
            location_id=mhw_location.id,
            date=shift_date.date(),
            start_time=time(8, 0),
            end_time=time(17, 0),
            published=True
        )
        session.add(shift_mhw)
        oncall_shifts.append(shift_mhw)
        # MHM
        shift_mhm = Shift(
            id=uuid.uuid4(),
            employee_id=emp_mhm.id,
            location_id=mhm_location.id,
            date=shift_date.date(),
            start_time=time(8, 0),
            end_time=time(17, 0),
            published=True
        )
        session.add(shift_mhm)
        oncall_shifts.append(shift_mhm)

    session.commit()
    return oncall_shifts


def test_emilio_always_staffs_thc_no_friday(session, sample_employees, sample_locations, published_oncall_schedule):
    """Test that Emilio always staffs THC and never on Friday"""
    # Find Emilio and THC location
    emilio = next(emp for emp in sample_employees if emp.name == "Emilio")
    thc_location = next(loc for loc in sample_locations if loc.name == "THC")
    
    # Generate Echo Lab schedule
    week_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    while week_start.weekday() != 0:  # Monday is 0
        week_start += timedelta(days=1)
    
    shifts = generate_echo_lab_schedule(week_start.date(), sample_employees, sample_locations, published_oncall_schedule)
    
    # Check that Emilio is assigned to THC on Monday-Thursday
    emilio_thc_shifts = [s for s in shifts if s.employee_id == emilio.id and s.location_id == thc_location.id]
    
    # Should have 4 shifts (Monday-Thursday)
    assert len(emilio_thc_shifts) == 4
    
    # Check that Emilio is NOT assigned on Friday
    friday = week_start + timedelta(days=4)
    emilio_friday_shifts = [s for s in shifts if s.employee_id == emilio.id and s.date == friday.date()]
    assert len(emilio_friday_shifts) == 0


def test_martha_staffs_txip_tuesday_friday(session, sample_employees, sample_locations, published_oncall_schedule):
    """Test that Martha staffs Tx-IP on Tuesday and Friday"""
    # Find Martha and Tx-IP location
    martha = next(emp for emp in sample_employees if emp.name == "Martha")
    txip_location = next(loc for loc in sample_locations if loc.name == "Tx-IP")
    
    # Generate Echo Lab schedule
    week_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    while week_start.weekday() != 0:  # Monday is 0
        week_start += timedelta(days=1)
    
    shifts = generate_echo_lab_schedule(week_start.date(), sample_employees, sample_locations, published_oncall_schedule)
    
    # Check that Martha is assigned to Tx-IP on Tuesday and Friday
    martha_txip_shifts = [s for s in shifts if s.employee_id == martha.id and s.location_id == txip_location.id]
    
    # Should have 2 shifts (Tuesday and Friday)
    assert len(martha_txip_shifts) == 2
    
    # Check specific days
    tuesday = week_start + timedelta(days=1)
    friday = week_start + timedelta(days=4)
    
    tuesday_shift = next((s for s in martha_txip_shifts if s.date == tuesday.date()), None)
    friday_shift = next((s for s in martha_txip_shifts if s.date == friday.date()), None)
    
    assert tuesday_shift is not None
    assert friday_shift is not None


def test_oncall_staff_at_mhw_mhm_have_regular_shifts(session, sample_employees, sample_locations, published_oncall_schedule):
    """Test that on-call staff at MHW/MHM also have regular Echo Lab shifts"""
    # Find MHW and MHM locations
    mhw_location = next(loc for loc in sample_locations if loc.name == "MHW")
    mhm_location = next(loc for loc in sample_locations if loc.name == "MHM")
    
    # Generate Echo Lab schedule
    week_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    while week_start.weekday() != 0:  # Monday is 0
        week_start += timedelta(days=1)
    
    shifts = generate_echo_lab_schedule(week_start.date(), sample_employees, sample_locations, published_oncall_schedule)
    
    # Check that there are shifts at MHW and MHM
    mhw_shifts = [s for s in shifts if s.location_id == mhw_location.id]
    mhm_shifts = [s for s in shifts if s.location_id == mhm_location.id]
    
    # Should have shifts at both locations
    assert len(mhw_shifts) > 0
    assert len(mhm_shifts) > 0


def test_jdch_oncall_staff_assigned_to_or_inpat(session, sample_employees, sample_locations, published_oncall_schedule):
    """Test that JDCH on-call staff are assigned to OR/Inpat Echo Lab shifts"""
    # Find OR/Inpat location
    or_inpat_location = next(loc for loc in sample_locations if loc.name == "OR/Inpat")
    
    # Generate Echo Lab schedule
    week_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    while week_start.weekday() != 0:  # Monday is 0
        week_start += timedelta(days=1)
    
    shifts = generate_echo_lab_schedule(week_start.date(), sample_employees, sample_locations, published_oncall_schedule)
    
    # Check that there are shifts at OR/Inpat
    or_inpat_shifts = [s for s in shifts if s.location_id == or_inpat_location.id]
    
    # Should have shifts at this location
    assert len(or_inpat_shifts) > 0


def test_echo_lab_only_monday_friday(session, sample_employees, sample_locations, published_oncall_schedule):
    """Test that Echo Lab schedules only run Monday through Friday"""
    # Generate Echo Lab schedule
    week_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    while week_start.weekday() != 0:  # Monday is 0
        week_start += timedelta(days=1)
    
    shifts = generate_echo_lab_schedule(week_start.date(), sample_employees, sample_locations, published_oncall_schedule)
    
    # Check that all shifts are Monday-Friday
    for shift in shifts:
        shift_date = shift.date
        weekday = shift_date.weekday()  # Monday=0, Sunday=6
        assert weekday < 5, f"Shift on {shift_date} is not Monday-Friday (weekday: {weekday})"
    
    # Should have exactly 5 days of shifts
    unique_dates = set(shift.date for shift in shifts)
    assert len(unique_dates) == 5


def test_all_business_rules_combined(session, sample_employees, sample_locations, published_oncall_schedule):
    """Test all business rules work together correctly"""
    # Find specific employees and locations
    emilio = next(emp for emp in sample_employees if emp.name == "Emilio")
    martha = next(emp for emp in sample_employees if emp.name == "Martha")
    thc_location = next(loc for loc in sample_locations if loc.name == "THC")
    txip_location = next(loc for loc in sample_locations if loc.name == "Tx-IP")
    
    # Generate Echo Lab schedule
    week_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    while week_start.weekday() != 0:  # Monday is 0
        week_start += timedelta(days=1)
    
    shifts = generate_echo_lab_schedule(week_start.date(), sample_employees, sample_locations, published_oncall_schedule)
    
    # Rule 1: Emilio always staffs THC (no Friday)
    emilio_thc_shifts = [s for s in shifts if s.employee_id == emilio.id and s.location_id == thc_location.id]
    assert len(emilio_thc_shifts) == 4  # Monday-Thursday
    
    friday = week_start + timedelta(days=4)
    emilio_friday_shifts = [s for s in shifts if s.employee_id == emilio.id and s.date == friday.date()]
    assert len(emilio_friday_shifts) == 0
    
    # Rule 2: Martha staffs Tx-IP on Tuesday and Friday
    martha_txip_shifts = [s for s in shifts if s.employee_id == martha.id and s.location_id == txip_location.id]
    assert len(martha_txip_shifts) == 2
    
    tuesday = week_start + timedelta(days=1)
    tuesday_shift = next((s for s in martha_txip_shifts if s.date == tuesday.date()), None)
    friday_shift = next((s for s in martha_txip_shifts if s.date == friday.date()), None)
    assert tuesday_shift is not None
    assert friday_shift is not None
    
    # Rule 3: Only Monday-Friday
    for shift in shifts:
        weekday = shift.date.weekday()
        assert weekday < 5
    
    # Rule 4: All locations have shifts
    location_counts = {}
    for shift in shifts:
        location_name = next(loc.name for loc in sample_locations if loc.id == shift.location_id)
        location_counts[location_name] = location_counts.get(location_name, 0) + 1
    
    # Should have shifts at all Echo Lab locations
    echo_lab_locations = ["THC", "Tx-IP", "MHW", "MHM", "OR/Inpat"]
    for location in echo_lab_locations:
        assert location_counts.get(location, 0) > 0, f"No shifts at {location}" 