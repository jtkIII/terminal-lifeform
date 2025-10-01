"""
File: test_compare_totals.py
Author: Jtk III
Date: 2024-06-10
Description: Test script to compare totals from the last N runs.
"""

from stats import compare_last_runs

try:
    results = compare_last_runs(n=22)
    assert results, "No results returned from compare_last_runs"
    print("✅ Tests completed successfully.")
except Exception as e:
    print(f"❌ Test failed: {e}")
    raise e

# Filepath: /home/jtk/Dev/TerminalLifeform/src/tests/test_compare_totals.py
