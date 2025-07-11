from datetime import date, timedelta, time
from typing import List, Optional
from .models import Employee, Location, Shift, DayOfWeek, TimeOff, TimeOffStatus
import uuid
import random

def filter_employees_with_time_off(
    employees: List[Employee],
    start_date: date,
    end_date: date
) -> List[Employee]:
    """
    Filter out employees who have approved time off requests that overlap with the given date range.
    
    Args:
        employees: List of employees to filter
        start_date: Start date of the schedule period
        end_date: End date of the schedule period
    
    Returns:
        List of employees available during the specified period
    """
    available_employees = []
    
    for employee in employees:
        # Check if employee has any approved time off that overlaps with the schedule period
        has_time_off = False
        
        for time_off in employee.time_off_requests:
            if (time_off.status == TimeOffStatus.APPROVED and 
                time_off.start_date <= end_date and 
                time_off.end_date >= start_date):
                has_time_off = True
                break
        
        if not has_time_off:
            available_employees.append(employee)
    
    return available_employees

def generate_weekly_schedule(
    week_start: date,
    employees: List[Employee],
    locations: List[Location],
    schedule_type: str = "echolab",
    published_oncall_shifts: List[Shift] = None
) -> List[Shift]:
    """
    Generate weekly schedule based on schedule type and business rules.
    
    Args:
        week_start: Start date of the week
        employees: List of available employees
        locations: List of available locations
        schedule_type: "echolab" or "oncall"
        published_oncall_shifts: Published on-call shifts for dependency rules
    """
    # Calculate week end date
    week_end = week_start + timedelta(days=6)
    
    # Filter out employees with approved time off for this week
    available_employees = filter_employees_with_time_off(employees, week_start, week_end)
    
    if schedule_type == "echolab":
        return generate_echo_lab_schedule(week_start, available_employees, locations, published_oncall_shifts or [])
    else:
        return generate_oncall_schedule(week_start, available_employees, locations)

def generate_echo_lab_schedule(
    week_start: date,
    employees: List[Employee],
    locations: List[Location],
    published_oncall_shifts: List[Shift]
) -> List[Shift]:
    """
    Generate echo lab schedule with specific business rules:
    1. THC is always staffed by Emilio. No THC clinic on Friday.
    2. Tx-IP on Tuesday and Friday only staffed by Martha
    3. Person on call at MHW/MHM also has that regular shift
    4. Person on JDCH call is on OR/Inpat echo lab shift
    5. Echo lab schedules only run Monday through Friday (M-F)
    """
    shifts = []
    
    # Find specific employees by name
    emilio = find_employee_by_name(employees, "Emilio")
    martha = find_employee_by_name(employees, "Martha")
    
    # Find specific locations
    thc_location = find_location_by_name(locations, "THC")
    txip_location = find_location_by_name(locations, "Tx-IP")
    or_inpat_location = find_location_by_name(locations, "OR/Inpat")
    mhw_location = find_location_by_name(locations, "MHW")
    mhm_location = find_location_by_name(locations, "MHM")
    
    # Rule 1: Assign THC shifts to Emilio (Mon-Thu only)
    if emilio and thc_location:
        shifts.extend(assign_thc_shifts(week_start, emilio, thc_location))
    
    # Rule 2: Assign Tx-IP shifts to Martha (Tue, Fri only)
    if martha and txip_location:
        shifts.extend(assign_txip_shifts(week_start, martha, txip_location))
    
    # Rule 3 & 4: Assign on-call dependent shifts
    if published_oncall_shifts:
        shifts.extend(assign_oncall_dependent_shifts(
            week_start, published_oncall_shifts, employees, 
            or_inpat_location, mhw_location, mhm_location, locations
        ))
    
    # Fill remaining shifts with available staff
    remaining_shifts = fill_remaining_echo_lab_shifts(
        week_start, employees, locations, shifts
    )
    shifts.extend(remaining_shifts)
    
    return shifts

def generate_oncall_schedule(
    week_start: date,
    employees: List[Employee],
    locations: List[Location]
) -> List[Shift]:
    """
    Generate on-call schedule (simplified version for now)
    """
    shifts = []
    
    # Find on-call locations
    jdch_location = find_location_by_name(locations, "JDCH")
    wm_location = find_location_by_name(locations, "W/M")
    
    # Generate one on-call shift per day for the week
    for i in range(7):
        current_date = week_start + timedelta(days=i)
        day_of_week = DayOfWeek(current_date.strftime("%a").title())
        
        # Find available employees for this day
        available_employees = [
            emp for emp in employees 
            if day_of_week in emp.availability
        ]
        
        if available_employees:
            # Randomly assign on-call shifts
            if jdch_location:
                employee = random.choice(available_employees)
                shifts.append(create_shift(employee.id, jdch_location.id, current_date))
            
            if wm_location:
                employee = random.choice(available_employees)
                shifts.append(create_shift(employee.id, wm_location.id, current_date))
    
    return shifts

def assign_thc_shifts(week_start: date, emilio: Employee, thc_location: Location) -> List[Shift]:
    """Assign THC shifts to Emilio (Monday through Thursday only)"""
    shifts = []
    
    for i in range(5):  # Monday (0) through Friday (4)
        if i == 4:  # Skip Friday
            continue
            
        current_date = week_start + timedelta(days=i)
        day_of_week = DayOfWeek(current_date.strftime("%a").title())
        
        # Check if Emilio is available on this day
        if day_of_week in emilio.availability:
            shifts.append(create_shift(emilio.id, thc_location.id, current_date))
    
    return shifts

