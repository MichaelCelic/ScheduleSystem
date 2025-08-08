# HospitalScheduler

A comprehensive hospital staff scheduling system with a modern React frontend and FastAPI backend. This application helps hospital administrators manage employee schedules, locations, and shift assignments efficiently.

## 🏥 What This Program Does

### Core Features
- **Employee Management**: Add, edit, and manage hospital staff with their availability preferences
- **Location Management**: Manage different hospital locations (JDCH, W/M)
- **Schedule Generation**: Automatically generate weekly schedules based on employee availability and preferences
- **Role-Based Scheduling**: Support for different employee roles (staff, student)
- **On-Call Scheduling**: Separate scheduling for on-call shifts
- **Live Data Updates**: Real-time updates across the application using React Context
- **Draft & Published Schedules**: Generate multiple draft schedules and publish the best one

### Key Components
- **Dashboard**: Overview of employees, locations, and schedule statistics
- **Employees Page**: Manage staff information, availability, and roles
- **Locations Page**: Manage hospital locations and departments
- **Schedules Page**: Generate, view, and publish weekly schedules with sub-tabs for different schedule types

## 🚀 Quick Start

### Prerequisites
- **Python 3.8-3.11** with pip
- **Node.js 16.0+** with npm
- **Git** (for cloning the repository)
- **4GB RAM** (recommended for development)
- **Modern web browser** (Chrome, Firefox, Safari, Edge)

## ⚡ Quick 5-Minute Setup

```bash
# Clone and setup
git clone <repository-url>
cd HospitalScheduler

# Backend (Terminal 1)
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (Terminal 2)
cd frontend
npm install
npm start
```

Visit http://localhost:3000 to start scheduling! 🚀

## 🚨 IMPORTANT: Launch Backend and Frontend Individually

**⚠️ CRITICAL: You MUST start the backend and frontend in separate terminal windows to avoid PowerShell syntax errors.**

### Step 1: Start Backend (Terminal 1)
```powershell
# Navigate to project directory
cd C:\Users\epicg\PycharmProjects\HospitalScheduler

# Activate virtual environment
& c:/Users/epicg/PycharmProjects/HospitalScheduler/.venv/Scripts/Activate.ps1

# Start FastAPI backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend will be available at:**
- **API**: http://localhost:8000
- **GraphQL Playground**: http://localhost:8000/graphql
- **API Documentation**: http://localhost:8000/docs

### Step 2: Start Frontend (Terminal 2)
```powershell
# Open a NEW terminal window
# Navigate to frontend directory
cd C:\Users\epicg\PycharmProjects\HospitalScheduler\frontend

# Start React development server
npm start
```

**Frontend will be available at:**
- **Web Application**: http://localhost:3000

### ❌ What NOT to do:
```powershell
# DON'T use bash syntax in PowerShell - this will cause errors:
cd /c/Users/epicg/PycharmProjects/HospitalScheduler && .venv/Scripts/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# DON'T try to start both services in one command:
npm start && uvicorn app.main:app --reload
```

### ✅ What TO do:
- Use separate terminal windows for each service
- Use PowerShell syntax (not bash syntax)
- Start backend first, then frontend
- Keep both terminals open while using the application

## 🔌 API Examples

### Sample GraphQL Queries

**Fetch All Employees:**
```graphql
query GetEmployees {
  employees {
    id
    name
    age
    maxHoursPerDay
    role
    availability {
      dayOfWeek
      isAvailable
    }
  }
}
```

**Generate Schedule:**
```graphql
mutation GenerateSchedule($weekStart: String!, $scheduleType: String!) {
  generateSchedule(weekStart: $weekStart, scheduleType: $scheduleType) {
    success
    message
    shifts {
      id
      employeeName
      locationName
      startTime
      endTime
    }
  }
}
```

**Publish Schedule:**
```graphql
mutation PublishSchedule($weekStart: String!) {
  publishSchedule(weekStart: $weekStart) {
    success
    message
    publishedShifts {
      id
      employeeName
      locationName
      startTime
      endTime
    }
  }
}
```

## 👨‍💻 Development Workflow

### Code Style
- **Backend**: Follow PEP 8 with Black formatter
- **Frontend**: Use Prettier for code formatting
- **TypeScript**: Strict mode enabled

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-schedule-type

# Make changes and test
npm test  # Frontend tests
pytest    # Backend tests

# Commit with conventional commits
git commit -m "feat: add new schedule type support"

# Push and create PR
git push origin feature/new-schedule-type
```

### Testing Strategy
- **Unit Tests**: Core business logic
- **Integration Tests**: API endpoints
- **E2E Tests**: Critical user workflows

## ⚡ Performance Guidelines

### Expected Performance
- **Schedule Generation**: < 5 seconds for 50 employees
- **API Response Time**: < 200ms for standard queries
- **Frontend Load Time**: < 3 seconds on 3G connection

### Optimization Tips
- Use pagination for large employee lists
- Implement caching for frequently accessed data
- Optimize GraphQL queries to fetch only needed fields

