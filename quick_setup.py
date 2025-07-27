#!/usr/bin/env python3
"""
Quick Hackathon Setup Script

This script creates repositories and adds users using GitHub usernames.
Simple and reliable approach.
"""

import os
import sys
import time
import logging
import pandas as pd
import subprocess
from github import Github, GithubException
from config import *

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quick_setup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class QuickHackathonSetup:
    def __init__(self):
        """Initialize the quick setup."""
        if not GITHUB_TOKEN:
            raise ValueError("GitHub token is required. Please set GITHUB_TOKEN environment variable.")
        
        self.github = Github(GITHUB_TOKEN)
        self.org = self.github.get_organization(GITHUB_ORG_NAME)
        self.template_repo = None
        
        # Configure Git user for this script
        self.configure_git_user()
        
        # Validate GitHub connection
        try:
            self.github.get_user()
            logger.info(f"Successfully connected to GitHub as {self.github.get_user().login}")
        except GithubException as e:
            logger.error(f"Failed to connect to GitHub: {e}")
            raise
    
    def configure_git_user(self):
        """Configure Git user for commits made by this script."""
        try:
            script_user_name = os.getenv('SCRIPT_GIT_USER_NAME', 'Hackathon Organizer')
            script_user_email = os.getenv('SCRIPT_GIT_USER_EMAIL', 'organizer@hackathon.com')
            
            subprocess.run(['git', 'config', '--global', 'user.name', script_user_name], 
                         capture_output=True, check=False)
            subprocess.run(['git', 'config', '--global', 'user.email', script_user_email], 
                         capture_output=True, check=False)
            
            logger.info(f"Configured Git user: {script_user_name} <{script_user_email}>")
        except Exception as e:
            logger.warning(f"Could not configure Git user: {e}")
    
    def get_template_repository(self):
        """Get the template repository for creating new repos."""
        try:
            self.template_repo = self.org.get_repo(TEMPLATE_REPO_NAME)
            logger.info(f"Found template repository: {TEMPLATE_REPO_NAME}")
            return True
        except GithubException as e:
            logger.error(f"Template repository '{TEMPLATE_REPO_NAME}' not found: {e}")
            return False
    
    def create_repository(self, team_name, leader_username):
        """Create a new repository for a team."""
        repo_name = f"{REPO_PREFIX}{team_name.lower().replace(' ', '-')}"
        
        logger.info(f"Creating repository '{repo_name}' for team '{team_name}'")
        
        try:
            # Check if repository already exists
            try:
                existing_repo = self.org.get_repo(repo_name)
                logger.warning(f"Repository '{repo_name}' already exists for team '{team_name}'")
                return existing_repo
            except GithubException:
                pass  # Repository doesn't exist, continue with creation
            
            # Create repository from template
            try:
                repo = self.org.create_repo_from_template(
                    repo_name,
                    self.template_repo,
                    description=f"{REPO_DESCRIPTION} for team {team_name}",
                    private=(REPO_VISIBILITY == 'private')
                )
                logger.info(f"Created repository '{repo_name}' from template for team '{team_name}'")
            except GithubException as template_error:
                logger.warning(f"Template creation failed: {template_error}")
                logger.info(f"Falling back to creating empty repository for team '{team_name}'")
                
                # Fallback: create empty repository
                repo = self.org.create_repo(
                    repo_name,
                    description=f"{REPO_DESCRIPTION} for team {team_name}",
                    private=(REPO_VISIBILITY == 'private'),
                    auto_init=True
                )
                logger.info(f"Created empty repository '{repo_name}' for team '{team_name}'")
            
            return repo
            
        except GithubException as e:
            logger.error(f"Failed to create repository '{repo_name}' for team '{team_name}': {e}")
            return None
    
    def add_user_to_organization(self, username, role="member"):
        """Add a user to the organization by username."""
        try:
            # Get user by username
            user = self.github.get_user(username)
            
            # Try to invite user to organization (will fail if already a member)
            try:
                self.org.invite_user(user=user, role=role)
                logger.info(f"Invited user {user.login} to organization with role: {role}")
                return True
            except GithubException as e:
                if "already a member" in str(e) or "already exists" in str(e):
                    logger.info(f"User {user.login} is already a member of the organization")
                    return True
                else:
                    logger.error(f"Failed to invite user {username} to organization: {e}")
                    return False
            except Exception as e:
                logger.warning(f"Unexpected error inviting user {username} to organization: {e}")
                return False
            
        except GithubException as e:
            logger.error(f"Failed to get user {username}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error with user {username}: {e}")
            return False
    
    def add_user_to_repository(self, repo, leader_username):
        """Add a user to a repository with specified permissions."""
        try:
            # Get user by username
            user = self.github.get_user(leader_username)
            
            # Add user to repository
            repo.add_to_collaborators(user.login, DEFAULT_PERMISSION)
            logger.info(f"Added user {user.login} to repository {repo.name} with {DEFAULT_PERMISSION} permission")
            return True
            
        except GithubException as e:
            logger.error(f"Failed to add user {leader_username} to repository {repo.name}: {e}")
            return False
    
    def process_teams_data(self):
        """Process teams data from Excel file and create repositories."""
        try:
            # Read Excel file
            df = pd.read_excel(EXCEL_FILE_PATH)
            logger.info(f"Loaded {len(df)} teams from {EXCEL_FILE_PATH}")
            
            # Check if we have usernames or need to use emails as usernames
            if 'leader_username' in df.columns:
                username_column = 'leader_username'
            else:
                username_column = LEADER_EMAIL_COLUMN
                logger.info("No 'leader_username' column found, using email column as usernames")
            
            # Validate required columns
            required_columns = [TEAM_NAME_COLUMN, username_column]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns in Excel file: {missing_columns}")
            
            # Process each team
            successful_setups = 0
            failed_setups = 0
            
            for index, row in df.iterrows():
                try:
                    team_name = row[TEAM_NAME_COLUMN]
                    leader_username = row[username_column]
                    
                    logger.info(f"Processing team: {team_name} (Leader: {leader_username})")
                    
                    # Step 1: Add user to organization
                    logger.info(f"Adding {leader_username} to organization...")
                    org_success = self.add_user_to_organization(leader_username)
                    if org_success:
                        logger.info(f"Successfully added {leader_username} to organization")
                    else:
                        logger.warning(f"Failed to add {leader_username} to organization, continuing...")
                    
                    # Step 2: Create repository
                    repo = self.create_repository(team_name, leader_username)
                    if repo:
                        # Step 3: Add leader to repository
                        if self.add_user_to_repository(repo, leader_username):
                            successful_setups += 1
                            logger.info(f"Successfully processed team '{team_name}'")
                        else:
                            failed_setups += 1
                            logger.warning(f"Repository created but failed to add leader for team '{team_name}'")
                    else:
                        failed_setups += 1
                        logger.error(f"Failed to create repository for team '{team_name}'")
                    
                    # Add delay to avoid rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error processing team {team_name if 'team_name' in locals() else 'unknown'}: {e}")
                    failed_setups += 1
                    continue
            
            logger.info(f"Processing complete. Successful: {successful_setups}, Failed: {failed_setups}")
            return successful_setups, failed_setups
            
        except FileNotFoundError:
            logger.error(f"Excel file not found: {EXCEL_FILE_PATH}")
            return 0, 0
        except Exception as e:
            logger.error(f"Error processing Excel file: {e}")
            return 0, 0
    
    def run(self):
        """Main execution method."""
        logger.info("Starting Quick Hackathon Setup Process...")
        
        # Validate template repository
        if not self.get_template_repository():
            logger.error("Cannot proceed without template repository")
            return False
        
        # Process teams data
        successful, failed = self.process_teams_data()
        
        logger.info(f"Final Results: {successful} successful, {failed} failed")
        
        if successful > 0:
            logger.info(f"Successfully processed {successful} teams!")
            return True
        else:
            logger.error("No teams were processed successfully!")
            return False


def main():
    """Main function to run the quick setup script."""
    try:
        setup = QuickHackathonSetup()
        success = setup.run()
        
        if success:
            print("✅ Quick setup completed successfully!")
            print("🎉 Repositories created and users added!")
            sys.exit(0)
        else:
            print("❌ Setup failed. Check the logs for details.")
            print("📋 Try using GitHub usernames in your Excel file.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 