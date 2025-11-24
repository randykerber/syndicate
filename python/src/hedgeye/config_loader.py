import os
import re
import yaml
from dotenv import load_dotenv
from pathlib import Path


def get_python_project_root() -> Path:
    """
    Find the Python project root directory by looking for pyproject.toml.
    
    The Python project root is where pyproject.toml lives (python/ directory).
    This is more robust than counting parent directories.
    
    Returns:
        Path to the Python project root directory
        
    Raises:
        FileNotFoundError: If project root cannot be found
    """
    current = Path(__file__).resolve()
    
    # Look for pyproject.toml going up the directory tree
    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists():
            return parent
            
    raise FileNotFoundError(
        "Cannot find Python project root (no pyproject.toml found). "
        f"Searched from: {current}"
    )


# Load secrets from .env (at python/ directory level)
_python_root = get_python_project_root()
load_dotenv(dotenv_path=_python_root / '.env')

# Load project config from config/hedgeye.yaml
def load_config():
    """
    Load configuration from hedgeye.yaml with variable substitution.
    
    Supports ${var_name} syntax in path values, where variables are defined
    in the base_paths section. For example:
    
    base_paths:
      prod_root: /Users/rk/d/downloads/hedgeye/prod
      project_root: /Users/rk/gh/randykerber/syndicate/python
    
    paths:
      ranges_dir: ${prod_root}/ranges
      mapping_file: ${project_root}/config/hedgeye/data/p-to-r-mapping.yaml
    
    Will resolve to the substituted paths.
    """
    python_root = get_python_project_root()
    config_path = python_root / "config" / "hedgeye.yaml"
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    # Resolve variable substitutions in paths
    if "base_paths" in config and "paths" in config:
        base_paths = config["base_paths"]
        
        def resolve_vars(value):
            """Recursively resolve ${var} substitutions in strings."""
            if isinstance(value, str):
                # Replace ${var_name} with value from base_paths
                def replace_var(match):
                    var_name = match.group(1)
                    if var_name in base_paths:
                        return str(base_paths[var_name])
                    else:
                        # Variable not found - return original
                        return match.group(0)
                
                # Pattern: ${var_name} (no spaces allowed in var_name)
                return re.sub(r'\$\{(\w+)\}', replace_var, value)
            elif isinstance(value, dict):
                return {k: resolve_vars(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [resolve_vars(item) for item in value]
            else:
                return value
        
        # Resolve all path values
        config["paths"] = resolve_vars(config["paths"])
    
    return config
