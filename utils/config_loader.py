# utils/config_loader.py
import json
import os
from typing import List, Dict, Any, Optional

SERVER_INFO_FILE = "server_info.json"
VALIDATION_WARNINGS_KEY = "__validation_warnings__" # Internal key

def load_server_configs() -> List[Dict[str, Any]]:
    """
    Loads and validates server configurations from SERVER_INFO_FILE.

    Returns:
        A list of valid server configuration dictionaries.
        Includes a special key '__validation_warnings__' if any issues were found
        during validation of individual items, even if some valid items exist.
        Raises exceptions for critical file-level errors (not found, invalid JSON).
    """
    configs: List[Dict[str, Any]] = []
    warnings: List[str] = []

    if not os.path.isfile(SERVER_INFO_FILE):
        raise FileNotFoundError(f"Configuration file `{SERVER_INFO_FILE}` not found.")

    try:
        with open(SERVER_INFO_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Failed to parse `{SERVER_INFO_FILE}`. Invalid JSON: {e.msg}", e.doc, e.pos)
    except Exception as e:
        raise IOError(f"An error occurred while reading `{SERVER_INFO_FILE}`: {e}")

    if not isinstance(data, list):
        raise TypeError(f"`{SERVER_INFO_FILE}` content must be a JSON list (array).")

    for index, item in enumerate(data):
        if isinstance(item, dict):
            ip = item.get("ip")
            name = item.get("Name") # Case-sensitive 'Name'

            # Basic validation for status checking
            if ip and isinstance(ip, str) and ip.strip() and \
               name and isinstance(name, str) and name.strip():
                valid_config = {"ip": ip.strip(), "Name": name.strip()}
                # Add optional RCON details if present and seem valid
                rcon_port = item.get("rcon_port")
                rcon_password = item.get("rcon_password")
                if rcon_port is not None:
                    try:
                        valid_config["rcon_port"] = int(rcon_port)
                    except (ValueError, TypeError):
                         warnings.append(f"Warning: Item {index+1} ('{name}') has non-integer 'rcon_port'. RCON will be disabled.")
                if rcon_password is not None and isinstance(rcon_password, str):
                     valid_config["rcon_password"] = rcon_password
                elif rcon_port is not None and rcon_password is None:
                     warnings.append(f"Warning: Item {index+1} ('{name}') has 'rcon_port' but missing 'rcon_password'. RCON will be disabled.")


                configs.append(valid_config)
            else:
                warning_msg = f"Warning: Item {index+1} in `{SERVER_INFO_FILE}` is missing a valid string 'ip' or 'Name'. Skipping."
                print(warning_msg)
                warnings.append(warning_msg)
        else:
            warning_msg = f"Warning: Item {index+1} in `{SERVER_INFO_FILE}` is not a valid JSON object (dictionary). Skipping."
            print(warning_msg)
            warnings.append(warning_msg)

    if warnings:
        # Attach warnings to the returned list using a special key
        # This allows the calling cog to access them if needed.
        # Note: This modifies the list object itself by adding an attribute.
        # A more robust way might be returning a tuple (configs, warnings).
        setattr(configs, VALIDATION_WARNINGS_KEY, warnings)
        # Alternatively: return configs, warnings

    if not configs and not data:
         print(f"Warning: `{SERVER_INFO_FILE}` is empty or contains no processable server entries.")
    elif not configs and data:
         print(f"Warning: No valid server configurations found in `{SERVER_INFO_FILE}` after validation.")


    print(f"Loaded {len(configs)} valid server configurations from {SERVER_INFO_FILE}.")
    return configs

def get_validation_warnings(configs: List[Dict[str, Any]]) -> List[str]:
    """Helper to retrieve warnings attached to the config list."""
    return getattr(configs, VALIDATION_WARNINGS_KEY, [])