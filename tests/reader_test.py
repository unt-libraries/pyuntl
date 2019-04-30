import unittest
from pyuntl.untldoc import untldict2py, untlxml2py
from tests import UNTL_DICT
from io import BytesIO
import os
from pyuntl.untl_structure import Metadata


class ReaderTest(unittest.TestCase):
    """Tests that read in a number of UNTL formats and expect no errors.

    Tests fail unless the root elements are an instance of Metadata.
    """

    def test_create_pyuntl_from_dict(self):
        self.root_element = untldict2py(UNTL_DICT)
        self.assertTrue(isinstance(self.root_element, Metadata))

    def test_create_pyuntl_from_xml_file(self):
        self.root_element = untlxml2py(
            os.path.join(os.path.dirname(os.path.realpath(__file__)),
                         'metadc_complete.untl.xml')
        )
        self.assertTrue(isinstance(self.root_element, Metadata))

    def test_create_pyuntl_from_xml_string(self):
        self.root_element = untlxml2py(
            BytesIO(
                open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                  'metadc_complete.untl.xml'), 'r').read().encode()
            )
        )
        self.assertTrue(isinstance(self.root_element, Metadata))

    def test_empty_record(self):
        self.root_element = untlxml2py(
            os.path.join(os.path.dirname(os.path.realpath(__file__)),
                         'metadc_empty.untl.xml')
        )
        self.assertTrue(isinstance(self.root_element, Metadata))

    def test_blank_description_record(self):
        self.root_element = untlxml2py(
            os.path.join(os.path.dirname(os.path.realpath(__file__)),
                         'metadc_blank_description.untl.xml')
        )
        self.assertTrue(isinstance(self.root_element, Metadata))

    def test_legacy_defaults_record(self):
        self.root_element = untlxml2py(
            os.path.join(os.path.dirname(os.path.realpath(__file__)),
                         'metadc_legacy_defaults.untl.xml')
        )
        self.assertTrue(isinstance(self.root_element, Metadata))


def suite():
    test_suite = unittest.makeSuite(ReaderTest, 'test')
    return test_suite


if __name__ == '__main__':
    unittest.main()
