#!/usr/bin/env python3
"""
GitHub Repository Creator for Hackathon Teams

This script connects to a GitHub organization, creates repositories using a template,
and adds team leaders to their respective repositories based on data from an Excel file.
"""

import os
import sys
import time
import logging
import pandas as pd
from github import Github, GithubException
from config import *

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('github_repo_creator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class GitHubRepoCreator:
    def __init__(self):
        """Initialize the GitHub repository creator."""
        if not GITHUB_TOKEN:
            raise ValueError("GitHub token is required. Please set GITHUB_TOKEN environment variable.")
        
        self.github = Github(GITHUB_TOKEN)
        self.org = self.github.get_organization(GITHUB_ORG_NAME)
        self.template_repo = None
        
        # Validate GitHub connection
        try:
            self.github.get_user()
            logger.info(f"Successfully connected to GitHub as {self.github.get_user().login}")
        except GithubException as e:
            logger.error(f"Failed to connect to GitHub: {e}")
            raise
    
    def get_template_repository(self):
        """Get the template repository for creating new repos."""
        try:
            self.template_repo = self.org.get_repo(TEMPLATE_REPO_NAME)
            logger.info(f"Found template repository: {TEMPLATE_REPO_NAME}")
            return True
        except GithubException as e:
            logger.error(f"Template repository '{TEMPLATE_REPO_NAME}' not found: {e}")
            return False
    
    def find_user_by_email(self, email):
        """Find GitHub user by email address."""
        try:
            # Search for users by email
            users = self.github.search_users(f"{email}")
            for user in users:
                # Check if the user's email matches
                if hasattr(user, 'email') and user.email == email:
                    return user
                # Also check if email is in user's public profile
                if hasattr(user, 'public_repos'):
                    return user
            return None
        except GithubException as e:
            logger.warning(f"Error searching for user with email {email}: {e}")
            return None
    
    def create_repository(self, team_name, leader_email):
        """Create a new repository for a team."""
        repo_name = f"{REPO_PREFIX}{team_name.lower().replace(' ', '-')}"
        
        try:
            # Check if repository already exists
            try:
                existing_repo = self.org.get_repo(repo_name)
                logger.warning(f"Repository '{repo_name}' already exists for team '{team_name}'")
                return existing_repo
            except GithubException:
                pass  # Repository doesn't exist, continue with creation
            
            # Create repository from template
            repo = self.org.create_repo_from_template(
                repo_name,
                self.template_repo,
                description=f"{REPO_DESCRIPTION} for team {team_name}",
                private=(REPO_VISIBILITY == 'private')
            )
            
            logger.info(f"Created repository '{repo_name}' for team '{team_name}'")
            return repo
            
        except GithubException as e:
            logger.error(f"Failed to create repository '{repo_name}' for team '{team_name}': {e}")
            return None
    
    def add_user_to_repository(self, repo, leader_email):
        """Add a user to a repository with specified permissions."""
        try:
            # Find user by email
            user = self.find_user_by_email(leader_email)
            if not user:
                logger.warning(f"Could not find GitHub user for email: {leader_email}")
                return False
            
            # Add user to repository
            repo.add_to_collaborators(user.login, DEFAULT_PERMISSION)
            logger.info(f"Added user {user.login} to repository {repo.name} with {DEFAULT_PERMISSION} permission")
            return True
            
        except GithubException as e:
            logger.error(f"Failed to add user {leader_email} to repository {repo.name}: {e}")
            return False
    
    def process_teams_data(self):
        """Process teams data from Excel file and create repositories."""
        try:
            # Read Excel file
            df = pd.read_excel(EXCEL_FILE_PATH)
            logger.info(f"Loaded {len(df)} teams from {EXCEL_FILE_PATH}")
            
            # Validate required columns
            required_columns = [TEAM_NAME_COLUMN, LEADER_EMAIL_COLUMN]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns in Excel file: {missing_columns}")
            
            # Process each team
            successful_creations = 0
            failed_creations = 0
            
            for index, row in df.iterrows():
                team_name = row[TEAM_NAME_COLUMN]
                leader_email = row[LEADER_EMAIL_COLUMN]
                
                logger.info(f"Processing team: {team_name} (Leader: {leader_email})")
                
                # Create repository
                repo = self.create_repository(team_name, leader_email)
                if repo:
                    # Add leader to repository
                    if self.add_user_to_repository(repo, leader_email):
                        successful_creations += 1
                        logger.info(f"Successfully processed team '{team_name}'")
                    else:
                        failed_creations += 1
                        logger.error(f"Failed to add leader to repository for team '{team_name}'")
                else:
                    failed_creations += 1
                    logger.error(f"Failed to create repository for team '{team_name}'")
                
                # Add delay to avoid rate limiting
                time.sleep(1)
            
            logger.info(f"Processing complete. Successful: {successful_creations}, Failed: {failed_creations}")
            return successful_creations, failed_creations
            
        except FileNotFoundError:
            logger.error(f"Excel file not found: {EXCEL_FILE_PATH}")
            return 0, 0
        except Exception as e:
            logger.error(f"Error processing Excel file: {e}")
            return 0, 0
    
    def run(self):
        """Main execution method."""
        logger.info("Starting GitHub repository creation process...")
        
        # Validate template repository
        if not self.get_template_repository():
            logger.error("Cannot proceed without template repository")
            return False
        
        # Process teams data
        successful, failed = self.process_teams_data()
        
        if failed == 0:
            logger.info("All repositories created successfully!")
            return True
        else:
            logger.warning(f"Some repositories failed to create. Check logs for details.")
            return False


def main():
    """Main function to run the repository creation script."""
    try:
        creator = GitHubRepoCreator()
        success = creator.run()
        
        if success:
            print("✅ Repository creation completed successfully!")
            sys.exit(0)
        else:
            print("❌ Some repositories failed to create. Check the logs for details.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 