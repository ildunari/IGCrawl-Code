#!/usr/bin/env python3
"""
Verification script to check if all components are properly installed and configured.
"""
import sys
import subprocess
import importlib
import os
from pathlib import Path

# Ensure project root is on the import path so `backend` can be imported
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def check_python_version():
    """Check Python version is 3.11+"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print("✅ Python 3.11+ detected")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} detected, need 3.11+")
        return False


def check_backend_dependencies():
    """Check if backend dependencies are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'sqlmodel', 'redis', 'rq', 
        'instagrapi', 'cryptography', 'pandas', 'openpyxl'
    ]
    
    missing = []
    for package in required_packages:
        try:
            importlib.import_module(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing backend packages: {', '.join(missing)}")
        return False
    else:
        print("✅ All backend dependencies installed")
        return True


def check_redis_running():
    """Check if Redis is running"""
    try:
        result = subprocess.run(['redis-cli', 'ping'], 
                                capture_output=True, text=True)
        if result.stdout.strip() == 'PONG':
            print("✅ Redis is running")
            return True
        else:
            print("❌ Redis is not responding")
            return False
    except FileNotFoundError:
        print("❌ Redis CLI not found")
        return False
    except Exception as e:
        print(f"❌ Redis check failed: {e}")
        return False


def check_env_file():
    """Check if .env file exists and has required variables"""
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ .env file not found")
        return False
    
    required_vars = [
        'SECRET_KEY', 'DATABASE_URL', 'REDIS_URL',
        'RATE_LIMIT_PER_MINUTE', 'SCRAPE_DELAY_SECONDS'
    ]
    
    with open(env_path) as f:
        env_content = f.read()
        missing = []
        for var in required_vars:
            if f"{var}=" not in env_content:
                missing.append(var)
    
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        return False
    else:
        print("✅ Environment variables configured")
        return True


def check_frontend_dependencies():
    """Check if frontend dependencies are installed"""
    try:
        package_json = Path('frontend/package.json')
        node_modules = Path('frontend/node_modules')
        
        if not package_json.exists():
            print("❌ frontend/package.json not found")
            return False
        
        if not node_modules.exists():
            print("❌ frontend/node_modules not found - run 'npm install'")
            return False
        
        print("✅ Frontend dependencies installed")
        return True
    except Exception as e:
        print(f"❌ Frontend check failed: {e}")
        return False


def check_database():
    """Check if database is accessible"""
    try:
        from backend.app.database import engine
        from sqlmodel import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            if result.fetchone()[0] == 1:
                print("✅ Database connection successful")
                return True
            else:
                print("❌ Database query failed")
                return False
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False


def main():
    """Run all checks"""
    print("🔍 Instagram Intelligence Dashboard - Verification Script\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Backend Dependencies", check_backend_dependencies),
        ("Redis Server", check_redis_running),
        ("Environment Configuration", check_env_file),
        ("Frontend Dependencies", check_frontend_dependencies),
        ("Database Connection", check_database),
    ]
    
    passed = 0
    failed = 0
    
    for name, check_func in checks:
        print(f"\nChecking {name}...")
        if check_func():
            passed += 1
        else:
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n✅ All checks passed! Your installation is ready.")
        print("\nTo start the application:")
        print("1. Start Redis: redis-server")
        print("2. Start Backend: cd backend && uvicorn app.main:app")
        print("3. Start Worker: cd backend && rq worker")
        print("4. Start Frontend: cd frontend && npm run dev")
    else:
        print(f"\n❌ {failed} checks failed. Please fix the issues above.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())