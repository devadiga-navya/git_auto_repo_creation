import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# GitHub Configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_ORG_NAME = os.getenv('GITHUB_ORG_NAME', 'your-organization-name')
TEMPLATE_REPO_NAME = os.getenv('TEMPLATE_REPO_NAME', 'hackathon_template')

# Excel Configuration
EXCEL_FILE_PATH = os.getenv('EXCEL_FILE_PATH', 'teams_data.xlsx')
TEAM_NAME_COLUMN = os.getenv('TEAM_NAME_COLUMN', 'team_name')
LEADER_EMAIL_COLUMN = os.getenv('LEADER_EMAIL_COLUMN', 'leader_email')

# Repository Configuration
REPO_PREFIX = os.getenv('REPO_PREFIX', 'hackathon-')
REPO_DESCRIPTION = os.getenv('REPO_DESCRIPTION', 'Hackathon project repository')
REPO_VISIBILITY = os.getenv('REPO_VISIBILITY', 'private')  # 'private' or 'public'

# User Permission Configuration
DEFAULT_PERMISSION = os.getenv('DEFAULT_PERMISSION', 'push')  # 'pull', 'push', 'admin', 'maintain', 'triage'

# Git Configuration (for commit authorship)
SCRIPT_GIT_USER_NAME = os.getenv('SCRIPT_GIT_USER_NAME', 'Hackathon Organizer')
SCRIPT_GIT_USER_EMAIL = os.getenv('SCRIPT_GIT_USER_EMAIL', 'organizer@hackathon.com')

# Error Handling
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
RETRY_DELAY = int(os.getenv('RETRY_DELAY', '5'))  # seconds 