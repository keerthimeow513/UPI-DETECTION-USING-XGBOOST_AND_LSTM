"""Unit tests for logger module."""

import unittest
import os
import sys
import logging
import tempfile
import shutil

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from utils.logger import setup_logger


class TestLogger(unittest.TestCase):
    """Test cases for the logger utility."""
    
    def test_logger_initialization(self):
        """Test that logger initializes correctly."""
        logger = setup_logger("test_logger")
        
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test_logger")
        self.assertEqual(logger.level, logging.INFO)
    
    def test_logger_has_handlers(self):
        """Test that logger has both console and file handlers."""
        logger = setup_logger("test_logger_handlers")
        
        # Check that handlers exist
        self.assertGreaterEqual(len(logger.handlers), 2)
        
        # Check handler types
        handler_types = [type(h) for h in logger.handlers]
        self.assertIn(logging.StreamHandler, handler_types)
    
    def test_logger_log_levels(self):
        """Test that logger respects log levels."""
        logger = setup_logger("test_logger_levels")
        
        # Test that INFO level is set
        self.assertTrue(logger.isEnabledFor(logging.INFO))
        
        # Test that DEBUG level is NOT enabled (since we set INFO)
        self.assertFalse(logger.isEnabledFor(logging.DEBUG))
    
    def test_logger_file_output(self):
        """Test that logger writes to file."""
        temp_dir = tempfile.mkdtemp()
        log_file = os.path.join(temp_dir, "test.log")
        
        try:
            logger = setup_logger("test_file_logger", log_file)
            test_message = "Test log message"
            logger.info(test_message)
            
            # Close handlers to flush the file
            for handler in logger.handlers:
                handler.close()
            
            # Check that file was created and contains message
            self.assertTrue(os.path.exists(log_file))
            with open(log_file, 'r') as f:
                content = f.read()
                self.assertIn(test_message, content)
                
        finally:
            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_logger_singleton_pattern(self):
        """Test that getting same logger name returns same instance."""
        logger1 = setup_logger("singleton_test")
        logger2 = setup_logger("singleton_test")
        
        # Should be the same object
        self.assertIs(logger1, logger2)
    
    def test_logger_format(self):
        """Test that logger format includes expected fields."""
        logger = setup_logger("test_format")
        
        # Check that handlers have formatters
        for handler in logger.handlers:
            formatter = handler.formatter
            self.assertIsNotNone(formatter)
            
            # Check format string includes expected fields
            format_str = formatter._fmt
            self.assertIn('%(asctime)s', format_str)
            self.assertIn('%(name)s', format_str)
            self.assertIn('%(levelname)s', format_str)
            self.assertIn('%(message)s', format_str)


if __name__ == '__main__':
    unittest.main()
