import sys
import os
import unittest

# Add the file to classpath for relative import
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from base_test import ModelTest


class IncomePredictionTest(ModelTest):

    def setUp(self):
        self.run_standalone_python_script("train.py")

    def test_single_app(self):
        self.run_python_app_test("app_xgb.py", "app_test.py")

    def test_explain_scan(self):
        self.run_model_and_scan("app_xgb.py", "income_explain_definition.yaml")


if __name__ == '__main__':
    unittest.main()