def assign_txip_shifts(week_start: date, martha: Employee, txip_location: Location) -> List[Shift]:
    """Assign Tx-IP shifts to Martha (Tuesday and Friday only)"""
    shifts = []
    
    for i in range(5):  # Monday (0) through Friday (4) only
        current_date = week_start + timedelta(days=i)
        day_of_week = DayOfWeek(current_date.strftime("%a").title())
        
        # Only assign on Tuesday (1) and Friday (4)
        if i in [1, 4] and day_of_week in martha.availability:
            shifts.append(create_shift(martha.id, txip_location.id, current_date))
    
    return shifts

def assign_oncall_dependent_shifts(
    week_start: date,
    published_oncall_shifts: List[Shift],
    employees: List[Employee],
    or_inpat_location: Location,
    mhw_location: Location,
    mhm_location: Location,
    locations: List[Location] = None  # add locations as optional arg for lookup
) -> List[Shift]:
    """
    Assign shifts based on on-call assignments:
    - Person on JDCH call is on OR/Inpat echo lab shift
    - Person on MHW/MHM call also has that regular shift
    - Only for Monday through Friday
    """
    shifts = []

    # Build a location lookup if locations are provided
    location_lookup = {loc.id: loc for loc in locations} if locations else {}

    # Group on-call shifts by date
    oncall_by_date = {}
    for shift in published_oncall_shifts:
        if shift.date not in oncall_by_date:
            oncall_by_date[shift.date] = []
        oncall_by_date[shift.date].append(shift)

    # Process each day's on-call assignments (M-F only)
    for shift_date, day_shifts in oncall_by_date.items():
        # Skip weekends (Saturday = 5, Sunday = 6)
        if shift_date.weekday() >= 5:
            continue

        for oncall_shift in day_shifts:
            # Robustly get location name
            location_name = None
            if oncall_shift.location and getattr(oncall_shift.location, 'name', None):
                location_name = oncall_shift.location.name
            elif hasattr(oncall_shift, 'location_id') and location_lookup:
                loc = location_lookup.get(oncall_shift.location_id)
                if loc:
                    location_name = loc.name

            if location_name == "JDCH" and or_inpat_location:
                # Person on JDCH call is on OR/Inpat echo lab shift
                shifts.append(create_shift(
                    oncall_shift.employee_id,
                    or_inpat_location.id,
                    shift_date
                ))
            elif location_name == "MHW" and mhw_location:
                # Person on MHW call also has that regular shift
                shifts.append(create_shift(
                    oncall_shift.employee_id,
                    mhw_location.id,
                    shift_date
                ))
            elif location_name == "MHM" and mhm_location:
                # Person on MHM call also has that regular shift
                shifts.append(create_shift(
                    oncall_shift.employee_id,
                    mhm_location.id,
                    shift_date
                ))

    return shifts

def fill_remaining_echo_lab_shifts(
    week_start: date,
    employees: List[Employee],
    locations: List[Location],
    existing_shifts: List[Shift]
) -> List[Shift]:
    """Fill remaining echo lab shifts with available staff (Monday through Friday only)"""
    shifts = []
    
    # Get all echo lab locations (excluding on-call locations)
    echo_lab_locations = [
        loc for loc in locations 
        if loc.name not in ["JDCH", "W/M", "THC", "Tx-IP", "OR/Inpat", "MHW", "MHM"]
    ]
    
    # Track existing assignments to avoid conflicts
    existing_assignments = set()
    for shift in existing_shifts:
        existing_assignments.add((shift.employee_id, shift.date))
    
    # Fill remaining shifts (M-F only)
    for i in range(5):  # Monday (0) through Friday (4) only
        current_date = week_start + timedelta(days=i)
        day_of_week = DayOfWeek(current_date.strftime("%a").title())
        
        for location in echo_lab_locations:
            # Find available employees for this day and location
            available_employees = [
                emp for emp in employees
                if day_of_week in emp.availability
                and (emp.id, current_date) not in existing_assignments
            ]
            
            if available_employees:
                employee = random.choice(available_employees)
                shifts.append(create_shift(employee.id, location.id, current_date))
                existing_assignments.add((employee.id, current_date))
    
    return shifts

def find_employee_by_name(employees: List[Employee], name: str) -> Optional[Employee]:
    """Find employee by name (case-insensitive)"""
    for emp in employees:
        if emp.name.lower() == name.lower():
            return emp
    return None

def find_location_by_name(locations: List[Location], name: str) -> Optional[Location]:
    """Find location by name (case-insensitive)"""
    for loc in locations:
        if loc.name.lower() == name.lower():
            return loc
    return None

def create_shift(employee_id: uuid.UUID, location_id: uuid.UUID, shift_date: date) -> Shift:
    """Create a new shift with default times"""
    return Shift(
        id=uuid.uuid4(),
        employee_id=employee_id,
        location_id=location_id,
        date=shift_date,
        start_time=time(8, 0),  # 8:00 AM
        end_time=time(17, 0),   # 5:00 PM
        published=False
    )

def check_oncall_schedule_published(
    week_start: date,
    published_shifts: List[Shift]
) -> bool:
    """
    Check if the on-call schedule for the given week is published.
    Returns True if there's a published on-call schedule for the week, False otherwise.
    """
    # Filter published on-call shifts for the given week
    oncall_shifts = [
        shift for shift in published_shifts
        if shift.date >= week_start 
        and shift.date < week_start + timedelta(days=7)
        and shift.location.name in ['JDCH', 'W/M']
    ]
    
    # Simply check if there are any on-call shifts for this week
    return len(oncall_shifts) > 0

def can_generate_echo_lab_schedule(
    week_start: date,
    published_shifts: List[Shift]
) -> bool:
    """
    Check if echo lab schedule can be generated for the given week.
    Requires on-call schedule to be published first.
    """
    return check_oncall_schedule_published(week_start, published_shifts) 