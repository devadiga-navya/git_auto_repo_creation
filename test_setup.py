#!/usr/bin/env python3
"""
Test script to verify the setup before running the main repository creation script.
"""

import os
import sys
import pandas as pd
from github import Github, GithubException
from config import *

def test_environment():
    """Test environment variables and configuration."""
    print("🔧 Testing Environment Configuration...")
    
    # Check required environment variables
    required_vars = ['GITHUB_TOKEN', 'GITHUB_ORG_NAME']
    missing_vars = []
    
    for var in required_vars:
        if not getattr(sys.modules[__name__], var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        return False
    
    print("✅ Environment variables configured")
    return True

def test_github_connection():
    """Test GitHub API connection."""
    print("\n🔗 Testing GitHub Connection...")
    
    try:
        github = Github(GITHUB_TOKEN)
        user = github.get_user()
        print(f"✅ Connected to GitHub as: {user.login}")
        
        # Test organization access
        org = github.get_organization(GITHUB_ORG_NAME)
        print(f"✅ Organization access confirmed: {GITHUB_ORG_NAME}")
        
        return True
    except GithubException as e:
        print(f"❌ GitHub connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_template_repository():
    """Test if template repository exists."""
    print(f"\n📁 Testing Template Repository: {TEMPLATE_REPO_NAME}")
    
    try:
        github = Github(GITHUB_TOKEN)
        org = github.get_organization(GITHUB_ORG_NAME)
        template_repo = org.get_repo(TEMPLATE_REPO_NAME)
        
        if template_repo.template:
            print(f"✅ Template repository found and is marked as template")
        else:
            print(f"⚠️  Repository found but not marked as template")
        
        return True
    except GithubException as e:
        print(f"❌ Template repository not found: {e}")
        return False

def test_excel_file():
    """Test if Excel file exists and has correct structure."""
    print(f"\n📊 Testing Excel File: {EXCEL_FILE_PATH}")
    
    try:
        # Check if file exists
        if not os.path.exists(EXCEL_FILE_PATH):
            print(f"❌ Excel file not found: {EXCEL_FILE_PATH}")
            return False
        
        # Read Excel file
        df = pd.read_excel(EXCEL_FILE_PATH)
        print(f"✅ Excel file loaded successfully")
        print(f"📈 Found {len(df)} rows of data")
        
        # Check required columns
        required_columns = [TEAM_NAME_COLUMN, LEADER_EMAIL_COLUMN]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ Missing required columns: {missing_columns}")
            print(f"Available columns: {list(df.columns)}")
            return False
        
        print(f"✅ Required columns found: {required_columns}")
        
        # Show sample data
        print("\n📋 Sample data:")
        print(df.head().to_string(index=False))
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return False

def test_user_search():
    """Test GitHub user search functionality."""
    print(f"\n👤 Testing User Search...")
    
    try:
        github = Github(GITHUB_TOKEN)
        
        # Test with a sample email
        test_email = "test@example.com"
        users = github.search_users(f"{test_email}")
        
        print(f"✅ User search functionality working")
        return True
        
    except Exception as e:
        print(f"❌ User search failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Running Setup Tests...\n")
    
    tests = [
        test_environment,
        test_github_connection,
        test_template_repository,
        test_excel_file,
        test_user_search
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! You're ready to run the main script.")
        print("💡 Run: python github_repo_creator.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues before running the main script.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 