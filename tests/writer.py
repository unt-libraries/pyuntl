import unittest
import os
import xml.etree.ElementTree as ET
from pyuntl.untldoc import untlxml2py

class WriterTest(unittest.TestCase):

    def setUp(self):
        self.well_formed_record = untlxml2py(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                'metadc_complete.untl.xml',
            )
        )

    def test_write_xml_file_from_pyuntl(self):
        self.well_formed_record.create_xml_file("/tmp/xml_test_output.xml")
        self.written_record = ET.parse("/tmp/xml_test_output.xml")
        self.well_formed_record = ET.parse(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                'metadc_complete.untl.xml'
            )
        )
        # get canonical version of xml files
        cxml1 = self.well_formed_record
        cxml2 = self.written_record
        # compare the two xmls
        self.assertTrue(
            # string output of root of initial xml
            ET.tostring(cxml1.getroot()) == \
            # string output of root generated xml
            ET.tostring(cxml2.getroot())
        )

    def tearDown(self):
        os.remove("/tmp/xml_test_output.xml")

def suite():
    test_suite = unittest.makeSuite(WriterTest, 'test')
    return test_suite

if __name__ == '__main__':
    unittest.main()
