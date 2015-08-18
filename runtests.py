#!/usr/bin/env python
import unittest
from tests import record, etd, field, reader, writer, pyuntl_test, dublincore, \
    highwire

def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(record.suite())
    test_suite.addTest(field.suite())
    test_suite.addTest(etd.suite())
    test_suite.addTest(highwire.suite())
    test_suite.addTest(reader.suite())
    test_suite.addTest(writer.suite())
    test_suite.addTest(pyuntl_test.suite())
    test_suite.addTest(dublincore.suite())
    return test_suite

runner = unittest.TextTestRunner()
runner.run(suite())
