"""
Git repository integration module
Handles cloning, pulling, and managing repositories
"""
import os
import shutil
from pathlib import Path
from git import Repo, Git
from utils.logger import setup_logger

logger = setup_logger(__name__)

class GitHandler:
    """Handle Git operations for repositories"""
    
    def __init__(self, repos_dir: str = "/tmp/repos"):
        self.repos_dir = Path(repos_dir)
        self.repos_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"GitHandler initialized with repos_dir: {repos_dir}")
    
    def clone_repository(self, repo_url: str, repo_name: str = None) -> Path:
        """
        Clone a repository from URL
        
        Args:
            repo_url: URL of the repository
            repo_name: Optional custom name for the repo folder
            
        Returns:
            Path to the cloned repository
        """
        if repo_name is None:
            repo_name = repo_url.split("/")[-1].replace(".git", "")
        
        repo_path = self.repos_dir / repo_name
        
        if repo_path.exists():
            logger.warning(f"Repository {repo_name} already exists, updating...")
            self.pull_repository(repo_path)
            return repo_path
        
        try:
            logger.info(f"Cloning repository from {repo_url}")
            Repo.clone_from(repo_url, str(repo_path))
            logger.info(f"Successfully cloned to {repo_path}")
            return repo_path
        except Exception as e:
            logger.error(f"Failed to clone repository: {e}")
            raise
    
    def pull_repository(self, repo_path: Path) -> bool:
        """
        Pull latest changes from repository
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            True if successful
        """
        try:
            repo = Repo(str(repo_path))
            logger.info(f"Pulling latest changes from {repo_path}")
            repo.remotes.origin.pull()
            logger.info(f"Successfully updated {repo_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to pull repository: {e}")
            raise
    
    def get_repository(self, repo_path: Path) -> Repo:
        """
        Get Git repository object
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            GitPython Repo object
        """
        return Repo(str(repo_path))
    
    def get_file_content(self, repo_path: Path, file_path: str) -> str:
        """
        Get file content from repository
        
        Args:
            repo_path: Path to the repository
            file_path: Relative path to file in repo
            
        Returns:
            File content as string
        """
        full_path = repo_path / file_path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    
    def write_file_content(self, repo_path: Path, file_path: str, content: str) -> bool:
        """
        Write content to file in repository
        
        Args:
            repo_path: Path to the repository
            file_path: Relative path to file in repo
            content: Content to write
            
        Returns:
            True if successful
        """
        full_path = repo_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Updated file: {file_path}")
        return True
    
    def cleanup_repository(self, repo_path: Path) -> bool:
        """
        Delete repository from disk
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            True if successful
        """
        try:
            if repo_path.exists():
                shutil.rmtree(repo_path)
                logger.info(f"Cleaned up repository: {repo_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to cleanup repository: {e}")
            raise
