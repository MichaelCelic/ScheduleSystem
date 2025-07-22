from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.exc import SQLAlchemyError
import time
from .logger import logger, log_database_operation

# Database URL
DATABASE_URL = "sqlite:///./hospital_scheduler.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    connect_args={"check_same_thread": False}
)

def init_db():
    """Initialize the database by creating all tables"""
    start_time = time.time()
    
    try:
        logger.info("Creating database tables")
        SQLModel.metadata.create_all(engine)
        
        duration = (time.time() - start_time) * 1000
        log_database_operation(
            operation="create_tables",
            table="all",
            duration_ms=duration,
            success=True
        )
        logger.info("Database tables created successfully")
        
    except SQLAlchemyError as e:
        duration = (time.time() - start_time) * 1000
        log_database_operation(
            operation="create_tables",
            table="all",
            duration_ms=duration,
            success=False,
            error=str(e)
        )
        logger.error(f"Failed to create database tables: {e}")
        raise
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        log_database_operation(
            operation="create_tables",
            table="all",
            duration_ms=duration,
            success=False,
            error=str(e)
        )
        logger.error(f"Unexpected error creating database tables: {e}")
        raise

def get_session():
    """Get a database session with logging"""
    start_time = time.time()
    
    try:
        session = Session(engine)
        
        # Log successful session creation
        duration = (time.time() - start_time) * 1000
        log_database_operation(
            operation="create_session",
            table="session",
            duration_ms=duration,
            success=True
        )
        
        return session
        
    except SQLAlchemyError as e:
        duration = (time.time() - start_time) * 1000
        log_database_operation(
            operation="create_session",
            table="session",
            duration_ms=duration,
            success=False,
            error=str(e)
        )
        logger.error(f"Failed to create database session: {e}")
        raise
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        log_database_operation(
            operation="create_session",
            table="session",
            duration_ms=duration,
            success=False,
            error=str(e)
        )
        logger.error(f"Unexpected error creating database session: {e}")
        raise

def log_query_execution(operation: str, table: str, query_details: str = None):
    """Decorator to log database query execution"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000
                
                log_database_operation(
                    operation=operation,
                    table=table,
                    duration_ms=duration,
                    success=True
                )
                
                if query_details:
                    logger.debug(f"Query executed successfully: {query_details}")
                
                return result
                
            except SQLAlchemyError as e:
                duration = (time.time() - start_time) * 1000
                log_database_operation(
                    operation=operation,
                    table=table,
                    duration_ms=duration,
                    success=False,
                    error=str(e)
                )
                logger.error(f"Database query failed: {e}")
                raise
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                log_database_operation(
                    operation=operation,
                    table=table,
                    duration_ms=duration,
                    success=False,
                    error=str(e)
                )
                logger.error(f"Unexpected error in database operation: {e}")
                raise
                
        return wrapper
    return decorator 