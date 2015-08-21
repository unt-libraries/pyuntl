import datetime
import cgi
from pyuntl import CREATION_DATE_REGEX, CREATION_MONTH_REGEX, \
    CREATION_YEAR_REGEX, META_CREATION_DATE_REGEX


def format_date_string(date_value):
    """Gets the month string from the date"""
    # if the month value is a single digit number
    if date_value < 10:
        return "0%s" % (date_value)
    else:
        return str(date_value)


class HighwireElement(object):
    """A class for containing DC elements"""
    def __init__(self, **kwargs):
        """Set all the defaults if inheriting class hasn't defined them"""
        self.tag = 'meta'
        content = kwargs.get('content', None)
        self.qualifier = kwargs.get('qualifier', None)
        # Set the elements content
        self.content = getattr(self, 'content', content)
        escape = kwargs.get('escape', False)
        # if the content needs to be escaped
        if escape and self.content:
            self.content = cgi.escape(
                self.content,
                1
            ).encode('ascii', 'xmlcharrefreplace')


class CitationTitle(HighwireElement):
    def __init__(self, **kwargs):
        self.name = 'citation_title'
        super(CitationTitle, self).__init__(**kwargs)

    def get_content(self):
        """Gets the title content"""
        pass


class CitationAuthor(HighwireElement):
    def __init__(self, **kwargs):
        self.name = 'citation_author'
        self.content = self.get_author(**kwargs)
        super(CitationAuthor, self).__init__(**kwargs)

    def get_author(self, **kwargs):
        """Determine the authors from the creator field"""
        qualifier = kwargs.get('qualifier', '')
        children = kwargs.get('children', [])
        creator_type_per = False
        author_name = None
        # find the creator type in children
        for child in children:
            # if the child tag is type, and the type is per
            if child.tag == 'type' and child.content == 'per':
                creator_type_per = True
            # Get the author name
            elif child.tag == 'name':
                author_name = child.content
        # if qualifer is aut and the type = per
        if qualifier == 'aut' and creator_type_per and author_name:
            return author_name

        return None


class CitationPublisher(HighwireElement):
    def __init__(self, **kwargs):
        self.name = 'citation_publisher'
        self.content = self.get_publisher_name(**kwargs)
        super(CitationPublisher, self).__init__(**kwargs)

    def get_publisher_name(self, **kwargs):
        """Get the publisher name"""
        children = kwargs.get('children', [])
        # find the creator type in children
        for child in children:
            # if the child tag is type, and the type is per
            if child.tag == 'name':
                return child.content
        return None


class CitationPublicationDate(HighwireElement):
    def __init__(self, **kwargs):
        self.name = 'citation_publication_date'
        self.content = self.get_publication_date(**kwargs)
        super(CitationPublicationDate, self).__init__(**kwargs)

    def get_publication_date(self, **kwargs):
        """Determine the creation date for the publication date"""
        date_string = kwargs.get('content', '')
        # Match the date value
        date_match = CREATION_DATE_REGEX.match(date_string)
        # Match the month value
        month_match = CREATION_MONTH_REGEX.match(date_string)
        # Match the year value
        year_match = CREATION_YEAR_REGEX.match(date_string)
        # check if a date match exists
        if date_match:
            # Get the values from the groups
            (year, month, day) = date_match.groups('')
            # Create the date
            try:
                creation_date = datetime.date(int(year), int(month), int(day))
            except ValueError:
                return None
            else:
                return "%s/%s/%s" % (
                    format_date_string(creation_date.month),
                    format_date_string(creation_date.day),
                    creation_date.year,
                )
        # check if a month match exists
        elif month_match:
            # Get the values from the groups
            (year, month) = month_match.groups('')
            # Create the date
            try:
                creation_date = datetime.date(int(year), int(month), 1)
            except ValueError:
                return None
            else:
                return "%s/%s" % (
                    format_date_string(creation_date.month),
                    creation_date.year,
                )
        # check if a year match exists
        elif year_match:
            # Get the values from the groups
            year = year_match.groups('')[0]
            return year
        else:
            return None


class CitationOnlineDate(HighwireElement):
    def __init__(self, **kwargs):
        self.name = 'citation_online_date'
        self.content = self.get_online_date(**kwargs)
        super(CitationOnlineDate, self).__init__(**kwargs)

    def get_online_date(self, **kwargs):
        """Get the online date from the meta creation date"""
        qualifier = kwargs.get('qualifier', '')
        content = kwargs.get('content', '')
        # if it is a meta-creation-date element
        if qualifier == 'metadataCreationDate':
            # Match the date value
            date_match = META_CREATION_DATE_REGEX.match(content)
            # Get the values from the groups
            (year, month, day) = date_match.groups('')
            # Create the date
            creation_date = datetime.date(int(year), int(month), int(day))
            return "%s/%s/%s" % (
                format_date_string(creation_date.month),
                format_date_string(creation_date.day),
                creation_date.year,
            )
        return None


