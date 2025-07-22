from datetime import date, timedelta, time
from typing import List, Optional
from .models import Employee, Location, Shift, DayOfWeek, TimeOff, TimeOffStatus
import uuid
import random
import math
from .logger import logger, log_business_rule, log_schedule_generation

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
    Generate a weekly schedule for the specified type
    """
    logger.info(f"Starting schedule generation for {schedule_type} week starting {week_start}")
    
    try:
        if schedule_type == "echolab":
            shifts = generate_echo_lab_schedule(week_start, employees, locations, published_oncall_shifts)
        elif schedule_type == "oncall":
            shifts = generate_oncall_schedule(week_start, employees, locations)
        else:
            logger.error(f"Unknown schedule type: {schedule_type}")
            raise ValueError(f"Unknown schedule type: {schedule_type}")
        
        log_schedule_generation(
            schedule_type=schedule_type,
            week_start=str(week_start),
            employee_count=len(employees),
            success=True
        )
        
        logger.info(f"Successfully generated {len(shifts)} shifts for {schedule_type}")
        return shifts
        
    except Exception as e:
        log_schedule_generation(
            schedule_type=schedule_type,
            week_start=str(week_start),
            employee_count=len(employees),
            success=False,
            error=str(e)
        )
        logger.error(f"Failed to generate {schedule_type} schedule: {e}")
        raise

def generate_echo_lab_schedule(
    week_start: date,
    employees: List[Employee],
    locations: List[Location],
    published_oncall_shifts: List[Shift] = None
) -> List[Shift]:
    """
    Generate Echo Lab schedule based on published on-call schedule
    """
    logger.info(f"Generating Echo Lab schedule for week starting {week_start}")
    
    try:
        # Use JDCH as the default location for Echo Lab shifts
        jdch_location = next((loc for loc in locations if loc.name == "JDCH"), None)
        if not jdch_location:
            logger.error("JDCH location not found")
            raise ValueError("JDCH location not found")
        
        # Get staff employees (non-students)
        staff_employees = [emp for emp in employees if emp.role.value == "staff"]
        logger.info(f"Found {len(staff_employees)} staff employees for Echo Lab scheduling")
        
        shifts = []
        all_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        assignment_options = ["TX-Inpat.", "TX-Outpat.", "Echo Lab", "MPG-Fetal", "PTO"]
        
        # Generate 5 weeks of schedules
        for week_num in range(5):
            week_date = week_start + timedelta(weeks=week_num)
            logger.info(f"Generating schedule for week {week_num + 1} starting {week_date}")
            
            for day_index, day in enumerate(all_days):
                current_date = week_date + timedelta(days=day_index)
                
                # Add date label for better visibility (e.g., "Monday (8/04)")
                day_with_date = f"{day} ({current_date.strftime('%m/%d')})"
                
                logger.info(f"Processing {day_with_date} - Date: {current_date}")
                
                # Create assignments for all employees
                assignments = {}
                
                for employee in staff_employees:
                    assignments[employee.name] = {}
                    
                    # Check if employee has approved time-off for this date
                    has_time_off = has_approved_time_off(employee, current_date)
                    
                    # Debug logging for time-off checks
                    logger.debug(f"Time-off check for {employee.name} on {current_date}: {has_time_off}")
                    
                    # Apply business rules
                    assignment = ""
                    
                    # Rule 1: Martha's assignments (respecting time-off)
                    if employee.name == "Martha":
                        if has_time_off:
                            assignment = "PTO"
                            logger.info(f"Martha has time-off on {current_date}, assigning PTO")
                        elif day == "Tuesday" or day == "Friday":
                            # Rule 2: Tx-IP on Tuesday and Friday only staffed by Martha
                            assignment = "TX-Inpat."
                        else:
                            # Random assignment for other days (avoid PTO for Martha on work days)
                            work_options = [opt for opt in assignment_options if opt != "PTO"]
                            assignment = work_options[int(random.random() * len(work_options))]
                    
                    # Rule 3: Other employees - check time-off first
                    else:
                        if has_time_off:
                            assignment = "PTO"
                            logger.info(f"{employee.name} has time-off on {current_date}, assigning PTO")
                        else:
                            # Random assignment for other employees/days
                            work_options = [opt for opt in assignment_options if opt != "PTO"]
                            assignment = work_options[int(random.random() * len(work_options))]
                    
                    assignments[employee.name][day] = assignment
                    
                    # Log business rule application
                    log_business_rule(
                        rule_name="echo_lab_assignment",
                        details={
                            "employee": employee.name,
                            "day": day,
                            "date": str(current_date),
                            "assignment": assignment,
                            "has_time_off": has_time_off
                        },
                        success=True
                    )
                
                # Create shift objects for this day
                for employee_name, day_assignments in assignments.items():
                    assignment = day_assignments[day]
                    if assignment and assignment != "PTO":
                        # Find the employee
                        employee = next((emp for emp in staff_employees if emp.name == employee_name), None)
                        if employee:
                            shift = Shift(
                                id=uuid.uuid4(),
                                employee_id=employee.id,
                                location_id=jdch_location.id,
                                date=current_date,
                                start_time=time(8, 0),  # 8:00 AM
                                end_time=time(17, 0),   # 5:00 PM
                                published=False
                            )
                            shifts.append(shift)
                            
                            logger.debug(f"Created shift for {employee_name} on {day} ({current_date}): {assignment}")
        
        logger.info(f"Generated {len(shifts)} Echo Lab shifts")
        return shifts
        
    except Exception as e:
        logger.error(f"Failed to generate Echo Lab schedule: {e}")
        raise

def generate_oncall_schedule(
    week_start: date,
    employees: List[Employee],
    locations: List[Location]
) -> List[Shift]:
    """
    Generate on-call schedule for JDCH and W/M locations
    """
    logger.info(f"Generating on-call schedule for week starting {week_start}")
    
    try:
        # Get on-call locations
        oncall_locations = [loc for loc in locations if loc.name in ["JDCH", "W/M", "On Call Fetal"]]
        if not oncall_locations:
            logger.error("No on-call locations found")
            raise ValueError("No on-call locations found")
        
        # Get staff employees
        staff_employees = [emp for emp in employees if emp.role.value == "staff"]
        logger.info(f"Found {len(staff_employees)} staff employees for on-call scheduling")
        
        shifts = []
        all_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        # Generate 5 weeks of schedules
        for week_num in range(5):
            week_date = week_start + timedelta(weeks=week_num)
            logger.info(f"Generating on-call schedule for week {week_num + 1} starting {week_date}")
            
            for day_index, day in enumerate(all_days):
                current_date = week_date + timedelta(days=day_index)
                
                # Assign employees to each location for this day
                for location in oncall_locations:
                    # Simple assignment logic - can be enhanced
                    assigned_employee = staff_employees[day_index % len(staff_employees)]
                    
                    # Note: Employees with time-off can still be assigned on-call
                    # (This is the business rule - on-call availability during time-off)
                    
                    shift = Shift(
                        id=uuid.uuid4(),
                        employee_id=assigned_employee.id,
                        location_id=location.id,
                        date=current_date,
                        start_time=time(17, 0),  # 5:00 PM
                        end_time=time(8, 0),     # 8:00 AM (next day)
                        published=False
                    )
                    shifts.append(shift)
                    
                    log_business_rule(
                        rule_name="oncall_assignment",
                        details={
                            "employee": assigned_employee.name,
                            "location": location.name,
                            "day": day,
                            "date": str(current_date)
                        },
                        success=True
                    )
                    
                    logger.debug(f"Created on-call shift for {assigned_employee.name} at {location.name} on {day} ({current_date})")
        
        logger.info(f"Generated {len(shifts)} on-call shifts")
        return shifts
        
    except Exception as e:
        logger.error(f"Failed to generate on-call schedule: {e}")
        raise

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

def has_approved_time_off(employee: Employee, check_date: date) -> bool:
    """
    Check if an employee has approved time-off for a specific date
    """
    try:
        for time_off in employee.time_off_requests:
            if (time_off.status.value == "approved" and 
                time_off.start_date <= check_date <= time_off.end_date):
                logger.debug(f"Employee {employee.name} has approved time-off on {check_date}")
                return True
        return False
    except Exception as e:
        logger.error(f"Error checking time-off for employee {employee.name}: {e}")
        return False

def can_generate_echo_lab_schedule(week_start: date, published_shifts: List[Shift]) -> bool:
    """
    Check if echo lab schedule can be generated based on published on-call schedule
    """
    logger.info(f"Checking if echo lab schedule can be generated for week starting {week_start}")
    
    try:
        # Check if we have published on-call shifts for the week
        week_end = week_start + timedelta(days=6)
        oncall_shifts = [
            shift for shift in published_shifts
            if shift.location.name in ["JDCH", "W/M"] and
            week_start <= shift.date <= week_end
        ]
        
        # We need at least one on-call shift per day for the week
        required_days = 7
        actual_days = len(set(shift.date for shift in oncall_shifts))
        
        can_generate = actual_days >= required_days
        
        log_business_rule(
            rule_name="echo_lab_generation_check",
            details={
                "week_start": str(week_start),
                "required_days": required_days,
                "actual_days": actual_days,
                "can_generate": can_generate
            },
            success=True
        )
        
        logger.info(f"Echo lab generation check: {actual_days}/{required_days} days covered, can generate: {can_generate}")
        return can_generate
        
    except Exception as e:
        log_business_rule(
            rule_name="echo_lab_generation_check",
            details={
                "week_start": str(week_start),
                "error": str(e)
            },
            success=False
        )
        logger.error(f"Error checking echo lab generation capability: {e}")
        return False

def check_oncall_schedule_published(week_start: date, published_shifts: List[Shift]) -> bool:
    """
    Check if on-call schedule is published for the given week
    """
    logger.info(f"Checking if on-call schedule is published for week starting {week_start}")
    
    try:
        week_end = week_start + timedelta(days=6)
        oncall_shifts = [
            shift for shift in published_shifts
            if shift.location.name in ["JDCH", "W/M"] and
            week_start <= shift.date <= week_end
        ]
        
        # Check if we have shifts for all days of the week
        week_days = set()
        for i in range(7):
            week_days.add(week_start + timedelta(days=i))
        
        covered_days = set(shift.date for shift in oncall_shifts)
        is_published = week_days.issubset(covered_days)
        
        log_business_rule(
            rule_name="oncall_schedule_published_check",
            details={
                "week_start": str(week_start),
                "required_days": len(week_days),
                "covered_days": len(covered_days),
                "is_published": is_published
            },
            success=True
        )
        
        logger.info(f"On-call schedule published check: {len(covered_days)}/{len(week_days)} days covered, published: {is_published}")
        return is_published
        
    except Exception as e:
        log_business_rule(
            rule_name="oncall_schedule_published_check",
            details={
                "week_start": str(week_start),
                "error": str(e)
            },
            success=False
        )
        logger.error(f"Error checking on-call schedule published status: {e}")
        return False 