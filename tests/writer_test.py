import os
import xml.etree.ElementTree as ET

import pytest

from pyuntl.untldoc import untlxml2py


@pytest.mark.parametrize('original_file', ['metadc_complete.untl.xml',
                                           'metadc_utf8.untl.xml'])
def test_write_xml_file_from_pyuntl_is_identical(original_file, tmpdir):
    # Load data from XML file into a UNTLElement tree.
    original_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                 original_file)
    well_formed_record = untlxml2py(original_path)
    # Write the loaded data back to a new XML file.
    new_path = os.path.join(tmpdir, 'xml_test_output.xml')
    well_formed_record.create_xml_file(new_path)
    # Read back the new file and original files into ElementTrees.
    new_record = ET.parse(new_path)
    well_formed_record = ET.parse(original_path)

    # Compare initial XML to generated XML.
    assert ET.tostring(well_formed_record.getroot()) == ET.tostring(new_record.getroot())
    with open(original_path) as original_f, open(new_path) as new_f:
        assert original_f.read() == new_f.read()


def test_write_xml_file_from_pyuntl_ascii_is_now_utf8(tmpdir):
    """Show XML character references are written back as UTF-8.

    Files with XML character references inserted by `xmlcharrefreplace` when
    characters could not be encoded properly are now encoded in UTF-8.
    For example, 'dram&#225;ticas' read in is now written out 'dramáticas'.
    """
    # Load data from XML file into a UNTLElement tree.
    ascii_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                              'metadc_ascii.untl.xml')
    ascii_record = untlxml2py(ascii_path)
    # Write the loaded data back to a new XML file.
    new_path = os.path.join(tmpdir, 'xml_test_output.xml')
    ascii_record.create_xml_file(new_path)
    # Read back the new file and original files into ElementTrees.
    new_record = ET.parse(new_path)
    ascii_record = ET.parse(ascii_path)

    # Compare initial XML to generated XML.
    assert ET.tostring(ascii_record.getroot()) == ET.tostring(new_record.getroot())
    with open(ascii_path) as ascii_f, open(new_path) as new_f:
        ascii_text = ascii_f.read()
        new_text = new_f.read()
        assert 'dram&#225;ticas' in ascii_text
        assert 'dram&#225;ticas' not in new_text
        assert 'dramáticas' not in ascii_text
        assert 'dramáticas' in new_text
