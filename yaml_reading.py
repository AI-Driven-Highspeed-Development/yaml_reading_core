from pathlib import Path
from typing import Optional, Union
from cores.yaml_reading_core.yaml_file import YamlFile
import yaml

class YamlReadingCore:
    
    @staticmethod
    def read_yaml(file_path: Union[str, Path]) -> Optional[YamlFile]:
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File '{file_path}' not found")

            with open(file_path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file) or {}
                return YamlFile(data, file_path)
        except (yaml.YAMLError, IOError, UnicodeDecodeError):
            raise FileNotFoundError(f"File '{file_path}' not found or invalid")
        
    @staticmethod
    def read_yaml_str(yaml_str: str) -> Optional[YamlFile]:
        try:
            data = yaml.safe_load(yaml_str) or {}
            return YamlFile(data)
        except yaml.YAMLError:
            raise ValueError("Invalid YAML string:\n" + yaml_str)

    @staticmethod
    def write_yaml(file_path: Union[str, Path], data: dict) -> None:
        try:
            file_path = Path(file_path)
            with open(file_path, 'w', encoding='utf-8') as file:
                yaml.safe_dump(data, file, default_flow_style=False, sort_keys=False)
        except (yaml.YAMLError, IOError) as e:
            raise IOError(f"Failed to write YAML to '{file_path}': {e}")