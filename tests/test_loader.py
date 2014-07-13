from tests.test_client import FlaskClientTestCase
import unittest

# The unittest module can be used from the command line
# to run tests from modules, classes or even individual test methods:
# python -m unittest -v tests.test_client.FlaskClientTestCase.test_home_page

suite = unittest.TestLoader().loadTestsFromTestCase(FlaskClientTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)

