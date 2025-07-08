#!/usr/bin/env python3
"""
Enhanced test runner with comprehensive logging for ENEM Pipeline tests.

This script runs the test suite with detailed logging to help identify
what and why tests are failing.
"""

import sys
import os
import logging
import subprocess
import time
from pathlib import Path
from datetime import datetime

# Configure logging for the test runner
def setup_logging():
    """Setup comprehensive logging for test execution."""
    # Create logs directory if it doesn't exist
    logs_dir = Path("tests/logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Create timestamp for log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"test_run_{timestamp}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__), log_file

def run_tests_with_verbose_output():
    """Run tests with verbose output and detailed logging."""
    logger, log_file = setup_logging()
    
    logger.info("=" * 80)
    logger.info("STARTING ENEM PIPELINE TEST SUITE")
    logger.info("=" * 80)
    logger.info(f"Test run started at: {datetime.now()}")
    logger.info(f"Log file: {log_file}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    
    # Check if we're in the right directory
    if not Path("tests").exists():
        logger.error("Tests directory not found. Please run from project root.")
        return False
    
    # Check for required files
    test_file = Path("tests/unit/test_assertions.py")
    if not test_file.exists():
        logger.error(f"Test file not found: {test_file}")
        return False
    
    logger.info(f"Found test file: {test_file}")
    
    # Run tests with pytest
    logger.info("Running tests with pytest...")
    start_time = time.time()
    
    try:
        # Run pytest with verbose output and detailed logging
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/unit/test_assertions.py",
            "-v",  # Verbose output
            "--tb=long",  # Long traceback format
            "--capture=no",  # Don't capture stdout/stderr
            "--log-cli-level=DEBUG",  # Show all log levels
            "--log-cli-format=%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "--log-file=tests/test_execution.log",
            "--log-file-level=DEBUG"
        ]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Log the results
        logger.info("=" * 80)
        logger.info("TEST EXECUTION COMPLETED")
        logger.info("=" * 80)
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Return code: {result.returncode}")
        
        if result.stdout:
            logger.info("STDOUT:")
            logger.info(result.stdout)
        
        if result.stderr:
            logger.warning("STDERR:")
            logger.warning(result.stderr)
        
        # Analyze results
        if result.returncode == 0:
            logger.info("✅ All tests passed successfully!")
            return True
        else:
            logger.error("❌ Some tests failed!")
            
            # Try to extract failure information
            if "FAILED" in result.stdout:
                logger.error("Test failures detected. Check the detailed output above.")
            
            return False
            
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        logger.error(f"Traceback: {sys.exc_info()}")
        return False

def main():
    """Main function to run the test suite."""
    print("ENEM Pipeline Test Suite Runner")
    print("=" * 50)
    
    success = run_tests_with_verbose_output()
    
    if success:
        print("\n✅ Test suite completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Test suite failed!")
        print("Check the log files for detailed information:")
        print("- tests/test_execution.log (pytest output)")
        print("- tests/logs/test_run_*.log (test runner output)")
        sys.exit(1)

if __name__ == "__main__":
    main() 