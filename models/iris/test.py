import sys
import os
import unittest

# Add the file to classpath for relative import
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from base_test import ModelTest


class IrisTest(ModelTest):

    def setUp(self):
        # Train all models at the start of each test - possibly excessive, but gives full flexibility to run
        # a single test in isolation
        self.run_standalone_python_script("train.py")

    def test_single_app(self):
        self.run_python_app_test("app_svm.py", "app_test.py")

    def test_single_app_xgboost(self):
        self.run_python_app_test("app_xgb.py", "app_test.py")

    def test_scan(self):
        self.run_model_and_scan("app_svm.py", "iris_scanner_definition.yaml")


if __name__ == '__main__':
    unittest.main()
