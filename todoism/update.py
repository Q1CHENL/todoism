import json
import time
import todoism.preference as pref

def check_for_updates() -> bool:
    """
    Check if a newer version of todoism is available on PyPI.
    Checks at most once per day and uses settings.json to store the last check time.
    """
    import sys
    import urllib.request
    import re
    
    settings_path = pref.get_settings_file_path()
    
    # Only check once per day - if we've checked recently, skip network request
    current_time = time.time()
    
    try:
        with open(settings_path, 'r') as f:
            settings = json.load(f)
            last_check = settings.get('last_update_check', 0)
            # If checked within last 24 hours, skip check
            if current_time - last_check < 86400:  # 24 hours
                return False  # Don't show update notification if we checked recently
    except (json.JSONDecodeError, FileNotFoundError):
        # If settings file is missing or invalid, we'll create/update it below
        pass
            
    # Update the timestamp in settings regardless of check result
    try:
        with open(settings_path, 'r') as f:
            try:
                settings = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                settings = pref.default_settings
        
        settings['last_update_check'] = current_time
        
        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=4)
    except Exception:
        pass
    
    try:
        # Get current installed version
        if sys.version_info >= (3, 8):
            import importlib.metadata
            current_version = importlib.metadata.version("todoism")
        else:
            import pkg_resources
            current_version = pkg_resources.get_distribution("todoism").version
        
        # Query PyPI with short timeout to not block the app
        req = urllib.request.Request(
            "https://pypi.org/pypi/todoism/json",
            headers={"User-Agent": "todoism-update-check"}
        )
        with urllib.request.urlopen(req, timeout=0.5) as response:
            data = json.loads(response.read().decode('utf-8'))
            latest_version = data["info"]["version"]
            
            # Use packaging's version parser for accurate comparison
            try:
                from packaging import version
                parsed_version = version.parse(current_version)
                if parsed_version.is_prerelease:
                    return False
                return version.parse(latest_version) > version.parse(current_version)
            except ImportError:
                # Fallback to simpler parsing if packaging module not available
                def parse_version(v):
                    return [int(x) for x in re.findall(r'\d+', v)]
                
                current_parts = parse_version(current_version)
                latest_parts = parse_version(latest_version)
                
                for i in range(max(len(current_parts), len(latest_parts))):
                    current_part = current_parts[i] if i < len(current_parts) else 0
                    latest_part = latest_parts[i] if i < len(latest_parts) else 0
                    
                    if latest_part > current_part:
                        return True
                    elif current_part > latest_part:
                        return False
                        
                return False  # Versions are equal
    except Exception:
        # Silent failure - don't interrupt startup
        return False
    
def update_todoism() -> bool:
    """
    Update todoism package.
    
    Returns: success (bool): True if update was successful
    """
    import subprocess
    import sys
    
    try:
        # Try user installation first (no admin privileges needed)
        pip_command = [sys.executable, "-m", "pip", "install", "--upgrade", "--user", "todoism"]
        process = subprocess.run(pip_command, capture_output=True, text=True)
        
        if process.returncode != 0:
            # If user installation fails, try system-wide installation
            pip_command = [sys.executable, "-m", "pip", "install", "--upgrade", "todoism"]
            process = subprocess.run(pip_command, capture_output=True, text=True)
            
            if process.returncode != 0:
                return False
                
        # Reset the last update check time to force a fresh check on next run
        try:
            settings_path = pref.get_settings_file_path()
            with open(settings_path, 'r') as f:
                settings = json.load(f)
            
            # Remove the timestamp to force a fresh check
            settings['last_update_check'] = 0
            
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=4)
        except Exception:
            pass
            
        return True
    except Exception:
        return False