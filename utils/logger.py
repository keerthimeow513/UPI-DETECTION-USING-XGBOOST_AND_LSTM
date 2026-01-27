import logging # Import the standard Python logging library for tracking events
import os # Import OS library for file and directory operations
from logging.handlers import RotatingFileHandler # Import a handler that rotates log files when they reach a certain size

def setup_logger(name="UPI_Fraud_Detection", log_file="project.log"): # Define a function to initialize our custom logger
    logger = logging.getLogger(name) # Create or retrieve a logger instance with the specified name
    logger.setLevel(logging.INFO) # Set the minimum logging level to INFO (ignoring DEBUG messages)
    
    # Create handlers
    c_handler = logging.StreamHandler() # Create a handler to output logs to the console (standard output)
    f_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5) # Create a file handler that rotates at 10MB and keeps 5 old logs
    
    # Create formatters and add it to handlers
    c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') # Define the text format for console logs (Time - Name - Level - Msg)
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') # Define the same text format for file logs for consistency
    
    c_handler.setFormatter(c_format) # Apply the formatter to the console handler
    f_handler.setFormatter(f_format) # Apply the formatter to the file handler
    
    # Add handlers to the logger
    if not logger.handlers: # Check if the logger already has handlers to prevent duplicate logging
        logger.addHandler(c_handler) # Attach the console handler to the logger
        logger.addHandler(f_handler) # Attach the file handler to the logger
        
    return logger # Return the configured logger object for use throughout the project