class CitationJournalTitle(HighwireElement):
    def __init__(self, **kwargs):
        self.name = 'citation_journal_title'
        super(CitationJournalTitle, self).__init__(**kwargs)


class CitationConferenceTitle(HighwireElement):
    def __init__(self, **kwargs):
        self.name = 'citation_conference_title'
        super(CitationConferenceTitle, self).__init__(**kwargs)


class CitationISSN(HighwireElement):
    def __init__(self, **kwargs):
        self.name = 'citation_issn'
        super(CitationISSN, self).__init__(**kwargs)


class CitationISBN(HighwireElement):
    def __init__(self, **kwargs):
        self.name = 'citation_isbn'
        super(CitationISBN, self).__init__(**kwargs)


class CitationDOI(HighwireElement):
    def __init__(self, **kwargs):
        self.name = 'citation_doi'
        super(CitationDOI, self).__init__(**kwargs)


class CitationVolume(HighwireElement):
    def __init__(self, **kwargs):
        self.name = 'citation_volume'
        super(CitationVolume, self).__init__(**kwargs)


class CitationIssue(HighwireElement):
    def __init__(self, **kwargs):
        self.name = 'citation_issue'
        super(CitationIssue, self).__init__(**kwargs)


class CitationFirstpage(HighwireElement):
    def __init__(self, **kwargs):
        self.name = 'citation_firstpage'
        super(CitationFirstpage, self).__init__(**kwargs)


class CitationLastpage(HighwireElement):
    def __init__(self, **kwargs):
        self.name = 'citation_lastpage'
        super(CitationLastpage, self).__init__(**kwargs)


class CitationDissertationInstitution(HighwireElement):
    def __init__(self, **kwargs):
        self.name = 'citation_dissertation_insitution'
        self.content = self.get_institution(**kwargs)
        super(CitationDissertationInstitution, self).__init__(**kwargs)

    def get_institution(self, **kwargs):
        """Get the dissertation institution"""
        qualifier = kwargs.get('qualifier', '')
        content = kwargs.get('content', '')
        # if it is a grantor element
        if qualifier == 'grantor':
            return content
        return None


class CitationTechnicalReportInstitution(HighwireElement):
    def __init__(self, **kwargs):
        self.name = 'citation_technical_report_insitution'
        super(CitationTechnicalReportInstitution, self).__init__(**kwargs)


class CitationTechnicalReportNumber(HighwireElement):
    def __init__(self, **kwargs):
        self.name = 'citation_technical_report_number'
        super(CitationTechnicalReportNumber, self).__init__(**kwargs)


def citation_director(**kwargs):
    """Directs the citation elements based on their qualifier"""
    qualifier = kwargs.get('qualifier', '')
    content = kwargs.get('content', '')
    # if it is a journal title element
    if qualifier == 'publicationTitle':
        return CitationJournalTitle(content=content)
    # if it is a volume element
    elif qualifier == 'volume':
        return CitationVolume(content=content)
    # if it is a issue element
    elif qualifier == 'issue':
        return CitationIssue(content=content)
    # if it is a first page element
    elif qualifier == 'pageStart':
        return CitationFirstpage(content=content)
    # if it is a last page element
    elif qualifier == 'pageEnd':
        return CitationLastpage(content=content)
    else:
        return None


def identifier_director(**kwargs):
    """Directs the identifier elements based on their qualifier"""
    qualifier = kwargs.get('qualifier', '')
    content = kwargs.get('content', '')
    # if it is a ISBN element
    if qualifier == 'ISBN':
        return CitationISBN(content=content)
    # if it is a ISSN element
    elif qualifier == 'ISSN':
        return CitationISSN(content=content)
    # if it is a DOI element
    elif qualifier == 'DOI':
        return CitationDOI(content=content)
    # if it is a report number element
    elif qualifier == 'REP-NO':
        return CitationTechnicalReportNumber(content=content)
    else:
        return None

HIGHWIRE_CONVERSION_DISPATCH = {
    'title': CitationTitle,
    'creator': CitationAuthor,
    'publisher': CitationPublisher,
    'date': CitationPublicationDate,
    'meta': CitationOnlineDate,
    'citation': citation_director,
    'identifier': identifier_director,
    'degree': CitationDissertationInstitution,
}
