# 📁 Folder Structure

```
SDLC_AI_version1/
│
├── 📄 README.md                    # Complete documentation
├── 📄 START_HERE.md                # Quick start guide (read this first!)
├── 📄 FOLDER_STRUCTURE.md          # This file
├── 📄 .gitignore                   # Git ignore rules
├── 🚀 start_backend.bat            # Windows: Start backend server
├── 🚀 start_frontend.bat           # Windows: Start frontend server
│
├── 📂 backend/                     # Python FastAPI Backend
│   ├── 📂 app/                     # Main application code
│   │   ├── 📄 __init__.py
│   │   ├── 📄 main.py              # FastAPI entry point
│   │   ├── 📄 database.py          # Database configuration
│   │   ├── 📄 models.py            # SQLAlchemy models (User, Project, Phase)
│   │   ├── 📄 models_integrations.py # Integration models
│   │   ├── 📄 schemas.py           # Pydantic schemas
│   │   │
│   │   ├── 📂 routers/             # API endpoints
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 auth.py          # Authentication endpoints
│   │   │   ├── 📄 projects.py      # Project CRUD
│   │   │   ├── 📄 phases.py        # Phase management
│   │   │   ├── 📄 approvals.py     # Approval workflows
│   │   │   ├── 📄 ai_copilot.py    # AI features (PRD, BRD, Risks)
│   │   │   ├── 📄 users.py         # User management
│   │   │   ├── 📄 integrations.py  # External integrations
│   │   │   └── 📄 chat.py          # AI chat
│   │   │
│   │   └── 📂 services/            # Business logic
│   │       ├── 📄 __init__.py
│   │       ├── 📄 ai_service.py    # OpenAI integration
│   │       └── 📄 document_parser.py # Document parsing
│   │
│   ├── 📄 .env                     # Environment variables (IMPORTANT!)
│   └── 📄 requirements.txt         # Python dependencies
│
└── 📂 frontend/                    # React TypeScript Frontend
    ├── 📂 src/                     # Source code
    │   ├── 📂 pages/               # React pages
    │   │   ├── 📄 LoginPage.tsx
    │   │   ├── 📄 DashboardPage.tsx
    │   │   ├── 📄 ProjectsPage.tsx
    │   │   ├── 📄 Phase1Page.tsx   # Requirements & Analysis
    │   │   ├── 📄 Phase2Page.tsx   # Planning & Backlog
    │   │   ├── 📄 Phase3Page.tsx   # Architecture & Design
    │   │   ├── 📄 Phase4Page.tsx   # Detailed Design
    │   │   ├── 📄 Phase5Page.tsx   # Development & Testing
    │   │   ├── 📄 Phase6Page.tsx   # Deployment
    │   │   └── 📄 ApprovalsPage.tsx
    │   │
    │   ├── 📂 components/          # Reusable components
    │   │   ├── 📂 AICopilot/       # AI chat component
    │   │   ├── 📂 DocumentUpload/  # File upload
    │   │   ├── 📂 Requirements/    # Gherkin viewer
    │   │   ├── 📂 modals/          # Modal dialogs
    │   │   └── ...
    │   │
    │   ├── 📂 services/            # API integration
    │   │   └── 📄 api.ts           # All API calls
    │   │
    │   ├── 📄 App.tsx              # Main app component
    │   ├── 📄 main.tsx             # Entry point
    │   └── 📄 index.css            # Global styles
    │
    ├── 📂 public/                  # Static assets
    │
    ├── 📄 index.html               # HTML template
    ├── 📄 package.json             # NPM dependencies
    ├── 📄 package-lock.json        # Locked dependencies
    ├── 📄 vite.config.ts           # Vite configuration
    ├── 📄 tsconfig.json            # TypeScript config
    ├── 📄 tsconfig.node.json       # Node TypeScript config
    ├── 📄 tailwind.config.js       # Tailwind CSS config
    └── 📄 postcss.config.js        # PostCSS config
```

## 🎯 Key Files to Configure

### Backend
1. **`backend/.env`** - MUST configure:
   - `OPENAI_API_KEY` - Your OpenAI API key
   - `DATABASE_URL` - Database connection string
   - `SECRET_KEY` - JWT secret (change in production)

2. **`backend/app/main.py`** - Main FastAPI application
3. **`backend/app/services/ai_service.py`** - All AI features

### Frontend
1. **`frontend/src/services/api.ts`** - All API endpoints
2. **`frontend/vite.config.ts`** - Proxy settings for backend

## 🚀 How to Start

### Option 1: Use Batch Scripts (Windows)
1. Double-click `start_backend.bat`
2. Double-click `start_frontend.bat` (in new window)

### Option 2: Manual Commands
See `START_HERE.md` for step-by-step instructions

## 📦 What's NOT Included

To keep the package clean, these are excluded:
- ❌ Documentation files (*.md in docs/)
- ❌ Test scripts
- ❌ Node_modules (install with `npm install`)
- ❌ Python virtual environment (create with `python -m venv venv`)
- ❌ Database files (create on first run)
- ❌ Build artifacts
- ❌ Log files
- ❌ Temporary files

## ✅ What IS Included

Everything needed to run:
- ✅ Complete backend source code
- ✅ Complete frontend source code
- ✅ Configuration files
- ✅ Dependencies lists (requirements.txt, package.json)
- ✅ Startup scripts
- ✅ Documentation (README.md, START_HERE.md)

## 📊 File Count Summary

- **Backend**: ~15-20 Python files
- **Frontend**: ~40-50 TypeScript/React files
- **Config**: ~15 configuration files
- **Docs**: 3 documentation files
- **Scripts**: 2 startup scripts

**Total**: ~70-80 essential files (without node_modules or venv)

## 🎓 Learning Path

1. **Start Here**: `START_HERE.md` - Quick setup
2. **Full Guide**: `README.md` - Complete documentation
3. **Code Structure**: This file - Understand organization
4. **Backend Code**: `backend/app/` - API and AI logic
5. **Frontend Code**: `frontend/src/` - UI components

## 💡 Pro Tips

- Keep `backend/.env` secure (never commit to git!)
- Use `.gitignore` to exclude sensitive files
- Read `README.md` for troubleshooting
- Check `START_HERE.md` for quick start

---

**Ready to start?** → Read `START_HERE.md` next! 🚀

