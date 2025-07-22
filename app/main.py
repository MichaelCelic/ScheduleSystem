from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from strawberry.fastapi import GraphQLRouter
from .schema import schema
from .database import init_db
from .seed_data import seed_database
from .logger import logger, setup_logger
from .middleware import LoggingMiddleware
import traceback

# Set up logging
setup_logger()

app = FastAPI(
    title="Hospital Scheduler API",
    description="A comprehensive hospital staff scheduling system",
    version="1.0.0"
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    """Application startup event handler"""
    logger.info("Starting Hospital Scheduler application")
    
    try:
        logger.info("Initializing database")
        init_db()
        logger.info("Database initialized successfully")
        
        # Seed the database with frontend data
        try:
            logger.info("Seeding database with initial data")
            seed_database()
            logger.info("Database seeded successfully")
        except Exception as e:
            logger.warning(f"Could not seed database: {e}")
            logger.debug(f"Seed error details: {traceback.format_exc()}")
            
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        logger.error(f"Initialization error details: {traceback.format_exc()}")
        raise

@app.on_event("shutdown")
def on_shutdown():
    """Application shutdown event handler"""
    logger.info("Shutting down Hospital Scheduler application")

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with logging"""
    logger.warning(
        f"HTTP exception: {exc.status_code} - {exc.detail}",
        extra={
            "event_type": "http_exception",
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": request.url.path,
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions with logging"""
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "event_type": "unhandled_exception",
            "exception_type": type(exc).__name__,
            "path": request.url.path,
            "method": request.method,
        },
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    logger.debug("Health check requested")
    return {"status": "healthy", "service": "hospital_scheduler"}

# Include GraphQL router
gql_app = GraphQLRouter(schema)
app.include_router(gql_app, prefix="/graphql") 