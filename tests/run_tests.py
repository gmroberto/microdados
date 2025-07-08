#!/usr/bin/env python3
"""
Simple test runner for ENEM Pipeline tests.

This script provides easy options for running tests with or without database support.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_database_config():
    """Check if database configuration is available."""
    required_vars = ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️  Database configuration missing: {', '.join(missing_vars)}")
        return False
    
    print("✅ Database configuration found")
    return True

def run_tests(args):
    """Run pytest with the specified arguments."""
    cmd = ['pytest']
    
    if args.verbose:
        cmd.append('-v')
    
    if args.very_verbose:
        cmd.append('-vv')
    
    if args.show_output:
        cmd.append('-s')
    
    if args.database_only:
        cmd.extend(['-m', 'database'])
    elif args.no_database:
        cmd.extend(['-m', 'not database'])
    
    if args.file:
        cmd.append(args.file)
    
    if args.class_name:
        cmd.append(f"::{args.class_name}")
    
    if args.method_name:
        cmd.append(f"::{args.method_name}")
    
    if args.coverage:
        cmd.extend(['--cov=src', '--cov-report=html', '--cov-report=term-missing'])
    
    print(f"Running: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\n❌ Test execution interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

def main():
    parser = argparse.ArgumentParser(
        description="Run ENEM Pipeline tests with easy configuration options",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage:
  python tests/run_tests.py                    # Run all non-database tests
  python tests/run_tests.py --database         # Run all tests (including database)
  python tests/run_tests.py --database-only    # Run only database tests
  python tests/run_tests.py --no-database      # Run only non-database tests
  python tests/run_tests.py --verbose          # Run with verbose output
  python tests/run_tests.py --coverage         # Run with coverage report
  python tests/run_tests.py --file test_assertions.py  # Run specific file
        """
    )
    
    # Test selection options
    parser.add_argument(
        '--database', 
        action='store_true',
        help='Run all tests including database tests (if database is configured)'
    )
    parser.add_argument(
        '--database-only', 
        action='store_true',
        help='Run only database tests'
    )
    parser.add_argument(
        '--no-database', 
        action='store_true',
        help='Run only non-database tests (default)'
    )
    
    # Output options
    parser.add_argument(
        '-v', '--verbose', 
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '-vv', '--very-verbose', 
        action='store_true',
        help='Very verbose output'
    )
    parser.add_argument(
        '-s', '--show-output', 
        action='store_true',
        help='Show print statements'
    )
    
    # Test targeting options
    parser.add_argument(
        '--file', 
        type=str,
        help='Run tests from specific file (e.g., test_assertions.py)'
    )
    parser.add_argument(
        '--class-name', 
        type=str,
        help='Run tests from specific class (e.g., TestConfiguration)'
    )
    parser.add_argument(
        '--method-name', 
        type=str,
        help='Run specific test method'
    )
    
    # Additional options
    parser.add_argument(
        '--coverage', 
        action='store_true',
        help='Run with coverage report'
    )
    parser.add_argument(
        '--check-config', 
        action='store_true',
        help='Check database configuration and exit'
    )
    
    args = parser.parse_args()
    
    # Check if we're in the right directory
    if not Path('pytest.ini').exists():
        print("❌ Error: pytest.ini not found. Please run this script from the project root.")
        return 1
    
    # Check database configuration if requested
    if args.check_config:
        has_db = check_database_config()
        return 0 if has_db else 1
    
    # Determine test mode
    if args.database:
        if not check_database_config():
            print("⚠️  Database configuration not found. Running without database tests.")
            args.no_database = True
            args.database = False
    
    if args.database_only:
        if not check_database_config():
            print("❌ Error: Database configuration required for --database-only")
            return 1
    
    # Run tests
    return run_tests(args)

if __name__ == '__main__':
    sys.exit(main()) 