import unittest

from rdflib import ConjunctiveGraph
from lxml import objectify

from pyuntl.dc_structure import DC, DC_NAMESPACES
from pyuntl.untldoc import (untldict2py, untlpy2dcpy,
                            untlpydict2dcformatteddict,
                            generate_dc_xml, generate_dc_json,
                            generate_dc_txt, dcdict2rdfpy)
from tests import UNTL_DICT, DUBLIN_CORE_XML
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
        """Set up the initial data."""
        self.root_element = untlpy2dcpy(untldict2py(UNTL_DICT))

    def testDCJSON(self):
        """Test output and re-JSONing of JSON export."""
        dcjson = generate_dc_json(UNTL_DICT.copy())
        j = json.loads(dcjson)
        self.assertTrue(type(j), dict)
        for key, value in j.items():
            self.assertTrue(key in UNTL_DICT, '%s not in %s'
                            % (key, UNTL_DICT))

    def testDCtoRDF(self):
        """Test Dublin Core to RDF function."""
        rdf = dcdict2rdfpy(UNTL_DICT)
        self.assertEqual(type(rdf), ConjunctiveGraph)

    def testDCText(self):
        """Test that we can generate a dc text."""
        dctext = generate_dc_txt(UNTL_DICT)
        self.assertEqual(type(dctext), str)

    def testDCXMLRootElement(self):
        """Check the Dublin Core for expected attrib and nsmap on root."""
        generated_dxml = generate_dc_xml(UNTL_DICT)

        # Verify root element has expected attribs, nsmap, and tag.
        generated_dxml_root = objectify.fromstring(generated_dxml)

        schema_location = ('http://www.openarchives.org/OAI/2.0/oai_dc/ '
                           'http://www.openarchives.org/OAI/2.0/oai_dc.xsd')
        expected_tag = '{http://www.openarchives.org/OAI/2.0/oai_dc/}dc'

        self.assertTrue(schema_location in generated_dxml_root.attrib.values())
        self.assertEqual(generated_dxml_root.nsmap, DC_NAMESPACES)
        self.assertEqual(generated_dxml_root.tag, expected_tag)

    def testDCXMLNonRootElements(self):
        """Test for expected Dublin Core elements."""
        generated_dxml = generate_dc_xml(UNTL_DICT)

        generated_dxml_root = objectify.fromstring(generated_dxml)
        constant_dxml_root = objectify.fromstring(DUBLIN_CORE_XML)
        results = []
        # Check if each of the root's children from the generated XML
        # has a match in the string constant's XML.
        for child in generated_dxml_root.iterchildren():
            # For each child, get all of the children with the same tag
            # from the XML being compared.
            same_tag_list = constant_dxml_root.findall(child.tag)
            element_found = False
            child_children = len(child.getchildren())
            # Check if any of the possible elements are a match.
            for current in same_tag_list:
                if (current.text == child.text and
                        current.tail == child.tail and
                        current.attrib == child.attrib and
                        len(current.getchildren()) == child_children):
                    element_found = True
                    break
            results.append(element_found)
        # If all elements came up with a match. Let it be True.
        self.assertTrue(all(results))

    def testDCFormattedDict(self):
        """Verify we can format to dc dict properly."""
        # make the dictionary
        dcd = untlpydict2dcformatteddict(UNTL_DICT)
        # workaround to make usable in python 2.5
        self.assertFalse('content' in dcd['publisher'], '%s not in %s'
                         % ('content', dcd['publisher']))
        self.assertTrue(len(dcd) < len(UNTL_DICT))

    def testConversionFromUNTLPY(self):
        """Verify the conversion from untl object."""
        self.assertTrue(type(self.root_element) is DC)

    def testDoesNotCreateContributor(self):
        """Verify there is no contributor element (not in Dublin Core)."""
        for element in self.root_element.children:
            self.assertNotEqual(element.tag, 'contributor')

    def testCreatesSource(self):
        """Verify the source's children are added."""
        for element in self.root_element.children:
            if element.tag == 'source':
                self.assertNotEqual(len(element.children), 0)

    def testCreatesRelation(self):
        """Verify the relation's children are added."""
        for element in self.root_element.children:
            if element.tag == 'relation':
                self.assertNotEqual(len(element.children), 0)

    def testCreatesRights(self):
        """Verify the rights' children are added."""
        for element in self.root_element.children:
            if element.tag == 'rights':
                self.assertNotEqual(len(element.children), 0)

    def testCreatesType(self):
        """Verify the type element is created but not populated."""
        for element in self.root_element.children:
            if element.tag == 'type':
                self.assertNotEqual(len(element.content), 0)

    def testCreatesPublisher(self):
        """Verify the publisher's children are added."""
        for element in self.root_element.children:
            if element.tag == 'publisher':
                self.assertNotEqual(len(element.content), 0)

    def testCreatesDescription(self):
        """Verify the description is added."""
        for element in self.root_element.children:
            if element.tag == 'description' and len(element.children) == 0:
                self.assertTrue(element.content is not None)

    def testCreatesFormat(self):
        """Verify the format is added."""
        for element in self.root_element.children:
            if element.tag == 'format' and len(element.children) == 0:
                self.assertTrue(element.content is not None)

    def testCreatesTitle(self):
        """Verify the title is added."""
        for element in self.root_element.children:
            if element.tag == 'title' and len(element.children) == 0:
                self.assertTrue(element.content is not None)

    def testCreatesCoverage(self):
        """Verify the coverage is added."""
        for element in self.root_element.children:
            if element.tag == 'coverage' and len(element.children) == 0:
                self.assertTrue(element.content is not None)

    def testCreatesDate(self):
        """Verify the date is added."""
        for element in self.root_element.children:
            if element.tag == 'date' and len(element.children) == 0:
                self.assertTrue(element.content is not None)

    def testCreatesIdentifier(self):
        """Verify the identifier is added."""
        for element in self.root_element.children:
            if element.tag == 'identifier' and len(element.children) == 0:
                self.assertTrue(element.content is not None)

    def testCreatesSubject(self):
        """Verify the subject is created."""
        for element in self.root_element.children:
            if element.tag == 'subject' and len(element.children) == 0:
                self.assertTrue(element.content is not None)

    def testCreatesCreator(self):
        """Test the creator element."""
        for element in self.root_element.children:
            if element.tag == 'creator':
                self.assertNotEqual(len(element.content), 0)


def suite():
    test_suite = unittest.makeSuite(DublinCoreTest, 'test')
    return test_suite

if __name__ == '__main__':
    unittest.main()
