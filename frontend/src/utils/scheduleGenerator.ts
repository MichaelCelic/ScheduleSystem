import { addDays, format, isSameDay, startOfWeek } from 'date-fns';

interface Employee {
  id: string;
  name: string;
  availability: {
    days: string[];
    maxHoursPerDay: number;
    preferredShifts: string[];
  };
}

interface Location {
  id: string;
  name: string;
  requiredStaff?: {
    morning: number;
    afternoon: number;
    night: number;
  };
}

interface Shift {
  employeeId: string;
  employeeName: string;
  date: Date;
  shiftType: 'morning' | 'afternoon' | 'night';
}

interface Schedule {
  id: string;
  locationId: string;
  locationName: string;
  weekStart: Date;
  shifts: {
    [key: string]: {
      morning: string[];
      afternoon: string[];
      night: string[];
    };
  };
  status: 'draft' | 'published';
}

// New assignment pool for randomization
const ASSIGNMENT_POOL = [
  'Inpatients',
  'Cath/Inpat.',
  'OR/Inpat.',
  'Sedat./Inpat.',
  'MWH/MHM',
  'THC',
  'TX-Inpat.',
  'PTO',
  'N/A',
  '',
];

// New Schedule interface for staff assignment layout
interface StaffAssignmentSchedule {
  id: string;
  locationId: string;
  locationName: string;
  weekStart: Date;
  assignments: {
    [employeeName: string]: {
      [day: string]: string; // e.g., { Monday: 'Inpatients', ... }
    };
  };
  status: 'draft' | 'published';
}

const SHIFT_HOURS = {
  morning: 8,
  afternoon: 8,
  night: 8,
};

const SHIFT_TIMES = {
  morning: '6AM-2PM',
  afternoon: '2PM-10PM',
  night: '10PM-6AM',
};

// Utility to shuffle an array
function shuffleArray<T>(array: T[]): T[] {
  const arr = [...array];
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

export class ScheduleGenerator {
  private employees: Employee[];
  private location: Location;
  private weekStart: Date;
  private previousWeekSchedule?: Schedule;

  constructor(
    employees: Employee[],
    location: Location,
    weekStart: Date,
    previousWeekSchedule?: Schedule
  ) {
    this.employees = employees;
    this.location = {
      ...location,
      requiredStaff: location.requiredStaff || {
        morning: 3,
        afternoon: 3,
        night: 2,
      }
    };
    this.weekStart = startOfWeek(weekStart);
    this.previousWeekSchedule = previousWeekSchedule;
  }

  private getDayOfWeek(date: Date): string {
    return format(date, 'EEEE');
  }

  private isEmployeeAvailable(employee: Employee, date: Date, shiftType: string): boolean {
    const dayOfWeek = this.getDayOfWeek(date);
    return (
      employee.availability.days.includes(dayOfWeek) &&
      employee.availability.preferredShifts.includes(`${shiftType} (${SHIFT_TIMES[shiftType as keyof typeof SHIFT_TIMES]})`)
    );
  }

  private getEmployeeShiftCount(employee: Employee, shifts: Shift[]): number {
    return shifts.filter(shift => shift.employeeId === employee.id).length;
  }

  private getEmployeeHoursForDay(employee: Employee, date: Date, shifts: Shift[]): number {
    return shifts
      .filter(shift => shift.employeeId === employee.id && isSameDay(shift.date, date))
      .reduce((total, shift) => total + SHIFT_HOURS[shift.shiftType as keyof typeof SHIFT_HOURS], 0);
  }

  private hadShiftLastWeek(employee: Employee, date: Date, shiftType: string): boolean {
    if (!this.previousWeekSchedule) return false;

    const lastWeekDate = addDays(date, -7);
    const dayOfWeek = this.getDayOfWeek(lastWeekDate);
    const lastWeekShifts = this.previousWeekSchedule.shifts[dayOfWeek][shiftType as keyof typeof SHIFT_TIMES];

    return lastWeekShifts.includes(employee.name);
  }

  private findBestEmployeeForShift(
    date: Date,
    shiftType: string,
    currentShifts: Shift[]
  ): Employee | null {
    const availableEmployees = this.employees.filter(employee =>
      this.isEmployeeAvailable(employee, date, shiftType)
    );

    if (availableEmployees.length === 0) return null;

    // Shuffle available employees for randomization
    const shuffledEmployees = shuffleArray(availableEmployees);

    // Score each employee based on various factors
    const scoredEmployees = shuffledEmployees.map(employee => {
      let score = 0;
      if (!this.hadShiftLastWeek(employee, date, shiftType)) {
        score += 3;
      }
      const shiftCount = this.getEmployeeShiftCount(employee, currentShifts);
      score += (5 - shiftCount) * 2;
      const hoursToday = this.getEmployeeHoursForDay(employee, date, currentShifts);
      if (hoursToday < employee.availability.maxHoursPerDay) {
        score += 2;
      }
      if (employee.availability.preferredShifts.includes(shiftType)) {
        score += 1;
      }
      return { employee, score };
    });

    scoredEmployees.sort((a, b) => b.score - a.score);
    return scoredEmployees[0]?.employee || null;
  }

  public generateSchedule(): StaffAssignmentSchedule {
    const schedule: StaffAssignmentSchedule = {
      id: Date.now().toString() + Math.random().toString(36).substring(2),
      locationId: this.location.id,
      locationName: this.location.name,
      weekStart: this.weekStart,
      assignments: {},
      status: 'draft',
    };

    for (const employee of this.employees) {
      schedule.assignments[employee.name] = {};
      for (let i = 0; i < 7; i++) {
        const date = addDays(this.weekStart, i);
        const dayOfWeek = this.getDayOfWeek(date);
        // Only assign if employee is available that day
        if (employee.availability.days.includes(dayOfWeek)) {
          // Randomly pick an assignment from the pool (excluding blank)
          const possibleAssignments = ASSIGNMENT_POOL.filter(a => a !== '');
          const assignment = possibleAssignments[Math.floor(Math.random() * possibleAssignments.length)];
          schedule.assignments[employee.name][dayOfWeek] = assignment;
        } else {
          schedule.assignments[employee.name][dayOfWeek] = '';
        }
      }
    }
    return schedule;
  }

  // Generate randomized On Call assignments for a week
  public generateRandomOnCallAssignments(schedules: Schedule[], locationNames: string[]): Record<string, string[]> {
    // For each location, get all employees scheduled for that week
    const onCallAssignments: Record<string, string[]> = {};
    locationNames.forEach(locationName => {
      const schedule = schedules.find(s => s.locationName === locationName);
      if (!schedule) {
        onCallAssignments[locationName] = Array(7).fill('');
        return;
      }
      // Collect all unique employees scheduled for the week
      const allEmployees = new Set<string>();
      Object.values(schedule.shifts).forEach(dayShifts => {
        Object.values(dayShifts).forEach(shiftArr => {
          shiftArr.forEach(emp => allEmployees.add(emp));
        });
      });
      // Shuffle employees for random on call order
      const shuffled = shuffleArray(Array.from(allEmployees));
      // Assign one per day, cycling if needed
      const weekOnCall = Array(7).fill('').map((_, i) => shuffled[i % shuffled.length] || '');
      onCallAssignments[locationName] = weekOnCall;
    });
    return onCallAssignments;
  }
} 