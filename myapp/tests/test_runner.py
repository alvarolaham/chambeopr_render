"""
This is test_runner.py
"""

import unittest

from colorama import Fore, Style, init
from django.test.runner import DiscoverRunner
from tabulate import tabulate

# Initialize colorama
init(autoreset=True)


class ColoredTextTestResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.successes = 0
        self.failures_count = 0
        self.errors_count = 0
        self.skips_count = 0

    def addSuccess(self, test):
        super().addSuccess(test)
        self.successes += 1
        self.stream.write(
            Fore.GREEN + Style.BRIGHT + " 🎉  SUCCESS: " + str(test) + "\n"
        )

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.failures_count += 1
        self.stream.write(
            Fore.RED + Style.BRIGHT + " ☹️  FAILURE: " + str(test) + "\n"
        )

    def addError(self, test, err):
        super().addError(test, err)
        self.errors_count += 1
        self.stream.write(
            Fore.RED + Style.BRIGHT + " ☹️  ERROR: " + str(test) + "\n"
        )

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.skips_count += 1
        self.stream.write(
            Fore.YELLOW + Style.BRIGHT + " ⏩  SKIPPED: " + str(test) + "\n"
        )

    def print_summary(self):
        total_tests = self.testsRun
        table_data = [
            ["Total Tests", total_tests],
            ["Successes", Fore.GREEN + str(self.successes) + Style.RESET_ALL],
            [
                "Failures",
                Fore.RED + str(self.failures_count) + Style.RESET_ALL,
            ],
            ["Errors", Fore.RED + str(self.errors_count) + Style.RESET_ALL],
            ["Skips", Fore.YELLOW + str(self.skips_count) + Style.RESET_ALL],
        ]
        summary = tabulate(
            table_data, headers=["Test Result", "Count"], tablefmt="pretty"
        )
        self.stream.write("\n" + summary + "\n")


class ColoredTextTestRunner(unittest.TextTestRunner):
    resultclass = ColoredTextTestResult

    def run(self, test):
        result = super().run(test)
        result.print_summary()
        return result


class PostgresTestRunner(DiscoverRunner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serialize = kwargs.get("serialize", True)

    def setup_databases(self, **kwargs):
        old_config = super().setup_databases(**kwargs)
        return old_config

    def teardown_databases(self, old_config, **kwargs):
        super().teardown_databases(old_config, **kwargs)

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        old_config = self.setup_databases()
        suite = self.build_suite(test_labels, extra_tests)
        result = ColoredTextTestRunner(verbosity=self.verbosity).run(suite)
        self.teardown_databases(old_config, verbosity=self.verbosity)
        return self.suite_result(suite, result)

    def build_suite(self, test_labels=None, extra_tests=None):
        suite = unittest.TestSuite()
        if test_labels:
            for label in test_labels:
                tests = self.test_loader.loadTestsFromName(label)
                suite.addTests(tests)
        else:
            suite = super().build_suite(test_labels)

        if extra_tests:
            suite.addTests(extra_tests)

        return suite
