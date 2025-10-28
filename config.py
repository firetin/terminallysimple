"""
Configuration management for Terminally Simple
"""

import json
from pathlib import Path
from typing import Dict, Any


class Config:
    """Manages application configuration and user preferences."""
    
    DEFAULT_CONFIG = {
        "theme": "textual-dark",
    }
    
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "terminallysimple"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._config = self._load()
    
    def _load(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    return {**self.DEFAULT_CONFIG, **loaded_config}
            except json.JSONDecodeError as e:
                print(f"Warning: Config file is corrupted ({e}). Using defaults.")
                return self.DEFAULT_CONFIG.copy()
            except (OSError, IOError) as e:
                print(f"Warning: Could not read config file ({e}). Using defaults.")
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()
    
    def save(self) -> bool:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
            return True
        except (OSError, IOError) as e:
            print(f"Error: Could not save config file: {e}")
            return False
        except (TypeError, ValueError) as e:
            print(f"Error: Invalid config data: {e}")
            return False
    
    def get(self, key: str, default=None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self._config[key] = value
    
    def reset(self) -> None:
        """Reset configuration to defaults."""
        self._config = self.DEFAULT_CONFIG.copy()
        self.save()


# Global config instance
config = Config()
