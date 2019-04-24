import pickle
import os
import io
import unittest

from pyuntl import UNTL_XML_ORDER
from pyuntl.quality import determine_completeness
from pyuntl.metadata_generator import pydict2xmlstring
from pyuntl.untldoc import (untldict2py, py2dict, untlxml2py, post2pydict,
                            find_untl_errors, add_empty_fields)
from tests import (UNTL_DICT, BAD_UNTL_DICT, IGNORE_POST_LIST,
                   EXPECTED_POST_TO_PYDICT)


class TestUNTLDictionaryToPythonObject(unittest.TestCase):
    def setUp(self):
        """Set up the initial data."""
        self.root_element = untldict2py(UNTL_DICT)

    def testPost2PyDict(self):
        """Test HTTP request to Python object."""
        rff = open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                'post.pkl'),
                   'rb')
        post = pickle.load(rff)
        rff.close()
        untl_dict = post2pydict(post, IGNORE_POST_LIST)
        self.assertEqual(untl_dict, EXPECTED_POST_TO_PYDICT)

    def testCompleteness(self):
        """Test completeness."""
        pyuntl = untldict2py(UNTL_DICT)
        completeness = determine_completeness(pyuntl)
        self.assertEqual(completeness, 1.0)

    def testIncompleteness(self):
        """Test incompleteness."""
        bad_pyuntl = untldict2py(BAD_UNTL_DICT)
        incompleteness = determine_completeness(bad_pyuntl)
        self.assertTrue(incompleteness < 0.02)

    def testFixErrors(self):
        """Test finding UNTL errors."""
        found = find_untl_errors(BAD_UNTL_DICT.copy(), fix_errors=True)
        self.assertTrue(len(found['error_dict']) > 0)

    def testAddEmptyFields(self):
        """Test adding the empty fields."""
        fixed = add_empty_fields(BAD_UNTL_DICT.copy())
        for x in UNTL_XML_ORDER:
            self.assertTrue(x in fixed, '%s not in %s' % (x, fixed))

    def testCreatesPublisher(self):
        """Test to make sure the the publisher's children are added."""
        for element in self.root_element.children:
            if element.tag == 'publisher':
                self.assertNotEqual(len(element.children), 0)

    def testCreatesDescription(self):
        """Test description with content and not children."""
        for element in self.root_element.children:
            if element.tag == 'description' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesLanguage(self):
        """Test language element with content and not children."""
        for element in self.root_element.children:
            if element.tag == 'language' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesResourceType(self):
        """Test ResourceType element with content and not children."""
        for element in self.root_element.children:
            if element.tag == 'resourceType' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesFormat(self):
        """Test format element with content and not children."""
        for element in self.root_element.children:
            if element.tag == 'format' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesTitle(self):
        """Test title element with content and not children."""
        for element in self.root_element.children:
            if element.tag == 'title' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesCollection(self):
        """Test collection element with content and not children."""
        for element in self.root_element.children:
            if element.tag == 'collection' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesNote(self):
        """Test note element with content and not children."""
        for element in self.root_element.children:
            if element.tag == 'note' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesMeta(self):
        """Test meta element with content and not children."""
        for element in self.root_element.children:
            if element.tag == 'meta' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesCoverage(self):
        """Test coverage element with content and not children."""
        for element in self.root_element.children:
            if element.tag == 'coverage' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesDate(self):
        """Test date element with content and not children."""
        for element in self.root_element.children:
            if element.tag == 'date' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesIdentifier(self):
        """Test identifier element with content and not children."""
        for element in self.root_element.children:
            if element.tag == 'identifier' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesPrimarySource(self):
        """Test primarySource element with content and not children."""
        for element in self.root_element.children:
            if element.tag == 'primarySource' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesInstitution(self):
        """Test institution element with content and not children."""
        for element in self.root_element.children:
            if element.tag == 'institution' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesSubject(self):
        """Test subject element with content and not children."""
        for element in self.root_element.children:
            if element.tag == 'subject' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesCreator(self):
        """Test creator element with content and not children."""
        for element in self.root_element.children:
            if element.tag == 'creator':
                self.assertNotEqual(len(element.children), 0)

    def testCircularEquality(self):
        self.assertEqual(
            py2dict(untlxml2py(io.StringIO(
                    pydict2xmlstring(UNTL_DICT)))), UNTL_DICT)


def suite():
    test_suite = unittest.makeSuite(TestUNTLDictionaryToPythonObject, 'test')
    return test_suite


if __name__ == '__main__':
    unittest.main()
