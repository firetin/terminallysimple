"""
Configuration management for Terminally Simple
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class Config:
    """Manages application configuration and user preferences."""
    
    DEFAULT_CONFIG: Dict[str, Any] = {
        "theme": "textual-dark",
    }
    
    def __init__(self) -> None:
        self.config_dir = Path.home() / ".config" / "terminallysimple"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._config = self._load()
    
    def _load(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config: Dict[str, Any] = json.load(f)
                    return {**self.DEFAULT_CONFIG, **loaded_config}
            except json.JSONDecodeError as e:
                logger.warning(f"Config file is corrupted ({e}). Using defaults.")
                return self.DEFAULT_CONFIG.copy()
            except (OSError, IOError) as e:
                logger.warning(f"Could not read config file: {e}. Using defaults.")
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()
    
    def save(self) -> bool:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
            return True
        except (OSError, IOError) as e:
            logger.error(f"Could not save config file: {e}")
            return False
        except (TypeError, ValueError) as e:
            logger.error(f"Invalid config data: {e}")
            return False
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
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
