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
- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Git** (for cloning the repository)

### Option 1: Manual Setup (Recommended for Development)

#### 1. Backend Setup
```bash
# Navigate to project directory
cd HospitalScheduler

# Create and activate virtual environment
python -m venv .venv
.venv/Scripts/activate  # On Windows
source .venv/bin/activate  # On macOS/Linux

# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at:
- **API**: http://localhost:8000
- **GraphQL Playground**: http://localhost:8000/graphql
- **API Documentation**: http://localhost:8000/docs

#### 2. Frontend Setup
```bash
# Open a new terminal window
cd frontend

# Install Node.js dependencies
npm install

# Start the React development server
npm start
```

The frontend will be available at:
- **Web Application**: http://localhost:3000

### Option 2: Docker Setup (Recommended for Production)

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

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

**Frontend won't start:**
- Ensure Node.js 16+ is installed
- Run `npm install` in the frontend directory
- Check for port conflicts (default: 3000)

**Database issues:**
- Delete `hospital_scheduler.db` to reset the database
- Restart the backend application

**Docker issues:**
- Ensure Docker and Docker Compose are installed
- Check that ports 3000 and 8000 are available
- Run `docker-compose down` before `docker-compose up --build`

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