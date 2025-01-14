import configparser
import os
from pathlib import Path
from typing import Dict, Any

class ConfigLoader:
    def __init__(self, config_path: str = "config.ini"):
        """Initialize configuration loader
        
        Args:
            config_path: Path to the config.ini file
        """
        self.config = configparser.ConfigParser()
        self.config_path = config_path
        self._load_config()
        self._setup_directories()

    def _load_config(self):
        """Load configuration from INI file"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        self.config.read(self.config_path)
        
        # Convert relative paths to absolute paths based on config file location
        base_dir = Path(self.config_path).parent.absolute()
        
        # Update paths in config
        self.config['MODEL']['path'] = str(base_dir / self.config['MODEL']['path'])
        self.config['DATA']['universe_data_path'] = str(base_dir / self.config['DATA']['universe_data_path'])
        self.config['OUTPUT']['base_dir'] = str(base_dir / self.config['OUTPUT']['base_dir'])
        self.config['OUTPUT']['story_images_dir'] = str(base_dir / self.config['OUTPUT']['story_images_dir'])

    def _setup_directories(self):
        """Create necessary directories"""
        directories = [
            self.config['MODEL']['path'],
            os.path.dirname(self.config['DATA']['universe_data_path']),
            self.config['OUTPUT']['base_dir'],
            self.config['OUTPUT']['story_images_dir']
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def get_model_config(self) -> Dict[str, Any]:
        """Get model configuration"""
        return {
            'path': self.config['MODEL']['path'],
            'default_size': self.config.getint('MODEL', 'default_size'),
            'max_size': self.config.getint('MODEL', 'max_size'),
            'min_size': self.config.getint('MODEL', 'min_size'),
            'size_step': self.config.getint('MODEL', 'size_step')
        }

    def get_data_config(self) -> Dict[str, str]:
        """Get data configuration"""
        return {
            'universe_data_path': self.config['DATA']['universe_data_path']
        }

    def get_output_config(self) -> Dict[str, str]:
        """Get output configuration"""
        return {
            'base_dir': self.config['OUTPUT']['base_dir'],
            'story_images_dir': self.config['OUTPUT']['story_images_dir']
        }

    def get_pipeline_config(self) -> Dict[str, Any]:
        """Get pipeline configuration"""
        return {
            'num_inference_steps': self.config.getint('PIPELINE', 'num_inference_steps'),
            'guidance_scale': self.config.getfloat('PIPELINE', 'guidance_scale'),
            'num_images_per_prompt': self.config.getint('PIPELINE', 'num_images_per_prompt')
        }

    def get_style_config(self) -> Dict[str, Any]:
        """Get style configuration"""
        return {
            'base_style': self.config['STYLE']['base_style'],
            'quality_boost': self.config['STYLE']['quality_boost'],
            'weights': {
                'main_prompt': self.config.getfloat('WEIGHTS', 'main_prompt'),
                'style': self.config.getfloat('WEIGHTS', 'style'),
                'scene': self.config.getfloat('WEIGHTS', 'scene'),
                'quality': self.config.getfloat('WEIGHTS', 'quality')
            }
        }

    def get_all_config(self) -> Dict[str, Dict]:
        """Get all configurations"""
        return {
            'model': self.get_model_config(),
            'data': self.get_data_config(),
            'output': self.get_output_config(),
            'pipeline': self.get_pipeline_config(),
            'style': self.get_style_config()
        }