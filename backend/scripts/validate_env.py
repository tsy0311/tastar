#!/usr/bin/env python3
"""
Environment variable validation script
Validates that all required environment variables are set correctly
"""
import sys
import os
from pathlib import Path
from typing import List, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from app.core.config import settings
except ImportError:
    print("❌ Failed to import settings. Make sure you're in the backend directory.")
    sys.exit(1)

def validate_env() -> Tuple[bool, List[str]]:
    """Validate environment variables"""
    errors = []
    warnings = []
    
    # Critical settings
    if settings.JWT_SECRET == "your-super-secret-jwt-key-change-in-production":
        warnings.append("JWT_SECRET is using default value (change in production!)")
    
    if settings.SECRET_KEY == "your-secret-key-change-in-production":
        warnings.append("SECRET_KEY is using default value (change in production!)")
    
    # Database
    if not settings.DATABASE_URL:
        errors.append("DATABASE_URL is not set")
    elif "postgresql://" not in settings.DATABASE_URL:
        warnings.append("DATABASE_URL format may be incorrect")
    
    # Redis (optional but recommended)
    if not settings.REDIS_URL:
        warnings.append("REDIS_URL is not set (Redis is optional)")
    
    # AI Services (optional)
    if not settings.OPENAI_API_KEY and not settings.ANTHROPIC_API_KEY:
        warnings.append("No AI API keys set (AI features will be limited)")
    
    # Email (optional)
    if not settings.SENDGRID_API_KEY and not settings.SMTP_HOST:
        warnings.append("No email configuration (email features will be disabled)")
    
    # File Storage
    if settings.STORAGE_TYPE == "s3":
        if not settings.AWS_S3_BUCKET:
            errors.append("AWS_S3_BUCKET is required when STORAGE_TYPE=s3")
        if not settings.AWS_ACCESS_KEY_ID:
            errors.append("AWS_ACCESS_KEY_ID is required when STORAGE_TYPE=s3")
        if not settings.AWS_SECRET_ACCESS_KEY:
            errors.append("AWS_SECRET_ACCESS_KEY is required when STORAGE_TYPE=s3")
    
    return len(errors) == 0, errors, warnings

def main():
    """Main validation function"""
    print("🔍 Validating Environment Variables\n")
    print("=" * 60)
    
    valid, errors, warnings = validate_env()
    
    if errors:
        print("\n❌ Errors found:")
        for error in errors:
            print(f"   • {error}")
    
    if warnings:
        print("\n⚠️  Warnings:")
        for warning in warnings:
            print(f"   • {warning}")
    
    if not errors and not warnings:
        print("\n✅ All environment variables are valid!")
    
    print("\n" + "=" * 60)
    print("\n📋 Current Configuration:")
    print(f"   DEBUG: {settings.DEBUG}")
    print(f"   DATABASE_URL: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}")
    print(f"   REDIS_URL: {settings.REDIS_URL}")
    print(f"   STORAGE_TYPE: {settings.STORAGE_TYPE}")
    print(f"   LOG_LEVEL: {settings.LOG_LEVEL}")
    
    if errors:
        print("\n❌ Please fix the errors above before running the application.")
        return 1
    
    if warnings:
        print("\n⚠️  Review the warnings above. The application will run but some features may be limited.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

