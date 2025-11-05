from typing import Dict
from pathlib import Path
from typing import Any, List, Union

import yaml

class YamlFile:
    """Represents a loaded YAML file with convenient data access methods."""
    
    def __init__(self, data: Dict[str, Any] = None, file_path: Union[str, Path] = None):
        self.data = data or {}
        self.file_path = file_path
    
    def exists_key(self, key_path: str) -> bool:
        """Check if a key exists using dot notation."""
        try:
            keys = key_path.split('.')
            value = self.data
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return False
            return True
        except (AttributeError, TypeError):
            return False
    
    def get(self, key_path: str, default: Any = None) -> Any:
        try:
            keys = key_path.split('.')
            value = self.data
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
            return value
        except (AttributeError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any) -> None:
        try:
            keys = key_path.split('.')
            current = self.data
            
            # Navigate to the parent of the target key
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                elif not isinstance(current[key], dict):
                    current[key] = {}
                current = current[key]
            
            # Set the final value
            current[keys[-1]] = value
        except (AttributeError, TypeError, IndexError):
            pass
    
    def has_required_keys(self, required_keys: List[str]) -> bool:
        return all(self.exists_key(key) for key in required_keys)
    
    def has_value(self, key_path: str) -> bool:
        """Check if a value exists at the given key path (not None)."""
        return self.get(key_path) is not None

    def save(self, file_path: Union[str, Path] = None) -> bool:
        target_path = file_path or self.file_path
        if not target_path:
            return False
        
        try:
            file_path = Path(file_path)
            # Create directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as file:
                yaml.safe_dump(self.data, file, default_flow_style=False,
                               allow_unicode=True, sort_keys=False)
            return True
        except (yaml.YAMLError, IOError, UnicodeEncodeError):
            return False

    def to_dict(self) -> Dict[str, Any]:
        return self.data.copy()
    
    def get_value(self, key_path: str, default: Any = None) -> Any:
        """Alias for get() method for consistency with YamlUtil."""
        return self.get(key_path, default)
    
    def validate_structure(self, required_keys: List[str]) -> bool:
        """Validate that the YAML data contains all required keys with non-None values."""
        if not isinstance(self.data, dict):
            return False
            
        return all(self.has_value(key_path) for key_path in required_keys)
    
    def merge(self, override_data: Dict[str, Any]) -> 'YamlFile':
        """Merge this YAML data with override data."""
        try:
            result = self.data.copy()
            for key, value in override_data.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = self._merge_dict_recursive(result[key], value)
                else:
                    result[key] = value
            return YamlFile(result, self.file_path)
        except (AttributeError, TypeError):
            return YamlFile(self.data.copy(), self.file_path)
    
    def _merge_dict_recursive(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge two dictionaries."""
        try:
            result = base.copy()
            for key, value in override.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = self._merge_dict_recursive(result[key], value)
                else:
                    result[key] = value
            return result
        except (AttributeError, TypeError):
            return base
