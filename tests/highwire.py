import unittest

from pyuntl.highwire_structure import (format_date_string, HighwireElement,
                                       CitationTitle, CitationAuthor,
                                       CitationPublisher,
                                       CitationPublicationDate,
                                       CitationOnlineDate, citation_director,
                                       identifier_director)
from pyuntl.untldoc import untlpy2highwirepy, untldict2py, highwirepy2dict
from tests import UNTL_DICT


class TestHighwire(unittest.TestCase):
    def testHighwire2Dict(self):
        """Test dictionary creation from Highwire."""
        untlpy = untldict2py(UNTL_DICT)
        highwi = untlpy2highwirepy(untlpy)
        hidict = highwirepy2dict(highwi)
        self.assertEqual(type(hidict), dict)

    def testUNTL2HIGHWIRE(self):
        """Test conversion from UNTL to Highwire."""
        untlpy = untldict2py(UNTL_DICT)
        highwi = untlpy2highwirepy(untlpy)
        for element in highwi:
            self.assertTrue(issubclass(type(element), HighwireElement))

    def testFormatDateString(self):
        """Test date is formatted as expected."""
        date = format_date_string(9)
        self.assertTrue(date == '09')
        date = format_date_string(90)
        self.assertTrue(date == '90')

    def testCreateHighwireElement(self):
        """Test Highwire elements can be created and content filled."""
        highwire = HighwireElement(content='test test test')
        self.assertEqual(highwire.content, 'test test test')

    def testCitationDirectorpublicationTitle(self):
        """Test CitationDirector creates proper highwire object."""
        highwire = citation_director(qualifier='publicationTitle')
        self.assertEqual(highwire.name, 'citation_journal_title')

    def testCitationDirectorvolume(self):
        """Test CitationDirector with volume creates proper
        highwire object.
        """
        highwire = citation_director(qualifier='volume')
        self.assertEqual(highwire.name, 'citation_volume')

    def testCitationDirectorpageStart(self):
        """Test CitationDirector with pageStart creates proper
        highwire object.
        """
        highwire = citation_director(qualifier='pageStart')
        self.assertEqual(highwire.name, 'citation_firstpage')

    def testCitationDirectorissue(self):
        """Test CitationDirector with issue creates proper
        highwire object.
        """
        highwire = citation_director(qualifier='issue')
        self.assertEqual(highwire.name, 'citation_issue')

    def testCitationDirectorpageEnd(self):
        """Test CitationDirector with pageEnd creates proper
        highwire object.
        """
        highwire = citation_director(qualifier='pageEnd')
        self.assertEqual(highwire.name, 'citation_lastpage')

    def testIdentifierDirectorISBN(self):
        """Test identifier expansion for ISBN."""
        highwire = identifier_director(qualifier='ISBN')
        self.assertEqual(highwire.name, 'citation_isbn')

    def testIdentifierDirectorISSN(self):
        """Test identifier expansion for ISSN."""
        highwire = identifier_director(qualifier='ISSN')
        self.assertEqual(highwire.name, 'citation_issn')

    def testIdentifierDirectorDOI(self):
        """Test identifier expansion for DOI."""
        highwire = identifier_director(qualifier='DOI')
        self.assertEqual(highwire.name, 'citation_doi')

    def testIdentifierDirectorREPNO(self):
        """Test identifier expansion for technical report number."""
        highwire = identifier_director(qualifier='REP-NO')
        self.assertEqual(highwire.name, 'citation_technical_report_number')

    def testCitationOnlineDate(self):
        """Test successful creation of online date object."""
        c = CitationOnlineDate(qualifier='this', content='that')
        self.assertEqual(c.name, 'citation_online_date')

    def testCitationPublicationDate(self):
        """Test successful creation of publication date object."""
        c = CitationPublicationDate(content='that')
        self.assertEqual(c.name, 'citation_publication_date')

    def testCitationPublisher(self):
        """Test publisher generates properly."""
        c = CitationPublisher(qualifier='that')
        self.assertEqual(c.name, 'citation_publisher')

    def testCitationAuthor(self):
        """Test author is created successfully."""
        c = CitationAuthor(qualifier='test')
        self.assertEqual(c.name, 'citation_author')

    def testCitationTitle(self):
        """Test title is created successfully."""
        c = CitationTitle(qualifier='test')
        self.assertEqual(c.name, 'citation_title')


def suite():
    test_suite = unittest.makeSuite(TestHighwire, 'test')
    return test_suite

if __name__ == '__main__':
    unittest.main()
