#!/usr/bin/env python3
"""
Repository Archiver Script

This script archives repositories created by quick_setup.py.
It can archive repositories by:
1. Reading from the same Excel file used for creation
2. Archiving all repositories with a specific prefix
3. Archiving specific repositories by name
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
        logging.FileHandler('archive_repositories.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class RepositoryArchiver:
    def __init__(self):
        """Initialize the repository archiver."""
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
    
    def archive_repository(self, repo_name):
        """Archive a specific repository."""
        try:
            repo = self.org.get_repo(repo_name)
            
            if repo.archived:
                logger.info(f"Repository '{repo_name}' is already archived")
                return True
            
            # Archive the repository using the correct API method
            repo.edit(archived=True)
            logger.info(f"Successfully archived repository '{repo_name}'")
            return True
            
        except GithubException as e:
            if "Not Found" in str(e):
                logger.warning(f"Repository '{repo_name}' not found")
                return False
            else:
                logger.error(f"Failed to archive repository '{repo_name}': {e}")
                return False
    
    def unarchive_repository(self, repo_name):
        """Unarchive a specific repository."""
        try:
            repo = self.org.get_repo(repo_name)
            
            if not repo.archived:
                logger.info(f"Repository '{repo_name}' is not archived")
                return True
            
            # Unarchive the repository using the correct API method
            repo.edit(archived=False)
            logger.info(f"Successfully unarchived repository '{repo_name}'")
            return True
            
        except GithubException as e:
            if "Not Found" in str(e):
                logger.warning(f"Repository '{repo_name}' not found")
                return False
            else:
                logger.error(f"Failed to unarchive repository '{repo_name}': {e}")
                return False
    
    def archive_repositories_by_prefix(self, prefix):
        """Archive all repositories with a specific prefix."""
        logger.info(f"Archiving repositories with prefix '{prefix}'")
        
        repos = self.get_repositories_by_prefix(prefix)
        if not repos:
            logger.warning(f"No repositories found with prefix '{prefix}'")
            return 0, 0
        
        successful = 0
        failed = 0
        
        for repo in repos:
            # Skip the template repository
            if repo.name == "hackathon_template":
                logger.info(f"Skipping template repository: {repo.name}")
                continue
                
            try:
                if repo.archived:
                    logger.info(f"Repository '{repo.name}' is already archived")
                    successful += 1
                else:
                    repo.edit(archived=True)
                    logger.info(f"Successfully archived repository '{repo.name}'")
                    successful += 1
            except Exception as e:
                logger.error(f"Failed to archive repository '{repo.name}': {e}")
                failed += 1
            
            # Add delay to avoid rate limiting
            time.sleep(1)
        
        return successful, failed
    
    def archive_repositories_from_excel(self):
        """Archive repositories based on the Excel file used for creation."""
        logger.info("Archiving repositories based on Excel file")
        
        repo_names = self.get_repositories_from_excel()
        if not repo_names:
            logger.error("No repository names found in Excel file")
            return 0, 0
        
        successful = 0
        failed = 0
        
        for repo_name in repo_names:
            if self.archive_repository(repo_name):
                successful += 1
            else:
                failed += 1
            
            # Add delay to avoid rate limiting
            time.sleep(1)
        
        return successful, failed
    
    def list_repositories(self, prefix=None):
        """List repositories that can be archived."""
        try:
            if prefix:
                repos = self.get_repositories_by_prefix(prefix)
                logger.info(f"Repositories with prefix '{prefix}':")
            else:
                repos = list(self.org.get_repos())
                logger.info("All repositories in organization:")
            
            for repo in repos:
                status = "ARCHIVED" if repo.archived else "ACTIVE"
                logger.info(f"  - {repo.name} ({status})")
            
            return len(repos)
            
        except Exception as e:
            logger.error(f"Error listing repositories: {e}")
            return 0
    
    def run(self, mode="excel", prefix=None, specific_repos=None):
        """Main execution method."""
        logger.info("Starting Repository Archiving Process...")
        
        if mode == "excel":
            successful, failed = self.archive_repositories_from_excel()
        elif mode == "prefix":
            if not prefix:
                prefix = REPO_PREFIX
            successful, failed = self.archive_repositories_by_prefix(prefix)
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
                if self.archive_repository(repo_name):
                    successful += 1
                else:
                    failed += 1
        elif mode == "unarchive":
            if not specific_repos:
                logger.error("No specific repositories provided for unarchiving")
                return False
            successful = 0
            failed = 0
            for repo_name in specific_repos:
                if self.unarchive_repository(repo_name):
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
        
        if mode == "unarchive":
            logger.info(f"Unarchiving complete. Successful: {successful}, Failed: {failed}")
            if successful > 0:
                logger.info(f"Successfully unarchived {successful} repositories!")
                return True
            else:
                logger.error("No repositories were unarchived successfully!")
                return False
        else:
            logger.info(f"Archiving complete. Successful: {successful}, Failed: {failed}")
            if successful > 0:
                logger.info(f"Successfully archived {successful} repositories!")
                return True
            else:
                logger.error("No repositories were archived successfully!")
                return False


def main():
    """Main function to run the repository archiver."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Archive/Unarchive GitHub repositories")
    parser.add_argument("--mode", choices=["excel", "prefix", "specific", "list", "unarchive"], 
                       default="excel", help="Archive mode")
    parser.add_argument("--prefix", help="Repository prefix to archive")
    parser.add_argument("--repos", nargs="+", help="Specific repository names to archive/unarchive")
    parser.add_argument("--list-only", action="store_true", help="Only list repositories, don't archive")
    
    args = parser.parse_args()
    
    try:
        archiver = RepositoryArchiver()
        
        if args.list_only:
            success = archiver.run("list", args.prefix)
        else:
            success = archiver.run(args.mode, args.prefix, args.repos)
        
        if success:
            print("✅ Repository archiving completed successfully!")
            sys.exit(0)
        else:
            print("❌ Repository archiving failed. Check the logs for details.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 