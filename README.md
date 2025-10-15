# TAO SDLC AI - Version 1

## 🚀 Quick Start Guide

This is a complete, production-ready SDLC management system with AI-powered features including requirement extraction, PRD/BRD generation, risk analysis, and more.

---

## 📋 Prerequisites

Before you start, ensure you have:

1. **Python 3.9+** installed
2. **Node.js 16+** and npm installed
3. **PostgreSQL** database running
4. **OpenAI API Key** (for AI features)

---

## 🗄️ Database Setup

### Option 1: PostgreSQL (Recommended)

1. **Install PostgreSQL** (if not already installed):
   - Download from https://www.postgresql.org/download/
   - Install and remember your password

2. **Create Database**:
   ```sql
   -- Connect to PostgreSQL
   psql -U postgres
   
   -- Create database
   CREATE DATABASE sdlc;
   
   -- Create user (optional)
   CREATE USER admin_user WITH PASSWORD 'Postgres9527';
   GRANT ALL PRIVILEGES ON DATABASE sdlc TO admin_user;
   ```

3. **Update Connection** (if different):
   - Edit `backend/.env`
   - Update `DATABASE_URL` if needed

---

## 🔧 Backend Setup

### Step 1: Navigate to Backend
```bash
cd backend
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Edit `backend/.env` file:
```env
# OpenAI API Key (REQUIRED for AI features)
OPENAI_API_KEY=your-openai-api-key-here

# Database URL
DATABASE_URL=postgresql://admin_user:Postgres9527@localhost:5432/sdlc

# JWT Secret (change in production)
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**⚠️ IMPORTANT**: Replace `your-openai-api-key-here` with your actual OpenAI API key!

### Step 5: Initialize Database
```bash
# From backend directory
python -c "from app.database import engine; from app import models; models.Base.metadata.create_all(bind=engine)"
```

### Step 6: Create Demo User (Optional)
```bash
python -c "from app.database import SessionLocal, engine; from app.models import User, Base; from passlib.context import CryptContext; Base.metadata.create_all(bind=engine); db = SessionLocal(); pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto'); user = User(username='demo', email='demo@example.com', full_name='Demo User', hashed_password=pwd_context.hash('demo123'), role='admin', is_active=True); db.add(user); db.commit(); print('Demo user created: username=demo, password=demo123')"
```

### Step 7: Start Backend Server
```bash
uvicorn app.main:app --reload
```

✅ Backend should now be running at: **http://localhost:8000**

---

## 🎨 Frontend Setup

### Step 1: Open New Terminal

Keep the backend running and open a **new terminal window**

### Step 2: Navigate to Frontend
```bash
cd frontend
```

### Step 3: Install Dependencies
```bash
npm install
```

### Step 4: Start Development Server
```bash
npm run dev
```

✅ Frontend should now be running at: **http://localhost:5173**

---

## 🌐 Access the Application

1. **Open your browser**
2. **Navigate to**: http://localhost:5173
3. **Login**:
   - Username: `demo`
   - Password: `demo123`
   - Or click "Demo Login" button

---

## 🎯 Features Overview

### Phase 1: Requirements & Analysis
- ✅ **Document Upload** - Upload Excel, Word, PDF, CSV files
- ✅ **AI-Powered Requirement Extraction** - Extracts and converts to Gherkin format
- ✅ **PRD Generation** - AI generates comprehensive Product Requirements Document
- ✅ **BRD Generation** - AI generates comprehensive Business Requirements Document
- ✅ **Risk Analysis** - AI analyzes requirements and identifies project risks
- ✅ **Export to PDF** - Save PRD/BRD as professional PDF files

### Phase 2: Planning & Backlog
- ✅ **Epic Generation** - AI creates epics from requirements
- ✅ **User Story Generation** - AI generates detailed user stories
- ✅ **Sprint Planning** - Organize stories into sprints

### Phase 3: Architecture & Design
- ✅ **Architecture Design** - Create system architecture
- ✅ **JIRA Integration** - Export to JIRA

