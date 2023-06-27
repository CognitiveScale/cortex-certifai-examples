import sys
import os
import unittest

# Add the file to classpath for relative import
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from base_test import ModelTest


class PatientReadmissionTest(ModelTest):

    def setUp(self):
        self.run_standalone_python_script("train.py")

    def test_single_app(self):
        self.run_python_app_test("app.py", "app_test.py")

    def test_definition_test(self):
        self.run_model_and_definition_test("app.py", "explain_def.yml")

    def test_fast_explain(self):
        self.run_model_and_explain("app.py", "explain_def.yml", fast=True)

    def test_traditional_explain(self):
        self.run_model_and_explain("app.py", "explain_def.yml", fast=False)


if __name__ == '__main__':
    unittest.main()
