#!/usr/bin/env python3
"""
Generate secure production secrets
"""

import secrets
import string
import os
from datetime import datetime

def generate_secret(length: int = 64) -> str:
    """Generate cryptographically secure secret"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_jwt_secret() -> str:
    """Generate JWT secret key"""
    return secrets.token_urlsafe(64)

def generate_db_password() -> str:
    """Generate strong database password"""
    return secrets.token_urlsafe(32) + string.digits

def main():
    """Generate all production secrets"""
    print("🔐 Generating Production Secrets")
    print("=" * 50)
    
    # Generate secrets
    jwt_secret = generate_jwt_secret()
    db_password = generate_db_password()
    github_webhook_secret = generate_secret(40)
    
    # Current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"Generated at: {timestamp}")
    print()
    print("🔑 Production Secrets:")
    print(f"SECRET_KEY={jwt_secret}")
    print(f"DATABASE_PASSWORD={db_password}")
    print()
    print("🌐 Service Configuration:")
    print(f"GITHUB_CLIENT_ID=your-github-client-id")
    print(f"GITHUB_CLIENT_SECRET=your-github-client-secret")
    print(f"BASE_URL=https://your-domain.com")
    print(f"DASHBOARD_URL=https://your-domain.com")
    print()
    print("⚠️  IMPORTANT SECURITY NOTES:")
    print("1. Store these secrets in a secure password manager")
    print("2. Never commit secrets to version control")
    print("3. Use environment-specific .env files")
    print("4. Rotate secrets regularly (every 90 days)")
    print("5. Use different secrets for staging/production")
    print()
    print("📝 To update .env.production:")
    print("cp .env.production .env")
    print("# Then update with your actual values above")

if __name__ == "__main__":
    main()
