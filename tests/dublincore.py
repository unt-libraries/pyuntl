import unittest
from rdflib import ConjunctiveGraph
from pyuntl.untldoc import untldict2py, py2dict, untlxml2py, untlpy2dcpy, \
    untlpydict2dcformatteddict, generate_dc_xml, generate_dc_json, \
    generate_dc_txt, dcdict2rdfpy
from pyuntl.metadata_generator import pydict2xmlstring
from tests import UNTL_DICT, DUBLIN_CORE_XML
from pyuntl.dc_structure import DC
import StringIO
try:
    # the json module was included in the stdlib in python 2.6
    # http://docs.python.org/library/json.html
    import json
except ImportError:
    # simplejson 2.0.9 is available for python 2.4+
    # http://pypi.python.org/pypi/simplejson/2.0.9
    # simplejson 1.7.3 is available for python 2.3+
    # http://pypi.python.org/pypi/simplejson/1.7.3
    import simplejson as json


class DublinCoreTest(unittest.TestCase):
    def setUp(self):
        """ Used to setup the initial data """
        self.root_element = untlpy2dcpy(untldict2py(UNTL_DICT))

    def testDCJSON(self):
        '''test output and re-jsoning of json export'''
        dcjson = generate_dc_json(UNTL_DICT.copy())
        j = json.loads(dcjson)
        self.assertTrue(type(j), dict)
        for key, value in j.items():
            self.assertTrue(key in UNTL_DICT, '%s not in %s' % (key, UNTL_DICT))

    def testDCtoRDF(self):
        '''test dublin core to RDF function'''
        rdf = dcdict2rdfpy(UNTL_DICT)
        self.assertEqual(type(rdf), ConjunctiveGraph)

    def testDCText(self):
        '''test that we can generate a dc text'''
        dctext = generate_dc_txt(UNTL_DICT)
        self.assertEqual(type(dctext), str)

    def testDCxml(self):
        '''render valid dublin core xml test'''
        dxml = generate_dc_xml(UNTL_DICT)
        self.assertEqual(dxml.strip(), DUBLIN_CORE_XML.strip())

    def testDCFormattedDict(self):
        '''make sure we can format to dc dict properly'''
        # make the dictionary
        dcd = untlpydict2dcformatteddict(UNTL_DICT)
        # workaround to make usable in python 2.5
        self.assertFalse('content' in dcd['publisher'], '%s not in %s' % ('content', dcd['publisher']))
        self.assertTrue(len(dcd) < len(UNTL_DICT))

    def testConversionFromUNTLPY(self):
        '''confirms the conversion from untl py object in setup worked right'''
        self.assertTrue(type(self.root_element) is DC)

    def testDoesNotCreateContributor(self):
        """Test to make sure there is no contributor element (not in dublin)"""
        for element in self.root_element.children:
            self.assertNotEqual(element.tag, 'contributor')

    def testCreatesSource(self):
        """Test to make sure the the source's children are added"""
        for element in self.root_element.children:
            if element.tag == 'source':
                self.assertNotEqual(len(element.children), 0)

    def testCreatesRelation(self):
        """Test to make sure the the relation's children are added"""
        for element in self.root_element.children:
            if element.tag == 'relation':
                self.assertNotEqual(len(element.children), 0)

    def testCreatesRights(self):
        """Test to make sure the the rights's children are added"""
        for element in self.root_element.children:
            if element.tag == 'rights':
                self.assertNotEqual(len(element.children), 0)

    def testCreatesType(self):
        """Test to make sure the the type element is created but not populated"""
        for element in self.root_element.children:
            if element.tag == 'type':
                self.assertNotEqual(len(element.content), 0)

    def testCreatesPublisher(self):
        """Test to make sure the the publisher's children are added"""
        for element in self.root_element.children:
            if element.tag == 'publisher':
                self.assertNotEqual(len(element.content), 0)

    def testCreatesDescription(self):
        """test add description"""
        for element in self.root_element.children:
            if element.tag == 'description' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesFormat(self):
        """test add format"""
        for element in self.root_element.children:
            if element.tag == 'format' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesTitle(self):
        """test add title"""
        for element in self.root_element.children:
            if element.tag == 'title' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesCoverage(self):
        """test create coverage"""
        for element in self.root_element.children:
            if element.tag == 'coverage' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesDate(self):
        """test create date"""
        for element in self.root_element.children:
            if element.tag == 'date' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesIdentifier(self):
        """make sure identifier is added"""
        for element in self.root_element.children:
            if element.tag == 'identifier' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesSubject(self):
        """make sure subject is created"""
        for element in self.root_element.children:
            if element.tag == 'subject' and len(element.children) == 0:
                self.assertNotEqual((element.content), None)

    def testCreatesCreator(self):
        """create creator but not children"""
        for element in self.root_element.children:
            if element.tag == 'creator':
                self.assertNotEqual(len(element.content), 0)


def suite():
    test_suite = unittest.makeSuite(DublinCoreTest, 'test')
    return test_suite

if __name__ == '__main__':
    unittest.main()
