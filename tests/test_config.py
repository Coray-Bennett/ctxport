"""
Unit tests for the configuration module
"""

import unittest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path

from ctxport.config.config import Config
from ctxport.config.config_manager import ConfigManager


class TestConfig(unittest.TestCase):
    """Test the Config class"""
    
    def test_default_config(self):
        """Test getting default configuration"""
        config = Config.get_default_config()
        
        # Verify default language mappings are present
        self.assertIn('.py', config.language_map)
        self.assertEqual('python', config.language_map['.py'])
        
        # Verify default filename mappings are present
        self.assertIn('dockerfile', config.filename_map)
        self.assertEqual('dockerfile', config.filename_map['dockerfile'])
        
        # Verify default text extensions are present
        self.assertIn('.txt', config.text_extensions)
        
        # Verify default ignore patterns are present
        self.assertTrue(any(pattern.endswith('/') for pattern in config.ignore_patterns))
    
    def test_config_merge(self):
        """Test merging configurations"""
        config1 = Config(
            language_map={'.a': 'lang-a', '.b': 'lang-b'},
            filename_map={'file1': 'lang1'},
            text_extensions={'.a', '.b'},
            ignore_patterns=['pattern1', 'pattern2']
        )
        
        config2 = Config(
            language_map={'.b': 'new-lang-b', '.c': 'lang-c'},
            filename_map={'file2': 'lang2'},
            text_extensions={'.b', '.c'},
            ignore_patterns=['pattern2', 'pattern3']
        )
        
        merged = config1.merge(config2)
        
        # Check language map merging
        self.assertEqual(merged.language_map['.a'], 'lang-a')
        self.assertEqual(merged.language_map['.b'], 'new-lang-b')  # Overridden
        self.assertEqual(merged.language_map['.c'], 'lang-c')
        
        # Check filename map merging
        self.assertEqual(merged.filename_map['file1'], 'lang1')
        self.assertEqual(merged.filename_map['file2'], 'lang2')
        
        # Check text extensions merging
        self.assertEqual(merged.text_extensions, {'.a', '.b', '.c'})
        
        # Check ignore patterns merging (duplicates removed)
        self.assertEqual(merged.ignore_patterns, ['pattern1', 'pattern2', 'pattern3'])


class TestConfigManager(unittest.TestCase):
    """Test the ConfigManager class"""
    
    def setUp(self):
        """Set up for tests"""
        # Create a ConfigManager with a clean cache for each test
        self.config_manager = ConfigManager()
        self.config_manager._cached_configs = {}
        self.config_manager._global_config = None
    
    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_config_file(self, mock_file, mock_exists):
        """Test loading configuration from a file"""
        # Mock the file existence and content
        mock_exists.return_value = True
        mock_file.return_value.__enter__.return_value.read.return_value = '''
        {
            "language_map": {".test": "test-lang"},
            "filename_map": {"testfile": "test-lang"},
            "text_extensions": [".test"],
            "ignore_patterns": ["test/"]
        }
        '''
        
        # Test loading a config file
        config_path = Path('/test/config.json')
        config = self.config_manager._load_config_file(config_path)
        
        # Verify the config was loaded correctly
        self.assertEqual(config.language_map, {".test": "test-lang"})
        self.assertEqual(config.filename_map, {"testfile": "test-lang"})
        self.assertEqual(config.text_extensions, {".test"})
        self.assertEqual(config.ignore_patterns, ["test/"])
    
    @patch('ctxport.config.config_manager.ConfigManager._load_config_file')
    @patch('pathlib.Path.exists')
    def test_get_config_for_directory(self, mock_exists, mock_load_config):
        """Test getting configuration for a directory"""
        # Set up mocks
        mock_exists.return_value = True
        
        # Mock the default config
        default_config = Config.get_default_config()
        
        # Mock the global config
        global_config = Config(language_map={'.custom': 'custom'})
        mock_load_config.side_effect = [global_config]
        
        # Get the config for a directory
        test_dir = Path('/test/dir')
        config = self.config_manager.get_config_for_directory(test_dir)
        
        # Verify the config was merged correctly
        self.assertIn('.py', config.language_map)  # From default
        self.assertIn('.custom', config.language_map)  # From global
        self.assertEqual('custom', config.language_map['.custom'])


if __name__ == '__main__':
    unittest.main()