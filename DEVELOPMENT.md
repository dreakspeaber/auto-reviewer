# Development Workflow

## Git Branching Strategy

We follow a feature branch workflow with the following structure:

### Main Branches
- `main` - Production-ready code
- `develop` - Integration branch for features

### Feature Branches
- `feature/TASK-ID-description` - For new features
- `bugfix/TASK-ID-description` - For bug fixes
- `hotfix/TASK-ID-description` - For urgent production fixes

## Task Management

Each task should be broken down into granular, single-responsibility subtasks with assigned task IDs.

### Task ID Format
- `TASK-001` - Initial project setup
- `TASK-002` - Frontend markdown editor implementation
- `TASK-003` - Backend API endpoint development
- `TASK-004` - GCP AI integration
- etc.

## Development Process

### 1. Starting a New Task
```bash
# Create a new feature branch from main
git checkout main
git pull origin main
git checkout -b feature/TASK-XXX-description
```

### 2. Development Workflow
```bash
# Make your changes
# Add files
git add .

# Commit with conventional commit format
git commit -m "feat: Add new feature description"
git commit -m "fix: Fix bug description"
git commit -m "docs: Update documentation"
git commit -m "refactor: Refactor code description"
```

### 3. Completing a Task
```bash
# Push your feature branch
git push origin feature/TASK-XXX-description

# Create a Pull Request to main
# Ensure all tests pass
# Get code review approval
# Merge to main
```

### 4. Rebase Strategy
```bash
# Before merging, rebase on main
git checkout main
git pull origin main
git checkout feature/TASK-XXX-description
git rebase main

# Resolve any conflicts
# Force push if needed (only on feature branches)
git push --force-with-lease origin feature/TASK-XXX-description
```

## Environment Setup

### Prerequisites
- Node.js (v16 or higher)
- Python (v3.8 or higher)
- Git

### Initial Setup
```bash
# Clone the repository
git clone <repository-url>
cd auto-reviewer

# Setup Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
npm run install:all
```

### Development Commands
```bash
# Start both frontend and backend
npm run dev

# Start only frontend
npm run dev:frontend

# Start only backend
npm run dev:backend

# Install frontend dependencies
npm run install:frontend

# Install backend dependencies
npm run install:backend
```

## Code Standards

### Frontend (React/TypeScript)
- Use TypeScript for all new code
- Follow ESLint rules
- Use shadcn/ui components
- Write meaningful component names
- Add proper TypeScript interfaces

### Backend (FastAPI/Python)
- Use type hints
- Follow PEP 8 style guide
- Use Pydantic models for data validation
- Add proper docstrings
- Handle errors gracefully

### Git Commit Messages
Use conventional commit format:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

## Testing

### Frontend Testing
```bash
cd front
npm test
```

### Backend Testing
```bash
cd back
source ../venv/bin/activate
pytest
```

## Deployment

### Frontend Build
```bash
npm run build:frontend
```

### Backend Deployment
```bash
cd back
source ../venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

## Environment Variables

Create `.env` files for local development:

### Backend (.env in back/ directory)
```env
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=global
```

### Frontend (.env in front/ directory)
```env
VITE_API_URL=http://localhost:8000
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Kill processes on ports 3000 and 8000
   lsof -ti:3000 | xargs kill -9
   lsof -ti:8000 | xargs kill -9
   ```

2. **Virtual environment not activated**
   ```bash
   source venv/bin/activate
   ```

3. **Node modules issues**
   ```bash
   cd front
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **Python dependencies issues**
   ```bash
   cd back
   source ../venv/bin/activate
   pip install -r requirements.txt --force-reinstall
   ```
