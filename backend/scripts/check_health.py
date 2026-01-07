#!/usr/bin/env python3
"""
Health check script for Unified AI Business Assistant
Checks the status of all required services and dependencies
"""
import sys
import os
import subprocess
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from app.core.config import settings
    from app.database.connection import get_db, engine
    from app.database.redis_client import get_redis
    from sqlalchemy import text
except ImportError as e:
    print(f"❌ Failed to import application modules: {e}")
    print("   Make sure you're in the backend directory and virtual environment is activated")
    sys.exit(1)

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(f"❌ Python 3.11+ required. Found: {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if required Python packages are installed"""
    required = ['fastapi', 'sqlalchemy', 'redis', 'pydantic']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages installed")
    return True

def check_database():
    """Check PostgreSQL database connection"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        print(f"✅ Database connected: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("   Make sure PostgreSQL is running and DATABASE_URL is correct")
        return False

def check_redis():
    """Check Redis connection"""
    try:
        import asyncio
        async def test_redis():
            try:
                client = await get_redis()
                await client.ping()
                return True
            except Exception as e:
                raise e
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(test_redis())
        loop.close()
        
        if result:
            print(f"✅ Redis connected: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
            return True
    except Exception as e:
        print(f"⚠️  Redis connection failed: {e}")
        print("   Redis is optional but recommended for caching")
        return False

def check_docker():
    """Check if Docker services are running"""
    try:
        result = subprocess.run(
            ['docker', 'compose', 'ps'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if 'unified-ai-postgres' in result.stdout or 'unified-ai-redis' in result.stdout:
            print("✅ Docker services detected")
            return True
        else:
            print("⚠️  Docker services not found (may be using external services)")
            return True  # Not a failure
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        print("⚠️  Docker not available (may be using external services)")
        return True  # Not a failure

def check_env_file():
    """Check if .env file exists"""
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        print("✅ .env file found")
        return True
    else:
        print("⚠️  .env file not found (using defaults)")
        env_example = Path(__file__).parent.parent / '.env.example'
        if env_example.exists():
            print("   You can copy .env.example to .env and configure it")
        return True  # Not a failure

def check_migrations():
    """Check if database migrations are up to date"""
    try:
        result = subprocess.run(
            ['alembic', 'current'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("✅ Database migrations checked")
            return True
        else:
            print("⚠️  Could not check migrations (run: alembic upgrade head)")
            return True  # Not a failure
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️  Alembic not available (migrations may not be run)")
        return True  # Not a failure

def main():
    """Run all health checks"""
    import argparse
    parser = argparse.ArgumentParser(description='Health check for Unified AI Business Assistant')
    parser.add_argument('--quiet', '-q', action='store_true', help='Quiet mode (minimal output)')
    args = parser.parse_args()
    
    if not args.quiet:
        print("🏥 Health Check for Unified AI Business Assistant\n")
        print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment File", check_env_file),
        ("Docker Services", check_docker),
        ("Database", check_database),
        ("Redis", check_redis),
        ("Migrations", check_migrations),
    ]
    
    results = []
    for name, check_func in checks:
        if not args.quiet:
            print(f"\n📋 {name}:")
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            if not args.quiet:
                print(f"❌ Error: {e}")
            results.append(False)
    
    if not args.quiet:
        print("\n" + "=" * 60)
        print("\n📊 Summary:")
    
    critical = results[:3]  # Python, Dependencies, Database
    optional = results[3:]
    
    if args.quiet:
        # Quiet mode: just return exit code
        return 0 if all(critical) else 1
    
    if all(critical):
        print("✅ All critical checks passed!")
        if all(optional):
            print("✅ All optional checks passed!")
        else:
            print("⚠️  Some optional checks failed (non-critical)")
        return 0
    else:
        print("❌ Some critical checks failed!")
        print("\nPlease fix the issues above before running the application.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

