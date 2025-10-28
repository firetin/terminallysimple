"""
Configuration management for Terminally Simple
"""

import json
from pathlib import Path
from typing import Dict, Any


class Config:
    """Manages application configuration and user preferences."""
    
    DEFAULT_CONFIG = {
        "theme": "dark",
        "accent_color": "cyan",
        "background": "default",
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
                    return {**self.DEFAULT_CONFIG, **json.load(f)}
            except Exception:
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()
    
    def save(self) -> bool:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
            return True
        except Exception:
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
