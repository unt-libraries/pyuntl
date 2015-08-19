import cPickle
import StringIO
import unittest
import os
from pyuntl.untldoc import untldict2py, py2dict, untlxml2py, post2pydict, \
    find_untl_errors, add_empty_fields
from pyuntl.quality import determine_completeness
from pyuntl.metadata_generator import pydict2xmlstring
from tests import UNTL_DICT, BAD_UNTL_DICT, IGNORE_POST_LIST, \
    EXPECTED_POST_TO_PYDICT
from pyuntl import UNTL_XML_ORDER


class TestUNTLDictionaryToPythonObject(unittest.TestCase):
    def setUp(self):
        """ Used to setup the initial data """
        self.root_element = untldict2py(UNTL_DICT)

    def testPost2PyDict(self):
        '''test http request to python object'''
        rff = open(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                'post.pkl'
            ), 'rb'
        )
        post = cPickle.load(rff)
        rff.close()
        untl_dict = post2pydict(post, IGNORE_POST_LIST)
        self.assertEqual(untl_dict, EXPECTED_POST_TO_PYDICT)

    def testCompleteness(self):
        '''completeness test'''
        pyuntl = untldict2py(UNTL_DICT)
        completeness = determine_completeness(pyuntl)
        self.assertEqual(completeness, 1.0)

    def testIncompleteness(self):
        '''incompleteness test'''
        bad_pyuntl = untldict2py(BAD_UNTL_DICT)
        incompleteness = determine_completeness(bad_pyuntl)
        self.assertTrue(incompleteness < 0.02)

    def testFixErrors(self):
        '''test find untl errors'''
        found = find_untl_errors(BAD_UNTL_DICT.copy(), fix_errors=True)
        self.assertTrue(len(found['error_dict']) > 0)

    def testAddEmptyFields(self):
        '''does it really add the empty fields? lets test.'''
        fixed = add_empty_fields(BAD_UNTL_DICT.copy())
        for x in UNTL_XML_ORDER:
            self.assertTrue(x in fixed, '%s not in %s' % (x, fixed))

    def testCreatesPublisher(self):
        """Test to make sure the the publisher's children are added"""
        for element in self.root_element.children:
            if element.tag == 'publisher':
                self.assertNotEqual(len(element.children), 0)

    def testCreatesDescription(self):
        """test description with content and not children"""
        for element in self.root_element.children:
            if element.tag == 'description' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesLanguage(self):
        """test language element with content and not children"""
        for element in self.root_element.children:
            if element.tag == 'language' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesResourceType(self):
        """test ResourceType element with content and not children"""
        for element in self.root_element.children:
            if element.tag == 'resourceType' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesFormat(self):
        """test format element with content and not children"""
        for element in self.root_element.children:
            if element.tag == 'format' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesTitle(self):
        """test title element with content and not children"""
        for element in self.root_element.children:
            if element.tag == 'title' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesCollection(self):
        """test collection element with content and not children"""
        for element in self.root_element.children:
            if element.tag == 'collection' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesNote(self):
        """test note element with content and not children"""
        for element in self.root_element.children:
            if element.tag == 'note' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesMeta(self):
        """test meta element with content and not children"""
        for element in self.root_element.children:
            if element.tag == 'meta' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesCoverage(self):
        """test coverage element with content and not children"""
        for element in self.root_element.children:
            if element.tag == 'coverage' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesDate(self):
        """test date element with content and not children"""
        for element in self.root_element.children:
            if element.tag == 'date' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesIdentifier(self):
        """test identifier element with content and not children"""
        for element in self.root_element.children:
            if element.tag == 'identifier' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesPrimarySource(self):
        """test primarysource element with content and not children"""
        for element in self.root_element.children:
            if element.tag == 'primarySource' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesInstitution(self):
        """test institution element with content and not children"""
        for element in self.root_element.children:
            if element.tag == 'institution' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesSubject(self):
        """test subject element with content and not children"""
        for element in self.root_element.children:
            if element.tag == 'subject' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesCreator(self):
        """test creator element with content and not children"""
        for element in self.root_element.children:
            if element.tag == 'creator':
                self.assertNotEqual(len(element.children), 0)

    def testCircularEquality(self):
        self.assertEqual(
            py2dict(untlxml2py(StringIO.StringIO(
                    pydict2xmlstring(UNTL_DICT)))), UNTL_DICT)


def suite():
    test_suite = unittest.makeSuite(TestUNTLDictionaryToPythonObject, 'test')
    return test_suite

if __name__ == '__main__':
    unittest.main()
