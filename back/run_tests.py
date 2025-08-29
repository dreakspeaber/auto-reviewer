#!/usr/bin/env python3
"""
Test runner script for the GCP module.
"""

import sys
import subprocess
import os

def run_tests(verbose=False, coverage=False):
    """Run the tests with specified options."""
    cmd = [sys.executable, "-m", "pytest", "test_gcp.py"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=gcp", "--cov-report=term-missing"])
    
    print(f"Running tests with command: {' '.join(cmd)}")
    print("-" * 50)
    
    result = subprocess.run(cmd, cwd=os.path.dirname(__file__))
    return result.returncode

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run tests for the GCP module")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-c", "--coverage", action="store_true", help="Run with coverage")
    
    args = parser.parse_args()
    
    exit_code = run_tests(verbose=args.verbose, coverage=args.coverage)
    sys.exit(exit_code)
