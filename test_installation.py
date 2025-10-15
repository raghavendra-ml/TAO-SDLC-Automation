"""
Installation Test Script for TAO SDLC AI
Tests all critical components before running the application
"""

import sys
import os
from pathlib import Path

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_success(text):
    print(f"[OK] {text}")

def print_error(text):
    print(f"[FAIL] {text}")

def print_warning(text):
    print(f"[WARNING] {text}")

def test_python_version():
    print_header("Testing Python Version")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 9:
        print_success("Python version is compatible (3.9+)")
        return True
    else:
        print_error("Python 3.9+ required")
        return False

def test_backend_structure():
    print_header("Testing Backend Structure")
    
    backend_files = [
        "backend/app/__init__.py",
        "backend/app/main.py",
        "backend/app/database.py",
        "backend/app/models.py",
        "backend/app/schemas.py",
        "backend/requirements.txt",
        "backend/.env"
    ]
    
    backend_dirs = [
        "backend/app/routers",
        "backend/app/services"
    ]
    
    all_good = True
    
    for file in backend_files:
        if os.path.exists(file):
            print_success(f"Found: {file}")
        else:
            print_error(f"Missing: {file}")
            all_good = False
    
    for dir in backend_dirs:
        if os.path.isdir(dir):
            print_success(f"Found directory: {dir}")
        else:
            print_error(f"Missing directory: {dir}")
            all_good = False
    
    return all_good

def test_frontend_structure():
    print_header("Testing Frontend Structure")
    
    frontend_files = [
        "frontend/package.json",
        "frontend/vite.config.ts",
        "frontend/tsconfig.json",
        "frontend/index.html",
        "frontend/src/main.tsx",
        "frontend/src/App.tsx"
    ]
    
    frontend_dirs = [
        "frontend/src/pages",
        "frontend/src/components",
        "frontend/src/services"
    ]
    
    all_good = True
    
    for file in frontend_files:
        if os.path.exists(file):
            print_success(f"Found: {file}")
        else:
            print_error(f"Missing: {file}")
            all_good = False
    
    for dir in frontend_dirs:
        if os.path.isdir(dir):
            print_success(f"Found directory: {dir}")
        else:
            print_error(f"Missing directory: {dir}")
            all_good = False
    
    return all_good

def test_backend_imports():
    print_header("Testing Backend Imports")
    
    try:
        sys.path.insert(0, 'backend')
        from app import models, main, database
        print_success("All backend imports successful!")
        return True
    except Exception as e:
        print_error(f"Import failed: {str(e)}")
        return False

def test_env_configuration():
    print_header("Testing Environment Configuration")
    
    if not os.path.exists("backend/.env"):
        print_error("backend/.env file not found!")
        print_warning("You need to create backend/.env with your OpenAI API key")
        return False
    
    with open("backend/.env", "r") as f:
        content = f.read()
        
        if "OPENAI_API_KEY" in content:
            if "your-openai-api-key" in content or "sk-proj-" not in content:
                print_warning("OPENAI_API_KEY found but not configured")
                print_warning("Please update backend/.env with your actual API key")
            else:
                print_success("OPENAI_API_KEY is configured")
        else:
            print_error("OPENAI_API_KEY not found in .env")
            return False
        
        if "DATABASE_URL" in content:
            print_success("DATABASE_URL is configured")
        else:
            print_warning("DATABASE_URL not found in .env")
    
    return True

def test_routers():
    print_header("Testing API Routers")
    
    router_files = [
        "backend/app/routers/auth.py",
        "backend/app/routers/projects.py",
        "backend/app/routers/phases.py",
        "backend/app/routers/ai_copilot.py",
        "backend/app/routers/approvals.py"
    ]
    
    all_good = True
    
    for router in router_files:
        if os.path.exists(router):
            print_success(f"Found: {os.path.basename(router)}")
        else:
            print_error(f"Missing: {router}")
            all_good = False
    
    return all_good

def test_services():
    print_header("Testing Services")
    
    service_files = [
        "backend/app/services/ai_service.py",
        "backend/app/services/document_parser.py"
    ]
    
    all_good = True
    
    for service in service_files:
        if os.path.exists(service):
            print_success(f"Found: {os.path.basename(service)}")
        else:
            print_error(f"Missing: {service}")
            all_good = False
    
    return all_good

def test_frontend_pages():
    print_header("Testing Frontend Pages")
    
    page_files = [
        "frontend/src/pages/LoginPage.tsx",
        "frontend/src/pages/DashboardPage.tsx",
        "frontend/src/pages/ProjectsPage.tsx",
        "frontend/src/pages/Phase1Page.tsx",
        "frontend/src/pages/Phase2Page.tsx"
    ]
    
    all_good = True
    found = 0
    
    for page in page_files:
        if os.path.exists(page):
            found += 1
    
    print_success(f"Found {found} page files")
    
    if found < 3:
        print_error("Critical pages missing!")
        return False
    
    return True

def test_documentation():
    print_header("Testing Documentation")
    
    doc_files = [
        "README.md",
        "START_HERE.md",
        "FOLDER_STRUCTURE.md"
    ]
    
    all_good = True
    
    for doc in doc_files:
        if os.path.exists(doc):
            print_success(f"Found: {doc}")
        else:
            print_error(f"Missing: {doc}")
            all_good = False
    
    return all_good

def main():
    print("\n")
    print("="*60)
    print("      TAO SDLC AI - Installation Test Suite")
    print("                 Version 1.0")
    print("="*60)
    
    results = {
        "Python Version": test_python_version(),
        "Backend Structure": test_backend_structure(),
        "Frontend Structure": test_frontend_structure(),
        "Backend Imports": test_backend_imports(),
        "Environment Config": test_env_configuration(),
        "API Routers": test_routers(),
        "Services": test_services(),
        "Frontend Pages": test_frontend_pages(),
        "Documentation": test_documentation()
    }
    
    print_header("Test Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}\n")
    
    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {test_name}")
    
    print("\n" + "="*60)
    
    if passed == total:
        print("\n[SUCCESS] All tests passed! Your installation is ready.")
        print("\nNext steps:")
        print("1. Configure backend/.env with your OpenAI API key")
        print("2. Run: start_backend.bat")
        print("3. Run: start_frontend.bat")
        print("4. Open: http://localhost:5173")
        return True
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed. Please review the errors above.")
        print("\nCheck:")
        print("- All files were copied correctly")
        print("- Python 3.9+ is installed")
        print("- All directories are in place")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] Test suite error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

