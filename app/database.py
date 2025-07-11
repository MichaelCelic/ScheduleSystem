from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///./hospital_scheduler.db"
engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    # Import all models to ensure they're registered with SQLModel
    from .models import Employee, Location, Shift, EmployeeAvailabilityLink, TimeOff
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine) 