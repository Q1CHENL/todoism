def check_for_updates() -> bool:
    """
    Check if a newer version of todoism is available on PyPI.
    Uses cached results to improve speed.
    """
    import sys
    import urllib.request
    import json
    import re
    import os
    import time
    
    # Cache path for update check results
    cache_dir = os.path.join(os.path.expanduser("~"), ".todoism")
    cache_file = os.path.join(cache_dir, "update_cache.json")
    os.makedirs(cache_dir, exist_ok=True)
    
    # Only check once per day
    check_required = True
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                cache = json.load(f)
                last_check = cache.get('timestamp', 0)
                current_time = time.time()
                # If checked within last 24 hours, use cached result
                if current_time - last_check < 86400:  # 24 hours
                    check_required = False
                    return cache.get('update_available', False)
        except (json.JSONDecodeError, IOError):
            pass
            
    if not check_required:
        return False
    
    try:
        # Get current installed version based on Python version
        if sys.version_info >= (3, 8):
            import importlib.metadata
            current_version = importlib.metadata.version("todoism")
        else:
            import pkg_resources
            current_version = pkg_resources.get_distribution("todoism").version
        
        # Query PyPI with shorter timeout
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
                update_available = version.parse(latest_version) > version.parse(current_version)
            except ImportError:
                # Fallback to simpler parsing
                def parse_version(v):
                    return [int(x) for x in re.findall(r'\d+', v)]
                
                current_parts = parse_version(current_version)
                latest_parts = parse_version(latest_version)
                
                update_available = False
                for i in range(max(len(current_parts), len(latest_parts))):
                    current_part = current_parts[i] if i < len(current_parts) else 0
                    latest_part = latest_parts[i] if i < len(latest_parts) else 0
                    
                    if latest_part > current_part:
                        update_available = True
                        break
                    elif current_part > latest_part:
                        update_available = False
                        break
            
            # Cache the result
            try:
                with open(cache_file, 'w') as f:
                    json.dump({
                        'timestamp': time.time(),
                        'update_available': update_available,
                        'current_version': current_version,
                        'latest_version': latest_version
                    }, f)
            except IOError:
                pass
                    
            return update_available
    except Exception:
        # Silent failure - don't interrupt startup
        return False
    
def update_todoism() -> bool:
    """
    Update todoism package while preserving user data files.
    
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
                return (False, f"Update failed: {process.stderr}")
        
        return True
    except Exception as e:
        return False