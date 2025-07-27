#!/usr/bin/env python3
"""
Repository Deletion Script

This script deletes repositories created by quick_setup.py.
⚠️  WARNING: This is an IRREVERSIBLE operation!
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
        logging.FileHandler('delete_repositories.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class RepositoryDeleter:
    def __init__(self):
        """Initialize the repository deleter."""
        if not GITHUB_TOKEN:
            raise ValueError("GitHub token is required. Please set GITHUB_TOKEN environment variable.")
        
        self.github = Github(GITHUB_TOKEN)
        self.org = self.github.get_organization(GITHUB_ORG_NAME)
        
        # Validate GitHub connection
        try:
            self.github.get_user()
            logger.info(f"Successfully connected to GitHub as {self.github.get_user().login}")
        except GithubException as e:
            logger.error(f"Failed to connect to GitHub: {e}")
            raise
    
    def get_repositories_by_prefix(self, prefix):
        """Get all repositories with a specific prefix."""
        try:
            repos = []
            for repo in self.org.get_repos():
                if repo.name.startswith(prefix):
                    repos.append(repo)
            return repos
        except Exception as e:
            logger.error(f"Error getting repositories with prefix '{prefix}': {e}")
            return []
    
    def get_repositories_from_excel(self):
        """Get repository names from the Excel file used for creation."""
        try:
            df = pd.read_excel(EXCEL_FILE_PATH)
            logger.info(f"Loaded {len(df)} teams from {EXCEL_FILE_PATH}")
            
            repos = []
            for index, row in df.iterrows():
                team_name = row[TEAM_NAME_COLUMN]
                repo_name = f"{REPO_PREFIX}{team_name.lower().replace(' ', '-')}"
                # Skip the template repository
                if repo_name != "hackathon_template":
                    repos.append(repo_name)
                else:
                    logger.info(f"Skipping template repository: {repo_name}")
            
            return repos
        except Exception as e:
            logger.error(f"Error reading Excel file: {e}")
            return []
    
    def delete_repository(self, repo_name, force=False):
        """Delete a specific repository."""
        try:
            repo = self.org.get_repo(repo_name)
            
            if not force:
                # Double-check with user
                confirm = input(f"⚠️  Are you sure you want to DELETE '{repo_name}'? (type 'yes' to confirm): ")
                if confirm.lower() != 'yes':
                    logger.info(f"Deletion of '{repo_name}' cancelled by user")
                    return False
            
            # Delete the repository
            repo.delete()
            logger.info(f"Successfully deleted repository '{repo_name}'")
            return True
            
        except GithubException as e:
            if "Not Found" in str(e):
                logger.warning(f"Repository '{repo_name}' not found")
                return False
            else:
                logger.error(f"Failed to delete repository '{repo_name}': {e}")
                return False
    
    def delete_repositories_by_prefix(self, prefix, force=False):
        """Delete all repositories with a specific prefix."""
        logger.info(f"Deleting repositories with prefix '{prefix}'")
        
        repos = self.get_repositories_by_prefix(prefix)
        if not repos:
            logger.warning(f"No repositories found with prefix '{prefix}'")
            return 0, 0
        
        # Show what will be deleted
        logger.info(f"Found {len(repos)} repositories to delete:")
        for repo in repos:
            if repo.name == "hackathon_template":
                logger.info(f"  - {repo.name} (SKIPPED - template repository)")
            else:
                logger.info(f"  - {repo.name}")
        
        if not force:
            confirm = input(f"⚠️  Are you sure you want to DELETE {len(repos)} repositories? (type 'yes' to confirm): ")
            if confirm.lower() != 'yes':
                logger.info("Deletion cancelled by user")
                return 0, 0
        
        successful = 0
        failed = 0
        
        for repo in repos:
            # Skip the template repository
            if repo.name == "hackathon_template":
                logger.info(f"Skipping template repository: {repo.name}")
                continue
                
            try:
                repo.delete()
                logger.info(f"Successfully deleted repository '{repo.name}'")
                successful += 1
            except Exception as e:
                logger.error(f"Failed to delete repository '{repo.name}': {e}")
                failed += 1
            
            # Add delay to avoid rate limiting
            time.sleep(1)
        
        return successful, failed
    
    def delete_repositories_from_excel(self, force=False):
        """Delete repositories based on the Excel file used for creation."""
        logger.info("Deleting repositories based on Excel file")
        
        repo_names = self.get_repositories_from_excel()
        if not repo_names:
            logger.error("No repository names found in Excel file")
            return 0, 0
        
        # Show what will be deleted
        logger.info(f"Found {len(repo_names)} repositories to delete:")
        for repo_name in repo_names:
            logger.info(f"  - {repo_name}")
        
        if not force:
            confirm = input(f"⚠️  Are you sure you want to DELETE {len(repo_names)} repositories? (type 'yes' to confirm): ")
            if confirm.lower() != 'yes':
                logger.info("Deletion cancelled by user")
                return 0, 0
        
        successful = 0
        failed = 0
        
        for repo_name in repo_names:
            if self.delete_repository(repo_name, force=True):  # Force since already confirmed
                successful += 1
            else:
                failed += 1
            
            # Add delay to avoid rate limiting
            time.sleep(1)
        
        return successful, failed
    
    def list_repositories(self, prefix=None):
        """List repositories that can be deleted."""
        try:
            if prefix:
                repos = self.get_repositories_by_prefix(prefix)
                logger.info(f"Repositories with prefix '{prefix}':")
            else:
                repos = list(self.org.get_repos())
                logger.info("All repositories in organization:")
            
            for repo in repos:
                status = "TEMPLATE" if repo.name == "hackathon_template" else "DELETABLE"
                logger.info(f"  - {repo.name} ({status})")
            
            return len(repos)
            
        except Exception as e:
            logger.error(f"Error listing repositories: {e}")
            return 0
    
    def run(self, mode="excel", prefix=None, specific_repos=None, force=False):
        """Main execution method."""
        logger.info("Starting Repository Deletion Process...")
        logger.warning("⚠️  WARNING: This will PERMANENTLY DELETE repositories!")
        
        if mode == "excel":
            successful, failed = self.delete_repositories_from_excel(force)
        elif mode == "prefix":
            if not prefix:
                prefix = REPO_PREFIX
            successful, failed = self.delete_repositories_by_prefix(prefix, force)
        elif mode == "specific":
            if not specific_repos:
                logger.error("No specific repositories provided")
                return False
            successful = 0
            failed = 0
            for repo_name in specific_repos:
                # Skip the template repository
                if repo_name == "hackathon_template":
                    logger.info(f"Skipping template repository: {repo_name}")
                    continue
                if self.delete_repository(repo_name, force):
                    successful += 1
                else:
                    failed += 1
        elif mode == "list":
            count = self.list_repositories(prefix)
            logger.info(f"Found {count} repositories")
            return True
        else:
            logger.error(f"Unknown mode: {mode}")
            return False
        
        logger.info(f"Deletion complete. Successful: {successful}, Failed: {failed}")
        
        if successful > 0:
            logger.info(f"Successfully deleted {successful} repositories!")
            return True
        else:
            logger.error("No repositories were deleted successfully!")
            return False


def main():
    """Main function to run the repository deleter."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Delete GitHub repositories (IRREVERSIBLE!)")
    parser.add_argument("--mode", choices=["excel", "prefix", "specific", "list"], 
                       default="excel", help="Deletion mode")
    parser.add_argument("--prefix", help="Repository prefix to delete")
    parser.add_argument("--repos", nargs="+", help="Specific repository names to delete")
    parser.add_argument("--list-only", action="store_true", help="Only list repositories, don't delete")
    parser.add_argument("--force", action="store_true", help="Skip confirmation prompts (DANGEROUS!)")
    
    args = parser.parse_args()
    
    try:
        deleter = RepositoryDeleter()
        
        if args.list_only:
            success = deleter.run("list", args.prefix)
        else:
            success = deleter.run(args.mode, args.prefix, args.repos, args.force)
        
        if success:
            print("✅ Repository deletion completed successfully!")
            sys.exit(0)
        else:
            print("❌ Repository deletion failed. Check the logs for details.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 