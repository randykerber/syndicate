"""
Shared configuration loading utilities for the Syndicate project.
"""
import os
import re
import yaml
from pathlib import Path
from typing import Any, Dict

def load_config(config_path: Path) -> Dict[str, Any]:
    """
    Loads a YAML configuration file and resolves internal variable references.

    This loader supports `${paths.some_path}` syntax for referencing other
    values within the same file.

    Args:
        config_path: The Path object pointing to the YAML configuration file.

    Returns:
        A dictionary containing the loaded and resolved configuration.
    """
    with open(config_path, 'r') as f:
        raw_content = f.read()

    # First, expand any environment variables (e.g., $HOME)
    expanded_content = os.path.expandvars(raw_content)

    # Use a regular expression to find all `${...}` references
    def replacer(match):
        # The key path is inside the match group, e.g., "paths.prod_root"
        key_path = match.group(1)
        keys = key_path.split('.')
        
        # Walk the data dictionary to find the replacement value
        # We need to load the YAML first to know the values
        temp_data = yaml.safe_load(expanded_content)
        value = temp_data
        try:
            for key in keys:
                value = value[key]
            return str(value)
        except (KeyError, TypeError):
            # If the key doesn't exist, return the original placeholder
            return match.group(0)

    # Iteratively replace references. This allows nested references.
    # A simple loop is used here; for very deep nesting, a more complex
    # graph-based resolver might be needed, but this is robust for most cases.
    resolved_content = expanded_content
    for _ in range(5): # Limit iterations to prevent infinite loops
        new_content = re.sub(r'\$\{(.*?)\}', replacer, resolved_content)
        if new_content == resolved_content:
            break # No more substitutions found
        resolved_content = new_content

    return yaml.safe_load(resolved_content)
