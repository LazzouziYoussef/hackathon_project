#!/usr/bin/env python
"""Simple test runner for ML engine tests.

Run with: python run_tests.py
"""
import sys
import os

# Add ml_engine to path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import test modules
from tests import test_preprocessing
from tests import test_feature_engineering
from tests import test_seasonal_baseline
from tests import test_pattern_learning
from tests import test_confidence_scoring
from tests import test_hybrid_forecaster


def run_test_module(module, module_name):
    """Run all test functions in a module."""
    print(f"\n{'='*60}")
    print(f"Running {module_name}")
    print('='*60)
    
    test_count = 0
    passed = 0
    failed = 0
    
    for name in dir(module):
        if name.startswith('test_'):
            test_count += 1
            test_func = getattr(module, name)
            try:
                test_func()
                passed += 1
                print(f"✅ {name}")
            except Exception as e:
                failed += 1
                print(f"❌ {name}: {e}")
    
    print(f"\n{module_name}: {passed}/{test_count} passed")
    return failed == 0


def main():
    """Run all tests."""
    print("Sadaqa Tech ML Engine Test Suite")
    print("="*60)
    
    all_passed = True
    
    all_passed &= run_test_module(test_preprocessing, "test_preprocessing")
    all_passed &= run_test_module(test_feature_engineering, "test_feature_engineering")
    all_passed &= run_test_module(test_seasonal_baseline, "test_seasonal_baseline")
    all_passed &= run_test_module(test_pattern_learning, "test_pattern_learning")
    all_passed &= run_test_module(test_confidence_scoring, "test_confidence_scoring")
    all_passed &= run_test_module(test_hybrid_forecaster, "test_hybrid_forecaster")
    
    print(f"\n{'='*60}")
    if all_passed:
        print("✅ ALL TESTS PASSED")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
