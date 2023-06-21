import time
import contextlib
import subprocess
import tempfile
import unittest
from typing import Optional, Sequence


def capture_err_and_out(stderr, stdout):
    if stderr is not None:
        print("\n---------------------- (main) stderr: ----------------------")
        print(stderr, end="")
        print("\n------------------------------------------------------------\n")
    if stdout is not None:
        print("\n---------------------- (main) stdout: ----------------------")
        print(stdout, end="")
        print("\n------------------------------------------------------------")


def capture_output(stdout, stderr, limit=100):
    count = 0
    print("\n---------------------- (service) stdout: ----------------------\n")
    with open(stdout, 'r+') as f:
        for line in f:
            if count > limit:
                break
            print(line, end="")
            limit += 1
    print("\n------------------------------------------------------------\n")
    print()

    count = 0
    print("\n---------------------- (service) stderr: ----------------------\n")
    with open(stderr, 'r+') as f:
        for line in f:
            if count > limit:
                break
            print(line, end="")
            limit += 1
    print("\n------------------------------------------------------------\n")


class ModelTest(unittest.TestCase):
    """Base class for testing Certifai Prediction Service Examples. Each example will typically include multiple
    scenarios where:

        1) a flask server is launched as a background process (via the Certifai Model SDK)
        2) a Certifai Scan is launched (or just a plain Python script) is launched in the foreground that calls (1)

    Each process that is launched in the foreground, (2), is expected to complete with a 0 exit code. Each process
    launched in the background (1) are expected to be run until explicitly killed.

    The following functions should cover scenarios that run plain Python Scripts::

        run_standalone_python_script(python_script)
        run_python_app_test(model_app, python_script)

    The following functions should cover scenarios that involve running a Certifai Scan::

        run_model_and_definition_test('app_dtree.py', 'my-definition.yaml')
        run_model_and_scan('app_dtree.py', 'my-definition.yaml')
        run_model_and_explain('app_dtree.py', 'my-definition.yaml', fast=True)
    """
    SLEEP_TIME = 5        # 5 seconds
    TERMINATION_TIME = 5  # 5 seconds
    DEFAULT_TEST_TIMEOUT = 2 * 60                     # 2 minutes
    DEFAULT_SCAN_TIMEOUT = 60 * 60 * 1                # 1 hour
    PRECALCULATE_TIMEOUT = DEFAULT_SCAN_TIMEOUT * 3   # 3 hours
    bg = None

    def _run_in_foreground(self, command: Sequence[str], timeout: Optional[int] = None):
        try:
            # Run process and wait until it completes
            process = subprocess.run(command, shell=False, capture_output=True, timeout=timeout, text=True)
            process.check_returncode()
        except subprocess.TimeoutExpired as te:
            error = f"\nProcess did not finish within expected time (command={te.cmd}, timeout={te.timeout} seconds). Error: {str(te)}"
            capture_err_and_out(te.stderr, te.stdout)
            self.fail(error)
        except subprocess.CalledProcessError as ce:
            error = f"\nProcess finished with non-zero exit code (command={ce.cmd}, code={ce.returncode}). Error: {str(ce)}"
            capture_err_and_out(ce.stderr, ce.stdout)
            self.fail(error)

    @contextlib.contextmanager
    def _run_in_background(self, command: Sequence[str]):
        with tempfile.NamedTemporaryFile(mode='w+') as stdout, tempfile.NamedTemporaryFile(mode='w+') as stderr:
            try:
                p = subprocess.Popen(command, shell=False, stdout=stdout, stderr=stderr, stdin=subprocess.DEVNULL,
                                     close_fds=True, text=True)
                yield
            except Exception:
                # WARNING: Killing the subprocess may not kill any workers spawned by the process (e.g. gunicorn!)
                p.kill()
                p.wait()
                capture_output(stdout.name, stderr.name)
                raise
            finally:
                # WARNING: Killing the subprocess may not kill any workers spawned by the process (e.g. gunicorn!)
                p.kill()
                p.wait()

    # Outward facing API

    def run_python_app_test(self, model_app: str, test_script: str):
        # Run a Python Model (flask app) in the background, give it a couple seconds to start up, before running test
        with self._run_in_background(["python", model_app]):
            time.sleep(self.SLEEP_TIME)
            self._run_in_foreground(["python", test_script], timeout=self.DEFAULT_TEST_TIMEOUT)

    def run_standalone_python_script(self, script: str):
        # Run the standalone test script
        self._run_in_foreground(["python", script], timeout=self.DEFAULT_SCAN_TIMEOUT)

    def run_model_and_definition_test(self, model_app: str, definition: str):
        # Run a Python Model (flask app) in the background, give it a couple seconds to start up, before running test
        with self._run_in_background(["python", model_app]):
            time.sleep(self.SLEEP_TIME)
            self._run_in_foreground(["certifai", "definition-test", "-f", definition], timeout=self.DEFAULT_SCAN_TIMEOUT)

    def run_model_and_scan(self, model_app: str, definition: str):
        # Run a Python Model (flask app) in the background, give it a couple seconds to start up, before running test
        with self._run_in_background(f"python {model_app}".split()):
            time.sleep(self.SLEEP_TIME)
            self._run_in_foreground(["certifai", "scan", "-f", definition], timeout=self.DEFAULT_SCAN_TIMEOUT)

    def run_model_and_explain(self, model_app: str, definition: str, fast: bool = False):
        # Run a Python Model (flask app) in the background, give it a couple seconds to start up.
        with self._run_in_background(f"python {model_app}".split()):
            time.sleep(self.SLEEP_TIME)
            if fast:
                # Run the precalculate step prior to the fast explain
                pre_calc_command = ["certifai", "explain", "-f", definition, "--precalculate"]
                self._run_in_foreground(pre_calc_command, timeout=self.PRECALCULATE_TIMEOUT)
                command = ["certifai", "explain", "-f", definition, "--fast"]
            else:
                command = ["certifai", "explain", "-f", definition]
            # Run the explanation scan
            self._run_in_foreground(command, timeout=self.DEFAULT_SCAN_TIMEOUT)

