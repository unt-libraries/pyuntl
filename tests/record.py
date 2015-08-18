import unittest
from pyuntl.untldoc import untldict2py, py2dict
from tests import UNTL_DICT
from pyuntl.untl_structure import Metadata as Record
from pyuntl.untl_structure import PYUNTL_DISPATCH, UNTLStructureException, \
FormGenerator
from pyuntl import UNTL_PTH_ORDER
from lxml.etree import _Element

class RecordTest(unittest.TestCase):
    def setUp(self):
        self.record = Record()

    def test_create_xml_string(self):
        field = PYUNTL_DISPATCH['title'](content=None)
        self.record.add_child(field)
        xml = self.record.create_xml_string()
        self.assertTrue(
            xml.strip() == '<?xml version="1.0" encoding="UTF-8"?>\n<metadata>\n  <title/>\n</metadata>\n'.strip()
        )

    def test_field_not_found(self):
        '''
        If there are no fields, then the children amount should be zero
        '''
        self.assertEquals(len(self.record.children), 0)

    def test_create_xml(self):
        '''
        the xml created from a pyuntl object should be of class _Element
        '''
        field = PYUNTL_DISPATCH['title'](content=None)
        self.record.add_child(field)
        xml = self.record.create_xml()
        self.assertTrue(isinstance(xml, _Element))

    def test_add_child(self):
        '''
        a field should exist in the children array of the record upon adding it
        '''
        field = PYUNTL_DISPATCH['title'](content=None)
        self.record.add_child(field)
        self.assertTrue(field in self.record.children)

    def test_add_child_field_where_qualifier_exists_and_content_does_not(self):
        '''
        we should be able to add a child that has a qualifier and not content
        it passes the test if it is included in the children array
        '''
        field = PYUNTL_DISPATCH['title'](
            content=None
        )
        self.record.add_child(field)
        self.record.children[0].set_qualifier('officialtitle')
        self.assertTrue(field in self.record.children)

    def test_convert_none_content_object_to_dict_and_back(self):
        '''
        using py2dict, then dict2py, finally back to py2dict on a none content
        object should yield an equivilent dictionary as the original one.
        '''
        field = PYUNTL_DISPATCH['title'](
            content=None
        )
        self.record.add_child(field)
        self.record.children[0].set_qualifier('officialtitle')
        missing_content_dict = py2dict(self.record)
        self.assertTrue(missing_content_dict == {'title': []})
        py_from_dict = untldict2py(missing_content_dict)
        self.assertTrue(
            self.record.children[0].qualifier != py_from_dict.qualifier
        )
        self.record.children[0].content = 'fake content'
        missing_content_dict = py2dict(self.record)
        self.assertTrue(
            missing_content_dict == \
            {
                'title': [
                    {'content': 'fake content', 'qualifier': 'officialtitle'}
                ]
            }
        )

    def test_convert_content_no_qualifier_roundtrip(self):
        '''
        if we add a child without a qualifier, make sure it doesn't create one
        if we send it on a 'round trip' py > dict > py
        '''
        field = PYUNTL_DISPATCH['title'](
            content='Tie Till the Title'
        )
        self.record.add_child(field)
        content_dict = py2dict(self.record)
        self.assertTrue(
            content_dict == {'title': [{'content': 'Tie Till the Title'}]}
        )
        py_from_dict = untldict2py(content_dict)
        self.assertTrue(
            py_from_dict.children[0].qualifier == None
        )

    def test_add_nonexistant_child(self):
        '''
        should raise a KeyError because we never added a field by that name
        '''
        self.assertRaises(KeyError, lambda: self.record.add_child(PYUNTL_DISPATCH['geolocation'](content=None)))

    def test_add_misplaced_child(self):
        '''
        should raise a UNTLStructureException because titles cant have infos
        '''
        field = PYUNTL_DISPATCH['title'](content=None)
        self.record.add_child(field)
        self.assertRaises(UNTLStructureException, lambda:
            self.record.children[0].add_child(
                PYUNTL_DISPATCH['info'](content=None)
            )
        )

    def test_remove_field(self):
        '''
        adding a single field and then removing it should leave us with 0
        '''
        field = PYUNTL_DISPATCH['title'](content=None)
        self.record.add_child(field)
        # try removing a field that exists
        del self.record.children[0]
        self.assertEqual(len(self.record.children), 0)

    def test_completeness(self):
        field = PYUNTL_DISPATCH['title'](content=None)
        self.record.add_child(field)
        self.assertEquals(self.record.completeness, 0.0)

    def test_record_length(self):
        field = PYUNTL_DISPATCH['title'](content=None)
        self.record.add_child(field)
        self.assertEquals(self.record.record_length, 13)

    def test_record_content_length(self):
        field = PYUNTL_DISPATCH['title'](content='fake title')
        self.record.add_child(field)
        field = PYUNTL_DISPATCH['meta'](content=None)
        self.record.add_child(field)
        self.assertEquals(self.record.record_content_length, 38)

    def test_create_element_dict(self):
        field = PYUNTL_DISPATCH['title'](content='fake title')
        self.record.add_child(field)
        field = PYUNTL_DISPATCH['meta'](content=None)
        self.record.add_child(field)
        d1 = py2dict(self.record)
        d2 = {'meta': [], 'title': [{'content': 'fake title'}]}
        self.assertTrue(d1 == d2)

    def test_sort_untl(self):
        c1 = untldict2py(UNTL_DICT)
        c2 = untldict2py(UNTL_DICT)
        c2.sort_untl(UNTL_PTH_ORDER)
        # make sure the sort of the children elements changes
        self.assertTrue(
            c1.children[0].tag != c2.children[0].tag and \
            c2.children[0].tag == 'title' and \
            c1.children[0].tag == 'publisher'
        )

    def test_validate(self):
        # this method was left undeveloped in pyuntl untl_structure
        pass

    def test_generate_form_data(self):
        '''
        We are expecting a instance of a FormGenerator class
        '''
        self.record = untldict2py(UNTL_DICT)
        form_gen = self.record.generate_form_data(sort_order=UNTL_PTH_ORDER)
        self.assertTrue(isinstance(form_gen, FormGenerator))

    def test_complete_record(self):
        '''
        we want to make sure each tag appears as created from the dict keys
        '''
        self.record = untldict2py(UNTL_DICT)
        for c in self.record.children:
            self.assertTrue(c.tag in UNTL_DICT.keys())

def suite():
    test_suite = unittest.makeSuite(RecordTest, 'test')
    return test_suite

if __name__ == '__main__':
    unittest.main()
