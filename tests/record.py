import unittest

from lxml.etree import _Element

from pyuntl import UNTL_PTH_ORDER
from pyuntl.untldoc import untldict2py, py2dict
from pyuntl.untl_structure import (Metadata as Record, PYUNTL_DISPATCH,
                                   UNTLStructureException, FormGenerator)
from tests import UNTL_DICT


class RecordTest(unittest.TestCase):
    def setUp(self):
        self.record = Record()

    def test_create_xml_string(self):
        field = PYUNTL_DISPATCH['title'](content=None)
        self.record.add_child(field)
        xml = self.record.create_xml_string()
        self.assertTrue(xml.strip() == ('<?xml version="1.0" encoding='
                                        '"UTF-8"?>\n<metadata>\n'
                                        '  <title/>\n</metadata>\n').strip())

    def test_field_not_found(self):
        """Test there are no children if there are no fields."""
        self.assertEquals(len(self.record.children), 0)

    def test_create_xml(self):
        """Test the XML created from a pyuntl object is of
        class _Element.
        """
        field = PYUNTL_DISPATCH['title'](content=None)
        self.record.add_child(field)
        xml = self.record.create_xml()
        self.assertTrue(isinstance(xml, _Element))

    def test_add_child(self):
        """Test field exists in the children array of the record
        upon adding it.
        """
        field = PYUNTL_DISPATCH['title'](content=None)
        self.record.add_child(field)
        self.assertTrue(field in self.record.children)

    def test_add_child_field_where_qualifier_exists_and_content_does_not(self):
        """Test a child added with a qualifier and not content
        is included in the children array.
        """
        field = PYUNTL_DISPATCH['title'](
            content=None
        )
        self.record.add_child(field)
        self.record.children[0].set_qualifier('officialtitle')
        self.assertTrue(field in self.record.children)

    def test_convert_none_content_object_to_dict_and_back(self):
        """Test for original dictionary equivalent to yielded one
        using py2dict, then dict2py, then finally back to py2dict
        on a None content.
        """
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
            missing_content_dict == {
                'title': [
                    {'content': 'fake content', 'qualifier': 'officialtitle'}
                ]
            }
        )

    def test_convert_content_no_qualifier_roundtrip(self):
        """Test adding a child without a qualifier doesn't create one
        when converting from py to dict to py.
        """
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
            py_from_dict.children[0].qualifier is None
        )

    def test_add_nonexistant_child(self):
        """Test adding a child to a field that shouldn't
        contain children raises exception.
        """
        field = PYUNTL_DISPATCH['subject']()
        self.assertRaises(UNTLStructureException,
                          lambda: field.add_child(
                              PYUNTL_DISPATCH['title'](content=None)))

    def test_add_misplaced_child(self):
        """Test adding an 'info' to a title element raises a
        UNTLStructureException because it is not an allowed child.
        """
        field = PYUNTL_DISPATCH['title'](content=None)
        self.record.add_child(field)
        self.assertRaises(UNTLStructureException,
                          lambda: self.record.children[0].add_child(
                              PYUNTL_DISPATCH['info'](content=None)))

    def test_remove_field(self):
        """Test adding a single field and then removing it leaves 0."""
        field = PYUNTL_DISPATCH['title'](content=None)
        self.record.add_child(field)
        # Try removing a field that exists.
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
        c2 = untldict2py(UNTL_DICT)
        c2.sort_untl(UNTL_PTH_ORDER)
        # Get ordered list of children tags.
        tag_list = [UNTL_PTH_ORDER.index(elem.tag) for elem in c2.children]
        # Verify order is in order of UNTL_PTH_ORDER.
        self.assertTrue(all(current <= next_ for current, next_ in zip(tag_list, tag_list[1:])))

    def test_validate(self):
        # This method was left undeveloped in pyuntl.untl_structure.
        pass

    def test_generate_form_data(self):
        """Test for an instance of a FormGenerator class."""
        self.record = untldict2py(UNTL_DICT)
        form_gen = self.record.generate_form_data(sort_order=UNTL_PTH_ORDER)
        self.assertTrue(isinstance(form_gen, FormGenerator))

    def test_complete_record(self):
        """Test each tag appears as created from the dict keys."""
        self.record = untldict2py(UNTL_DICT)
        for c in self.record.children:
            self.assertTrue(c.tag in UNTL_DICT.keys())


def suite():
    test_suite = unittest.makeSuite(RecordTest, 'test')
    return test_suite


if __name__ == '__main__':
    unittest.main()
