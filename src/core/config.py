"""
Configuration loader for URL Organizer
Loads and manages global.yaml configuration
"""
import yaml
from pathlib import Path
from typing import Dict, Any, List


class Config:
    """Global configuration manager"""

    def __init__(self, config_path: str = None):
        """
        Load configuration from YAML file

        Args:
            config_path: Path to global.yaml, defaults to config/global.yaml
        """
        if config_path is None:
            # Default to project root/config/global.yaml
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "global.yaml"

        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load YAML configuration file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key

        Args:
            key: Dot-notation key (e.g., 'url_parsing.tracker_params')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def get_tracker_params(self) -> List[str]:
        """Get list of tracker parameters to remove from URLs"""
        return self.get('url_parsing.tracker_params', [])

    def get_normalize_settings(self) -> Dict[str, bool]:
        """Get URL normalization settings"""
        return self.get('url_parsing.normalize', {})

    def get_enabled_methods(self) -> List[str]:
        """Get list of enabled organization methods"""
        return self.get('organization_methods.enabled', [])

    def get_output_dir(self, output_type: str) -> Path:
        """
        Get output directory path

        Args:
            output_type: Type of output ('processed_data_dir', 'analysis_dir', 'visualization_dir')

        Returns:
            Path to output directory
        """
        project_root = Path(__file__).parent.parent.parent
        rel_path = self.get(f'output.{output_type}', f'data/{output_type}')
        return project_root / rel_path

    def get_visualization_settings(self) -> Dict[str, Any]:
        """Get visualization configuration"""
        return self.get('visualization.settings', {})

    def reload(self):
        """Reload configuration from file"""
        self.config = self._load_config()


# Global config instance
_config = None


def get_config() -> Config:
    """Get global configuration instance (singleton)"""
    global _config
    if _config is None:
        _config = Config()
    return _config