## 🔒 Security Considerations

### Data Protection
- All employee data is stored locally (SQLite)
- No external API calls or data transmission
- Database file should be backed up regularly

### Access Control
- Currently designed for single-organization use
- Consider implementing user authentication for multi-tenant scenarios
- Regular database backups recommended

### Production Deployment
- Use environment variables for sensitive configuration
- Implement proper logging and monitoring
- Consider using PostgreSQL for production databases

## 🚀 Production Deployment

### Environment Setup
```bash
# Production environment variables
DATABASE_URL=postgresql://user:pass@localhost/hospital_scheduler
DEBUG=False
LOG_LEVEL=INFO
CORS_ORIGINS=https://yourdomain.com
```

### Docker Production
```bash
# Build production image
docker build -t hospital-scheduler:latest .

# Run with production settings
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e DEBUG=False \
  hospital-scheduler:latest
```

### Monitoring
- Health check endpoint: `GET /health`
- Log files location: `logs/`
- Database backup: `hospital_scheduler_data/`

## 📁 Project Structure

```
HospitalScheduler/
├── app/                    # FastAPI backend
│   ├── __init__.py
│   ├── main.py            # FastAPI application entry point
│   ├── models.py          # SQLModel database models
│   ├── schema.py          # GraphQL schema definitions
│   ├── database.py        # Database initialization and setup
│   ├── scheduler.py       # Schedule generation logic
│   ├── cli.py             # Command-line interface
│   └── graphql_types.py   # GraphQL type definitions
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Main application pages
│   │   ├── utils/         # Utility functions
│   │   └── App.tsx        # Main React application
│   ├── package.json       # Node.js dependencies
│   └── tsconfig.json      # TypeScript configuration
├── tests/                 # Test files
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Docker configuration
└── README.md             # This file
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Strawberry GraphQL**: GraphQL implementation
- **SQLModel**: SQL database ORM
- **SQLite**: Database (can be easily changed to PostgreSQL/MySQL)
- **Pydantic**: Data validation

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type-safe JavaScript
- **Material-UI (MUI)**: Component library
- **Apollo Client**: GraphQL client
- **React Router**: Navigation
- **Date-fns**: Date manipulation

## 📊 Database Schema

The application uses the following main entities:
- **Employee**: Staff members with availability preferences
- **Location**: Hospital locations (JDCH, W/M)
- **Shift**: Individual work assignments
- **EmployeeAvailabilityLink**: Employee availability by day of week

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory for custom configuration:
```env
DATABASE_URL=sqlite:///./hospital_scheduler.db
DEBUG=True
```

### Database
The application uses SQLite by default. The database file (`hospital_scheduler.db`) will be created automatically on first run.

## 🧪 Testing

```bash
# Run backend tests
pytest

# Run frontend tests
cd frontend
npm test
```

## 📝 Usage Guide

### 1. Adding Employees
1. Navigate to the Employees page
2. Click "Add Employee"
3. Fill in name, age, max hours per day, and availability
4. Select role (staff/student)
5. Save the employee

### 2. Managing Locations
1. Go to the Locations page
2. Add or edit hospital locations
3. Default locations: JDCH (main hospital), W/M (on-call)

### 3. Generating Schedules
1. Navigate to the Schedules page
2. Select "Draft Schedules" tab
3. Choose schedule type (Echo Lab or On Call)
4. Set week start date
5. Click "Generate Schedule"
6. Review generated schedules and publish the best one

### 4. Viewing Published Schedules
1. Go to the "Published Schedules" tab
2. View current and historical schedules
3. Use sub-tabs to switch between Echo Lab and On Call schedules

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
- Ensure Python 3.8+ is installed
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify the virtual environment is activated
- **IMPORTANT**: Use PowerShell syntax, not bash syntax

**Frontend won't start:**
- Ensure Node.js 16+ is installed
- Run `npm install` in the frontend directory
- Check for port conflicts (default: 3000)
- **IMPORTANT**: Start in a separate terminal from backend

**PowerShell syntax errors:**
- **Problem**: Using `&&` or bash commands in PowerShell
- **Solution**: Use separate terminal windows for each service
- **Example**: Don't use `command1 && command2`, use separate terminals

**Database issues:**
- Delete `hospital_scheduler.db` to reset the database
- Restart the backend application

**Docker issues:**
- Ensure Docker and Docker Compose are installed
- Check that ports 3000 and 8000 are available
- Run `docker-compose down` before `docker-compose up --build`

**Port already in use:**
```powershell
# Check what's using port 8000
netstat -ano | findstr :8000

# Check what's using port 3000
netstat -ano | findstr :3000

# Kill process if needed (replace PID with actual process ID)
taskkill /PID <PID> /F
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the GraphQL playground at http://localhost:8000/graphql
3. Check the API documentation at http://localhost:8000/docs
4. Open an issue in the repository

---

**Happy Scheduling! 🏥✨** 