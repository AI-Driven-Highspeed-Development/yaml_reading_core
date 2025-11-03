from managers.config_manager import ConfigManager

class YamlReadingCore:
    
    def __init__(self):
        self.cm = ConfigManager()
        self.config = self.cm.config.yaml_reading_core
        
    def display_module_name(self):
        print("Module Name:", self.config.module_name)