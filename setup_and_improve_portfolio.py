'''
Interactive script to set up and improve your quant portfolio repository.
This will help you configure the repo path and then improve it based on cataloged JDs.
'''

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import quant_poc_repo_path, quant_poc_repo_remote
from modules.helpers import print_lg


def setup_portfolio_repo():
    '''
    Interactive setup for portfolio repository.
    '''
    print_lg("=" * 80)
    print_lg("Quant Portfolio Repository Setup")
    print_lg("=" * 80)
    
    current_path = quant_poc_repo_path
    if current_path:
        print_lg(f"\nCurrent portfolio repo path: {current_path}")
        if os.path.exists(current_path):
            print_lg("✅ Path exists!")
            use_current = input("\nUse this path? (y/n): ").strip().lower()
            if use_current == 'y':
                return current_path
    
    print_lg("\nPlease provide your portfolio repository path:")
    print_lg("  - If it exists, provide the full path")
    print_lg("  - If it doesn't exist, we'll create it")
    print_lg("  - Example: C:/Users/YourName/quant_portfolio")
    print_lg("  - Example: G:/My Drive/quant_portfolio")
    
    repo_path = input("\nPortfolio repo path: ").strip().strip('"').strip("'")
    
    if not repo_path:
        print_lg("No path provided. Exiting.")
        return None
    
    # Normalize path
    repo_path = os.path.abspath(os.path.expanduser(repo_path))
    
    # Create directory if it doesn't exist
    if not os.path.exists(repo_path):
        create = input(f"\nDirectory doesn't exist. Create it? (y/n): ").strip().lower()
        if create == 'y':
            os.makedirs(repo_path, exist_ok=True)
            print_lg(f"✅ Created directory: {repo_path}")
        else:
            print_lg("Directory not created. Exiting.")
            return None
    
    # Initialize git if not already a repo
    if not os.path.exists(os.path.join(repo_path, '.git')):
        init_git = input("\nInitialize as git repository? (y/n): ").strip().lower()
        if init_git == 'y':
            import subprocess
            try:
                subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True, timeout=10)
                print_lg("✅ Initialized git repository")
            except Exception as e:
                print_lg(f"⚠️  Git init failed: {e}")
    
    # Update config file
    update_config = input(f"\nUpdate config/settings.py with this path? (y/n): ").strip().lower()
    if update_config == 'y':
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'config', 'settings.py')
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace the quant_poc_repo_path line
            import re
            pattern = r'quant_poc_repo_path = ".*"'
            replacement = f'quant_poc_repo_path = "{repo_path.replace(chr(92), "/")}"'
            content = re.sub(pattern, replacement, content)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print_lg("✅ Updated config/settings.py")
        except Exception as e:
            print_lg(f"⚠️  Failed to update config: {e}")
            print_lg(f"   Please manually set quant_poc_repo_path = \"{repo_path}\" in config/settings.py")
    
    return repo_path


def main():
    '''
    Main function.
    '''
    # Setup repo path
    repo_path = setup_portfolio_repo()
    if not repo_path:
        return
    
    print_lg("\n" + "=" * 80)
    print_lg("Ready to improve portfolio!")
    print_lg("=" * 80)
    
    # Run improvement script
    print_lg("\nRunning portfolio improvement script...")
    print_lg("(This will analyze all cataloged JDs and add missing functionality)\n")
    
    try:
        # Import and run the improvement script
        from improve_portfolio import main as improve_main
        improve_main()
    except Exception as e:
        print_lg(f"\nError running improvement: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
