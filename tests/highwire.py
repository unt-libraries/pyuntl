from pyuntl.highwire_structure import format_date_string, HighwireElement, \
    CitationTitle, CitationAuthor, CitationPublisher, CitationPublicationDate, \
    CitationOnlineDate, citation_director, identifier_director, \
    CitationOnlineDate
from pyuntl.tests import UNTL_DICT
from pyuntl.untldoc import untlpy2highwirepy, untldict2py, highwirepy2dict
import unittest

class TestHighwire(unittest.TestCase):

    def testHighwire2Dict(self):
        '''test dictionary creation from highwire'''
        untlpy = untldict2py(UNTL_DICT)
        highwi = untlpy2highwirepy(untlpy)
        hidict = highwirepy2dict(highwi)
        self.assertEqual(type(hidict), dict)

    def testUNTL2HIGHWIRE(self):
        '''can we transfer from untl to highwire'''
        untlpy = untldict2py(UNTL_DICT)
        highwi = untlpy2highwirepy(untlpy)
        for element in highwi:
            self.assertTrue(issubclass(type(element), HighwireElement))

    def testFormatDateString(self):
        """date should be returned as expected"""

        date = format_date_string(9)
        self.assertTrue(date == '09')
        date = format_date_string(90)
        self.assertTrue(date == '90')

    def testCreateHighwireElement(self):
        """Test to make sure Highwire elements can be created and content filled"""

        highwire = HighwireElement(content='test test test')
        self.assertEqual(highwire.content, 'test test test')

    def testCitationDirectorpublicationTitle(self):
        '''tests CitationDirector creates proper highwire object'''

        highwire = citation_director(qualifier='publicationTitle')
        self.assertEqual(highwire.name, 'citation_journal_title')

    def testCitationDirectorvolume(self):
        '''tests CitationDirector creates proper highwire object'''

        highwire = citation_director(qualifier='volume')
        self.assertEqual(highwire.name, 'citation_volume')

    def testCitationDirectorpageStart(self):
        '''tests CitationDirector creates proper highwire object'''

        highwire = citation_director(qualifier='pageStart')
        self.assertEqual(highwire.name, 'citation_firstpage')

    def testCitationDirectorissue(self):
        '''tests CitationDirector creates proper highwire object'''

        highwire = citation_director(qualifier='issue')
        self.assertEqual(highwire.name, 'citation_issue')

    def testCitationDirectorpageEnd(self):
        '''tests CitationDirector creates proper highwire object'''

        highwire = citation_director(qualifier='pageEnd')
        self.assertEqual(highwire.name, 'citation_lastpage')

    def testIdentifierDirectorISBN(self):
        '''tests identifier expansion'''

        highwire = identifier_director(qualifier='ISBN')
        self.assertEqual(highwire.name, 'citation_isbn')

    def testIdentifierDirectorISSN(self):
        '''tests identifier expansion'''

        highwire = identifier_director(qualifier='ISSN')
        self.assertEqual(highwire.name, 'citation_issn')

    def testIdentifierDirectorDOI(self):
        '''tests identifier expansion'''

        highwire = identifier_director(qualifier='DOI')
        self.assertEqual(highwire.name, 'citation_doi')

    def testIdentifierDirectorREPNO(self):
        '''tests identifier expansion'''

        highwire = identifier_director(qualifier='REP-NO')
        self.assertEqual(highwire.name, 'citation_technical_report_number')

    def testCitationOnlineDate(self):
        '''tests successful creation of online date object'''

        c = CitationOnlineDate(qualifier='this', content='that')
        self.assertEqual(c.name, 'citation_online_date')

    def testCitationPublicationDate(self):
        '''tests successful creation of publication object'''

        c = CitationPublicationDate(content='that')
        self.assertEqual(c.name, 'citation_publication_date')

    def testCitationPublisher(self):
        '''tests did publisher generate properly'''

        c = CitationPublisher(qualifier='that')
        self.assertEqual(c.name, 'citation_publisher')

    def testCitationAuthor(self):
        ''' tests if author can create successfully '''

        c = CitationAuthor(qualifier='test')
        self.assertEqual(c.name, 'citation_author')

    def testCitationTitle(self):
        ''' tests if title can create successfully '''

        c = CitationTitle(qualifier='test')
        self.assertEqual(c.name, 'citation_title')

def suite():
    test_suite = unittest.makeSuite(TestHighwire, 'test')
    return test_suite

if __name__ == '__main__':
    unittest.main()
