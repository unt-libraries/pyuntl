import unittest
from pyuntl.untl_structure import PYUNTL_DISPATCH, UNTLStructureException
from tests import UNNORMALIZED_DICT, NORMALIZED_DICT, UNNORMALIZED_UNTLBS, \
    UNNORMALIZED_LCSH, NORMALIZED_UNTLBS, NORMALIZED_LCSH
from pyuntl.util import untldict_normalizer, normalize_UNTL, normalize_LCSH


class FieldTest(unittest.TestCase):

    def setUp(self):
        self.field = PYUNTL_DISPATCH['title'](content=None)

    def test_quick_access(self):
        self.assertEqual(self.field.tag, 'title')

    def test_set_qualifier(self):
        self.field.set_qualifier('test')
        self.assertEqual(self.field.qualifier, 'test')

    def test_set_qualifier_wrong_element(self):
        self.field = PYUNTL_DISPATCH['collection'](content=None)
        self.assertRaises(UNTLStructureException,
                          lambda: self.field.set_qualifier('test'))

    def test_set_content(self):
        self.field.set_content('test')
        self.assertEqual(self.field.content, 'test')

    def test_add_unspecified_attribute(self):
        self.field.name = 'Donald Ronald'
        self.assertTrue(self.field.name)

    def test_add_content_non_ascii(self):
        self.field.set_content('test \xc2')
        self.assertEqual(self.field.content, 'test \xc2')

    def test_add_content_removes_leading_trailing_space(self):
        self.field.set_content('   test   ')
        self.assertEqual(self.field.content, 'test')

    def test_qualifier_removes_trailing_space(self):
        self.field.set_qualifier('test ')
        self.assertEqual(self.field.qualifier, 'test')

    def testLCSHFieldNormalization(self, lcsh_content=UNNORMALIZED_LCSH,
                                   normalized_content=NORMALIZED_LCSH):
        """Tests normalizing an LCSH string"""
        norm = normalize_LCSH(lcsh_content)
        self.assertEqual(norm, normalized_content)

    def testUNTLBSFieldNormalization(self, untlbs_content=UNNORMALIZED_UNTLBS,
                                     normalized_content=NORMALIZED_UNTLBS):
        """Tests normalizing a UNTL-BS string"""
        norm = normalize_UNTL(untlbs_content)
        self.assertEqual(norm, normalized_content)

    def testSingleNormalization(self, untl_dict=UNNORMALIZED_DICT,
                                normalized_dict=NORMALIZED_DICT):
        """Test normalizing LCSH untl data"""
        normalize_required = {
            'subject': ['LCSH'],
            }
        norm = untldict_normalizer(untl_dict, normalize_required)
        self.assertEqual(norm, normalized_dict)

    def testAllNormalizations(self, untl_dict=UNNORMALIZED_DICT,
                              normalized_dict=NORMALIZED_DICT):
        """Tests all the normalizations for untl"""
        normalize_required = {
            'subject': ['LCSH', 'UNTL-BS'],
            }
        norm = untldict_normalizer(untl_dict, normalize_required)
        self.assertEqual(norm, normalized_dict)


def suite():
    test_suite = unittest.makeSuite(FieldTest, 'test')
    return test_suite

if __name__ == '__main__':
    unittest.main()
