# 🚀 Quick Start - TAO SDLC AI

## ⚡ Fast Setup (5 Minutes)

### Step 1: Prerequisites Check ✅

Make sure you have:
- [ ] Python 3.9+ (`python --version`)
- [ ] Node.js 16+ (`node --version`)
- [ ] PostgreSQL running
- [ ] OpenAI API Key

---

## 🔧 Setup Instructions

### 1️⃣ Database Setup (2 minutes)

**Option A: Use existing PostgreSQL**
```sql
CREATE DATABASE sdlc;
```

**Option B: Use SQLite (Quick Test)**
- Edit `backend/.env`
- Change `DATABASE_URL` to:
  ```
  DATABASE_URL=sqlite:///./sdlc.db
  ```

### 2️⃣ Backend Setup (2 minutes)

```bash
# Navigate to backend
cd backend

# Create virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure OpenAI API Key
# Edit backend/.env and add your key:
# OPENAI_API_KEY=sk-your-key-here

# Initialize database
python -c "from app.database import engine; from app import models; models.Base.metadata.create_all(bind=engine)"

# Create demo user
python -c "from app.database import SessionLocal; from app.models import User; from passlib.context import CryptContext; db = SessionLocal(); pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto'); user = User(username='demo', email='demo@example.com', full_name='Demo User', hashed_password=pwd_context.hash('demo123'), role='admin', is_active=True); db.add(user); db.commit(); print('✅ Demo user created!')"

# Start backend
uvicorn app.main:app --reload
```

**✅ Backend running at: http://localhost:8000**

### 3️⃣ Frontend Setup (1 minute)

Open **NEW terminal** (keep backend running):

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start frontend
npm run dev
```

**✅ Frontend running at: http://localhost:5173**

---

## 🎯 Test It!

1. **Open Browser**: http://localhost:5173
2. **Click**: "Demo Login" button
3. **Create** a new project
4. **Upload** a document
5. **Extract** requirements with AI
6. **Generate** PRD and BRD

---

## 🔑 Login Credentials

**Demo Account:**
- Username: `demo`
- Password: `demo123`

---

## ⚠️ Common Issues

### Backend won't start?
```bash
# Check if virtual environment is activated
# Should see (venv) in terminal

# If not, activate it:
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### Database error?
```bash
# Option 1: Check PostgreSQL is running
# Option 2: Use SQLite instead (see Step 1)
```

### Frontend won't start?
```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### OpenAI API error?
```bash
# Check your .env file has valid API key:
# OPENAI_API_KEY=sk-proj-...
```

---

## 📁 What's Included?

### Backend (`/backend`)
✅ FastAPI application
✅ AI service with OpenAI integration
✅ Document parser (Excel, Word, PDF, CSV)
✅ Database models and migrations
✅ Authentication system
✅ All API endpoints

### Frontend (`/frontend`)
✅ React + TypeScript application
✅ All pages and components
✅ Tailwind CSS styling
✅ Vite configuration
✅ API integration

---

## 🎉 You're Ready!

After setup, you can:
- ✅ Upload requirement documents
- ✅ Extract requirements with AI
- ✅ Generate PRD automatically
- ✅ Generate BRD automatically
- ✅ Analyze project risks
- ✅ Create epics and user stories
- ✅ Export to PDF
- ✅ Track entire SDLC process

---

## 📖 Full Documentation

See `README.md` for:
- Detailed setup instructions
- API documentation
- Troubleshooting guide
- Production deployment tips

---

## 💡 Pro Tips

1. **Keep backend running** in one terminal
2. **Keep frontend running** in another terminal
3. **Check console logs** if something doesn't work
4. **Use Demo Login** for quick access
5. **Read README.md** for advanced features

---

**Need Help?** Check the full `README.md` file! 📚

**Happy Coding! 🚀**

