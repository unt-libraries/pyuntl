from pyuntl.etd_ms_structure import ETD_MSElement, ETD_MS, ETD_MSTitle, \
    ETD_MS_StructureException, contributor_director, description_director, \
    date_director, identifier_director, subject_director
from pyuntl.untldoc import untlpy2etd_ms, untldict2py
from tests import UNTL_DICT
import unittest


class TestETD(unittest.TestCase):

    def testETDfromUNTL(self):
        '''confirm that the etd object conversion works'''
        etd = untlpy2etd_ms(untldict2py(UNTL_DICT))
        self.assertEqual(type(etd), ETD_MS)

    def testCreateETDElement(self):
        """Test to make sure ETD elements can be created and content filled"""

        etd = ETD_MSElement(content='test test test')
        self.assertEqual(etd.content, 'test test test')

    def testAddChildToETDMS(self):
        '''test ability to add child to etd element'''

        etd = ETD_MS(content='proud parent')
        etd_child = ETD_MSTitle(content='cantakerous child')
        etd.add_child(etd_child)
        self.assertTrue('title' in etd.contained_children)

    def testAddBadChildToETDMS(self):
        '''test inability to add bad child to etd element'''

        etd = ETD_MSTitle(content='title parent')
        etd_bad_child = ETD_MSTitle(content='incompatible child')
        self.assertRaises(ETD_MS_StructureException, etd.add_child,
                          etd_bad_child)

    def testContributorDirector(self):
        '''tests contributor expansion'''

        etd = contributor_director(qualifier='jrr')
        self.assertEqual(etd.qualifier, 'jrr')
        self.assertEqual(etd.tag, 'contributor')

    def testDescriptionDirector(self):
        '''tests description expansion'''

        etd = description_director(qualifier='content')
        self.assertEqual(etd.tag, 'description')

    def testDateDirector(self):
        '''tests date expansion'''

        etd = date_director(qualifier='creation', content='2222-11-01')
        self.assertEqual(etd.tag, 'date')

    def testIdentifierDirector(self):
        '''tests identifier expansion'''

        etd = identifier_director(ark='ark:/67531/metadc271729')
        self.assertEqual(etd.tag, 'identifier')
        self.assertEqual(etd.content, 'http://digital.library.unt.edu/' +
                         'ark:/67531/metadc271729')

    def testSubjectDirector(self):
        '''tests subject expansion'''

        etd = subject_director(qualifier='schemey')
        self.assertEqual(etd.tag, 'subject')


def suite():
    test_suite = unittest.makeSuite(TestETD, 'test')
    return test_suite

if __name__ == '__main__':
    unittest.main()
