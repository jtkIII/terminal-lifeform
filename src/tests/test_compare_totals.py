from stats import compare_last_runs

try:
    results = compare_last_runs(n=10)
    assert results, "No results returned from compare_last_runs"
    print("✅ Tests completed successfully.")
except Exception as e:
    print(f"❌ Test failed: {e}")
    raise e