### Phase 4-6: Development, Testing, Deployment
- ✅ **Progress Tracking**
- ✅ **Approval Workflows**
- ✅ **Deployment Management**

---

## 🔑 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/demo` - Demo login
- `POST /api/auth/signup` - User registration

### Projects
- `GET /api/projects/` - List all projects
- `POST /api/projects/` - Create new project
- `GET /api/projects/{id}` - Get project details

### AI Copilot
- `POST /api/ai/generate/{phase_id}` - Generate content (PRD, BRD, Epics, Stories)
- `POST /api/ai/analyze-risks/{phase_id}` - Analyze project risks
- `POST /api/ai/extract-requirements` - Extract requirements from documents

---

## 🐛 Troubleshooting

### Backend Issues

**Error: Database connection failed**
- Check PostgreSQL is running
- Verify DATABASE_URL in `.env`
- Ensure database `sdlc` exists

**Error: ModuleNotFoundError**
- Activate virtual environment
- Run `pip install -r requirements.txt`

**Error: OpenAI API error**
- Verify OPENAI_API_KEY in `.env`
- Check API key is valid
- Ensure you have OpenAI credits

### Frontend Issues

**Error: Cannot connect to backend**
- Ensure backend is running on port 8000
- Check `vite.config.ts` proxy settings

**Error: npm install fails**
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again

---

## 📁 Project Structure

```
SDLC_AI_version1/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── database.py          # Database configuration
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── routers/             # API endpoints
│   │   │   ├── auth.py
│   │   │   ├── projects.py
│   │   │   ├── phases.py
│   │   │   ├── ai_copilot.py   # AI features
│   │   │   └── ...
│   │   └── services/            # Business logic
│   │       ├── ai_service.py    # OpenAI integration
│   │       └── document_parser.py
│   ├── .env                     # Environment variables
│   └── requirements.txt         # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── pages/               # React pages
│   │   ├── components/          # React components
│   │   ├── services/            # API services
│   │   └── App.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── index.html
│
└── README.md                    # This file
```

---

## 🔒 Security Notes

### Production Deployment

1. **Change SECRET_KEY** in `.env`
2. **Use strong database password**
3. **Enable HTTPS**
4. **Set proper CORS origins** in `main.py`
5. **Secure OpenAI API key** (use environment variables)
6. **Regular security updates**

---

## 💰 Cost Considerations

### OpenAI API Usage
- Requirements Extraction: ~$0.002-$0.005 per document
- PRD Generation: ~$0.001-$0.003 per document
- BRD Generation: ~$0.001-$0.003 per document
- Risk Analysis: ~$0.0003-$0.001 per analysis
- **Average per project**: Less than $0.01

---

## 🆘 Support

### Common Commands

**Backend**:
```bash
# Start server
uvicorn app.main:app --reload

# Run on different port
uvicorn app.main:app --reload --port 8001

# Check database
python -c "from app.database import engine; print(engine)"
```

**Frontend**:
```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## 📝 Environment Variables Reference

### Backend (.env)
```env
# Required
OPENAI_API_KEY=sk-...                    # Your OpenAI API key
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Optional (has defaults)
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## ✅ Quick Verification

After setup, verify everything works:

1. ✅ Backend runs at http://localhost:8000
2. ✅ Frontend runs at http://localhost:5173
3. ✅ Can login with demo/demo123
4. ✅ Can create a project
5. ✅ Can upload documents
6. ✅ AI features work (PRD, BRD, Risk Analysis)

---

## 🎉 You're Ready!

Your TAO SDLC AI application is now set up and ready to use!

### Next Steps:
1. Create your first project
2. Upload requirement documents
3. Extract requirements with AI
4. Generate PRD and BRD
5. Analyze project risks
6. Plan your sprints

**Happy coding! 🚀**

---

## 📞 Additional Information

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **AI**: OpenAI GPT-4o-mini
- **Authentication**: JWT tokens
- **Database**: PostgreSQL

**Version**: 1.0
**Last Updated**: January 2025

