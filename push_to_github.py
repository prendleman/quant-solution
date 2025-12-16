"""
Helper script to push portfolio to GitHub.
"""

import os
import sys
import subprocess

def push_to_github(repo_url: str = None):
    """
    Push portfolio to GitHub.
    
    Args:
        repo_url: GitHub repository URL (e.g., https://github.com/username/repo.git)
    """
    repo_path = os.path.dirname(os.path.abspath(__file__))
    
    # Check if remote exists
    result = subprocess.run(['git', 'remote', '-v'], 
                          cwd=repo_path, 
                          capture_output=True, 
                          text=True)
    
    if 'origin' in result.stdout:
        print("Remote 'origin' already exists.")
        print("Pushing to existing remote...")
        subprocess.run(['git', 'push', '-u', 'origin', 'master'], cwd=repo_path)
    else:
        if not repo_url:
            print("ERROR: No remote configured and no repository URL provided.")
            print("\nTo push to GitHub:")
            print("1. Create a repository on GitHub")
            print("2. Run: git remote add origin <your-repo-url>")
            print("3. Run: git push -u origin master")
            print("\nOr provide the repo URL to this script.")
            return
        
        print(f"Adding remote: {repo_url}")
        subprocess.run(['git', 'remote', 'add', 'origin', repo_url], cwd=repo_path)
        
        print("Pushing to GitHub...")
        subprocess.run(['git', 'push', '-u', 'origin', 'master'], cwd=repo_path)
        print("Done!")

if __name__ == "__main__":
    repo_url = sys.argv[1] if len(sys.argv) > 1 else None
    push_to_github(repo_url)
