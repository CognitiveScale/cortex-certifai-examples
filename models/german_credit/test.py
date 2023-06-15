import sys
import os
import unittest

# Add the file to classpath for relative import
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from base_test import ModelTest


class GermanCreditTest(ModelTest):

    def setUp(self):
        self.run_standalone_python_script("train.py")

    def test_single_app(self):
        self.run_python_app_test("app_dtree.py", "app_test.py")

    def test_composed_app(self):
        self.run_python_app_test("composed_app.py", "composed_app_test.py")

    def test_trust_scan(self):
        self.run_model_and_scan("composed_app.py", "german_credit_scanner_definition.yaml")

    def test_explain_scan(self):
        self.run_standalone_python_script("explain.py")

    def test_soft_scoring_app(self):
        self.run_python_app_test("app_mlp_soft_scoring.py", "app_mlp_soft_scoring_test.py")

    def test_soft_scoring_scan(self):
        self.run_model_and_scan("app_mlp_soft_scoring.py", "german_credit_shap_explanation_scanner_definition.yaml")


if __name__ == '__main__':
    unittest.main()
