#!/usr/bin/env python3
"""
Test failure analyzer for ENEM Pipeline tests.

This script analyzes test execution logs to identify patterns in failures
and provide insights into what went wrong.
"""

import re
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def analyze_test_logs(log_file_path="tests/test_execution.log"):
    """Analyze test execution logs for failures and patterns."""
    log_file = Path(log_file_path)
    
    if not log_file.exists():
        print(f"❌ Log file not found: {log_file}")
        print("Run the tests first to generate logs.")
        return
    
    print(f"📊 Analyzing test logs: {log_file}")
    print("=" * 80)
    
    # Read the log file
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Analyze patterns
    analysis = {
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'errors': [],
        'warnings': [],
        'test_classes': defaultdict(int),
        'failure_patterns': defaultdict(int),
        'environment_issues': [],
        'configuration_issues': [],
        'database_issues': [],
        'file_issues': []
    }
    
    # Count test results
    passed_pattern = r'PASSED'
    failed_pattern = r'FAILED'
    error_pattern = r'ERROR'
    
    analysis['passed_tests'] = len(re.findall(passed_pattern, content))
    analysis['failed_tests'] = len(re.findall(failed_pattern, content))
    analysis['total_tests'] = analysis['passed_tests'] + analysis['failed_tests']
    
    # Find test classes
    class_pattern = r'class (\w+):'
    test_classes = re.findall(class_pattern, content)
    for test_class in test_classes:
        if test_class.startswith('Test'):
            analysis['test_classes'][test_class] += 1
    
    # Find error patterns
    error_lines = [line.strip() for line in content.split('\n') if 'ERROR' in line]
    for line in error_lines:
        analysis['errors'].append(line)
        
        # Categorize errors
        if any(keyword in line.lower() for keyword in ['environment', 'env']):
            analysis['environment_issues'].append(line)
        elif any(keyword in line.lower() for keyword in ['config', 'configuration']):
            analysis['configuration_issues'].append(line)
        elif any(keyword in line.lower() for keyword in ['database', 'db', 'connection']):
            analysis['database_issues'].append(line)
        elif any(keyword in line.lower() for keyword in ['file', 'path', 'directory']):
            analysis['file_issues'].append(line)
    
    # Find warning patterns
    warning_lines = [line.strip() for line in content.split('\n') if 'WARNING' in line]
    analysis['warnings'] = warning_lines
    
    # Find common failure patterns
    failure_keywords = [
        'assert', 'assertion', 'expected', 'got', 'missing', 'not found',
        'failed', 'error', 'exception', 'traceback'
    ]
    
    for keyword in failure_keywords:
        pattern = rf'\b{keyword}\b'
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            analysis['failure_patterns'][keyword] = len(matches)
    
    # Print analysis results
    print(f"📈 Test Summary:")
    print(f"   Total tests: {analysis['total_tests']}")
    print(f"   Passed: {analysis['passed_tests']} ✅")
    print(f"   Failed: {analysis['failed_tests']} ❌")
    
    if analysis['total_tests'] > 0:
        success_rate = (analysis['passed_tests'] / analysis['total_tests']) * 100
        print(f"   Success rate: {success_rate:.1f}%")
    
    print()
    
    # Show test classes
    if analysis['test_classes']:
        print("🧪 Test Classes Found:")
        for test_class, count in analysis['test_classes'].items():
            print(f"   - {test_class}")
    
    print()
    
    # Show error categories
    if analysis['environment_issues']:
        print("🌍 Environment Issues:")
        for issue in analysis['environment_issues'][:5]:  # Show first 5
            print(f"   - {issue}")
        if len(analysis['environment_issues']) > 5:
            print(f"   ... and {len(analysis['environment_issues']) - 5} more")
    
    if analysis['configuration_issues']:
        print("⚙️  Configuration Issues:")
        for issue in analysis['configuration_issues'][:5]:
            print(f"   - {issue}")
        if len(analysis['configuration_issues']) > 5:
            print(f"   ... and {len(analysis['configuration_issues']) - 5} more")
    
    if analysis['database_issues']:
        print("🗄️  Database Issues:")
        for issue in analysis['database_issues'][:5]:
            print(f"   - {issue}")
        if len(analysis['database_issues']) > 5:
            print(f"   ... and {len(analysis['database_issues']) - 5} more")
    
    if analysis['file_issues']:
        print("📁 File/Path Issues:")
        for issue in analysis['file_issues'][:5]:
            print(f"   - {issue}")
        if len(analysis['file_issues']) > 5:
            print(f"   ... and {len(analysis['file_issues']) - 5} more")
    
    print()
    
    # Show common failure patterns
    if analysis['failure_patterns']:
        print("🔍 Common Failure Patterns:")
        sorted_patterns = sorted(analysis['failure_patterns'].items(), 
                               key=lambda x: x[1], reverse=True)
        for pattern, count in sorted_patterns[:10]:
            print(f"   - '{pattern}': {count} occurrences")
    
    print()
    
    # Provide recommendations
    print("💡 Recommendations:")
    
    if analysis['environment_issues']:
        print("   • Check environment variables (DB_USER, DB_PASSWORD, etc.)")
        print("   • Verify .env file exists and is properly configured")
    
    if analysis['configuration_issues']:
        print("   • Review config.yml and configuration files")
        print("   • Check database connection settings")
    
    if analysis['database_issues']:
        print("   • Ensure database server is running")
        print("   • Verify database credentials and permissions")
        print("   • Check network connectivity to database")
    
    if analysis['file_issues']:
        print("   • Verify required directories exist (data/, logs/, downloads/)")
        print("   • Check file permissions")
        print("   • Ensure test data files are available")
    
    if analysis['failed_tests'] > 0:
        print("   • Run individual test classes to isolate issues")
        print("   • Check the detailed log file for specific error messages")
    
    print()
    print("📋 For detailed analysis, check:")
    print(f"   - Full log: {log_file}")
    print("   - Individual test output in the log file")

def main():
    """Main function to run the analysis."""
    print("🔍 ENEM Pipeline Test Failure Analyzer")
    print("=" * 50)
    
    # Check if log file path was provided as argument
    log_file = sys.argv[1] if len(sys.argv) > 1 else "tests/test_execution.log"
    
    analyze_test_logs(log_file)

if __name__ == "__main__":
    main() 