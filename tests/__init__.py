import unittest
import tests.efsc.test_efsc_tools

def efst_test_suite():

    loader = unittest.TestLoader()
    efst_test_suite = unittest.TestSuite()

    # load tests from the efsc package
    efsc_tools_suite = loader.loadTestsFromModule(tests.efsc.test_efsc_tools)


    efst_test_suite.addTests(efsc_tools_suite)

    return efst_test_suite
