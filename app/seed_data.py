import uuid
from datetime import date
from sqlmodel import select, delete
from .database import get_session
from .models import Employee, Location, EmployeeAvailabilityLink, EmployeeRole, DayOfWeek, Shift, TimeOff, TimeOffStatus

def seed_database():
    """Seed the database with employee and location data from frontend"""
    with get_session() as session:
        # Clear existing data (ignore errors if tables don't exist)
        try:
            session.exec(delete(TimeOff))
            session.exec(delete(EmployeeAvailabilityLink))
            session.exec(delete(Shift))
            session.exec(delete(Employee))
            session.exec(delete(Location))
            session.commit()
        except Exception:
            # Tables might not exist yet, which is fine
            session.rollback()
        
        # Create employees with specific IDs
        employees_data = [
            {
                "id": uuid.UUID("7b57a3aa-afa2-41ff-bcb4-768d9d2bcbf2"),
                "name": "Martha",
                "age": 35,
                "role": EmployeeRole.STAFF,
                "max_hours_per_day": 10.5,
                "availability": {
                    "days": ["Monday", "Tuesday", "Thursday", "Friday", "Saturday"],
                    "preferred_shifts": ["Morning (6AM-2PM)", "Afternoon (2PM-10PM)"]
                }
            },
            {
                "id": uuid.UUID("ba1de010-5637-4855-a865-c7b44e9c578e"),
                "name": "Grisel",
                "age": 28,
                "role": EmployeeRole.STAFF,
                "max_hours_per_day": 8.5,
                "availability": {
                    "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
                    "preferred_shifts": ["Morning (6AM-2PM)", "Afternoon (2PM-10PM)"]
                }
            },
            {
                "id": uuid.UUID("5a02f738-fe7d-4859-86a3-d89710484344"),
                "name": "Emilio",
                "age": 32,
                "role": EmployeeRole.STAFF,
                "max_hours_per_day": 8.5,
                "availability": {
                    "days": ["Tuesday", "Wednesday", "Thursday", "Friday"],
                    "preferred_shifts": ["Afternoon (2PM-10PM)", "Night (10PM-6AM)"]
                }
            },
            {
                "id": uuid.UUID("1ba91002-ea3a-4377-bc2a-9bab3d4de5b7"),
                "name": "Annie",
                "age": 29,
                "role": EmployeeRole.STAFF,
                "max_hours_per_day": 8.5,
                "availability": {
                    "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                    "preferred_shifts": ["Morning (6AM-2PM)", "Night (10PM-6AM)"]
                }
            },
            {
                "id": uuid.UUID("9f1754d4-d387-4b71-923a-e731dfdd9a72"),
                "name": "Angela",
                "age": 31,
                "role": EmployeeRole.STAFF,
                "max_hours_per_day": 8.5,
                "availability": {
                    "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                    "preferred_shifts": ["Afternoon (2PM-10PM)", "Night (10PM-6AM)"]
                }
            },
            {
                "id": uuid.UUID("685265d0-5ed5-46a8-8db7-6c637f847e5a"),
                "name": "Alexandra",
                "age": 27,
                "role": EmployeeRole.STAFF,
                "max_hours_per_day": 8.5,
                "availability": {
                    "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                    "preferred_shifts": ["Morning (6AM-2PM)", "Afternoon (2PM-10PM)"]
                }
            },
            {
                "id": uuid.UUID("26115c86-90d8-4759-8e7d-ef21183b1e60"),
                "name": "Shannon",
                "age": 33,
                "role": EmployeeRole.STAFF,
                "max_hours_per_day": 8.5,
                "availability": {
                    "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                    "preferred_shifts": ["Night (10PM-6AM)", "Afternoon (2PM-10PM)"]
                }
            },
            {
                "id": uuid.UUID("2d5bc4ac-f250-46dc-a0dd-3747c9b217a8"),
                "name": "Guadalupe",
                "age": 30,
                "role": EmployeeRole.STAFF,
                "max_hours_per_day": 8.5,
                "availability": {
                    "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                    "preferred_shifts": ["Morning (6AM-2PM)", "Night (10PM-6AM)"]
                }
            },
            {
                "id": uuid.UUID("8c38d6f4-199d-4a9a-aaf6-0de5a7d27ff2"),
                "name": "William",
                "age": 24,
                "role": EmployeeRole.STUDENT,
                "max_hours_per_day": 8.0,
                "availability": {
                    "days": ["Monday", "Tuesday", "Wednesday", "Thursday"],
                    "preferred_shifts": ["Morning (6AM-2PM)", "Afternoon (2PM-10PM)", "Night (10PM-6AM)"]
                }
            }
        ]
        
        # Day mapping from frontend to backend
        day_mapping = {
            "Monday": DayOfWeek.MON,
            "Tuesday": DayOfWeek.TUE,
            "Wednesday": DayOfWeek.WED,
            "Thursday": DayOfWeek.THU,
            "Friday": DayOfWeek.FRI,
            "Saturday": DayOfWeek.SAT,
            "Sunday": DayOfWeek.SUN
        }
        
        # Create employees
        for emp_data in employees_data:
            employee = Employee(
                id=emp_data["id"],
                name=emp_data["name"],
                age=emp_data["age"],
                role=emp_data["role"],
                max_hours_per_day=emp_data["max_hours_per_day"]
            )
            session.add(employee)
            session.commit()
            session.refresh(employee)
            
            # Add availability links
            for day_name in emp_data["availability"]["days"]:
                day_enum = day_mapping[day_name]
                availability_link = EmployeeAvailabilityLink(
                    employee_id=employee.id,
                    day=day_enum,
                    preferred_shifts=",".join(emp_data["availability"]["preferred_shifts"])
                )
                session.add(availability_link)
            
            session.commit()
        

        
        # Create locations (data from SchedulerContext.tsx)
        locations_data = [
            {
                "name": "JDCH",
                "address": "123 JDCH Ave",
                "required_staff_morning": 3,
                "required_staff_afternoon": 3,
                "required_staff_night": 2,
                "notes": ""
            },
            {
                "name": "W/M",
                "address": "456 W/M Blvd",
                "required_staff_morning": 2,
                "required_staff_afternoon": 2,
                "required_staff_night": 1,
                "notes": ""
            },
            {
                "name": "On Call Fetal",
                "address": "789 Fetal Care Dr",
                "required_staff_morning": 1,
                "required_staff_afternoon": 1,
                "required_staff_night": 1,
                "notes": "Fetal care on-call coverage"
            }
        ]
        
        for loc_data in locations_data:
            location = Location(
                id=uuid.uuid4(),
                name=loc_data["name"],
                address=loc_data["address"],
                required_staff_morning=loc_data["required_staff_morning"],
                required_staff_afternoon=loc_data["required_staff_afternoon"],
                required_staff_night=loc_data["required_staff_night"],
                notes=loc_data["notes"]
            )
            session.add(location)
        
        session.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database() 