"""Configuration management for Orbit."""

import json
from pathlib import Path
from typing import Any, Dict

class Config:
    """Manages application configuration."""
    
    DEFAULT_CONFIG = {
        'auto_update_check': True,
        'update_check_interval': 86400,  # 24 hours in seconds
        'preferred_source': 'flatpak',
        'appimage_scan_dirs': [
            str(Path.home() / 'Applications'),
            str(Path.home() / '.local' / 'bin'),
            '/opt'
        ],
        'theme': 'auto',  # auto, light, dark
        'backup_location': str(Path.home() / 'Documents' / 'orbit_backups'),
        'show_notifications': True,
        'enable_logging': True,
        'log_level': 'INFO'
    }
    
    def __init__(self):
        self.config_dir = Path.home() / '.config' / 'orbit'
        self.config_file = self.config_dir / 'config.json'
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults to add any new keys
                    return {**self.DEFAULT_CONFIG, **loaded}
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                return self.DEFAULT_CONFIG.copy()
        else:
            # Create default config
            self.config_dir.mkdir(parents=True, exist_ok=True)
            self._save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()
    
    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default=None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value and save."""
        self.config[key] = value
        self._save_config(self.config)
    
    def reset(self):
        """Reset configuration to defaults."""
        self.config = self.DEFAULT_CONFIG.copy()
        self._save_config(self.config)
