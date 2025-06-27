import typer
from datetime import date
from .database import get_session
from .models import Employee, Location
from .scheduler import generate_weekly_schedule

app = typer.Typer()

@app.command()
def add_employee(name: str, age: int, max_hours_per_day: int, availability: str):
    """Add a new employee. Availability: comma-separated days (e.g. Mon,Tue,Wed)"""
    from .models import DayOfWeek
    days = [DayOfWeek[d.strip().upper()[:3]] for d in availability.split(",")]
    with get_session() as session:
        employee = Employee(name=name, age=age, max_hours_per_day=max_hours_per_day, availability=days)
        session.add(employee)
        session.commit()
        typer.echo(f"Added employee {name}")

@app.command()
def remove_employee(employee_id: str):
    """Remove an employee by UUID."""
    import uuid
    with get_session() as session:
        employee = session.get(Employee, uuid.UUID(employee_id))
        if not employee:
            typer.echo("Employee not found")
            raise typer.Exit(1)
        session.delete(employee)
        session.commit()
        typer.echo(f"Removed employee {employee_id}")

@app.command()
def regenerate_schedule(week_start: str):
    """Regenerate the schedule for a given week (YYYY-MM-DD)."""
    week_start_date = date.fromisoformat(week_start)
    with get_session() as session:
        employees = session.query(Employee).all()
        locations = session.query(Location).all()
        shifts = generate_weekly_schedule(week_start_date, employees, locations)
        for s in shifts:
            session.add(s)
        session.commit()
        typer.echo(f"Regenerated schedule for week starting {week_start}")

if __name__ == "__main__":
    app() 