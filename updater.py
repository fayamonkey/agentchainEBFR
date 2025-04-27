import os
import json
import git
import logging
import shutil
import requests
from typing import Tuple, Optional

class GitHubUpdater:
    REPO_URL = "https://github.com/SamuelSchmidgall/AgentLaboratory.git"
    API_URL = "https://api.github.com/repos/SamuelSchmidgall/AgentLaboratory/commits/main"
    VERSION_FILE = "version.json"
    
    def __init__(self, local_path: str = "."):
        """Initialize the updater with the path to the local repository."""
        self.local_path = os.path.abspath(local_path)
        self.repo = None
        self.version_file = os.path.join(self.local_path, self.VERSION_FILE)
        # Don't initialize Git automatically
    
    def _get_current_version(self) -> Optional[str]:
        """Get the currently installed version from version file."""
        try:
            if os.path.exists(self.version_file):
                with open(self.version_file, 'r') as f:
                    data = json.load(f)
                    return data.get('version')
        except Exception as e:
            logging.error(f"Error reading version file: {str(e)}")
        return None
    
    def _save_current_version(self, version: str):
        """Save the current version to version file."""
        try:
            with open(self.version_file, 'w') as f:
                json.dump({'version': version}, f)
        except Exception as e:
            logging.error(f"Error saving version file: {str(e)}")
    
    def check_for_updates(self) -> Tuple[bool, Optional[str]]:
        """Check if updates are available from GitHub using the API.
        
        Returns:
            Tuple[bool, Optional[str]]: (updates_available, latest_commit_message)
        """
        try:
            # Use GitHub API to check latest commit
            response = requests.get(self.API_URL)
            if response.status_code == 200:
                latest_commit = response.json()
                latest_version = latest_commit['sha']
                current_version = self._get_current_version()
                
                # If we have a current version and it matches the latest, no update needed
                if current_version and current_version == latest_version:
                    return False, None
                    
                return True, latest_commit.get('commit', {}).get('message', 'Update available')
            return False, None
            
        except Exception as e:
            logging.error(f"Error checking for updates: {str(e)}")
            return False, None
    
    def update(self) -> Tuple[bool, str]:
        """Update by downloading the latest version.
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Get the latest version SHA
            response = requests.get(self.API_URL)
            if response.status_code == 200:
                latest_commit = response.json()
                latest_version = latest_commit['sha']
                
                # Save the new version
                self._save_current_version(latest_version)
                
                # Provide update instructions
                message = (
                    "To update to the latest version:\n"
                    "1. Visit https://github.com/SamuelSchmidgall/AgentLaboratory\n"
                    "2. Download the latest version\n"
                    "3. Replace your current files with the new ones"
                )
                return True, message
            
            return False, "Could not get latest version information"
            
        except Exception as e:
            error_msg = f"Error updating: {str(e)}"
            logging.error(error_msg)
            return False, error_msg 