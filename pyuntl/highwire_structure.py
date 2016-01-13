import cgi
import datetime

from pyuntl import (CREATION_DATE_REGEX, CREATION_MONTH_REGEX,
                    CREATION_YEAR_REGEX, META_CREATION_DATE_REGEX)


def format_date_string(date_value):
    """Get the month string from the date."""
    # Handle single digit month value.
    if date_value < 10:
        return '0%s' % (date_value)
    else:
        return str(date_value)


class HighwireElement(object):
    """A class for containing DC elements."""

    def __init__(self, **kwargs):
        """Set all the defaults if inheriting class hasn't defined them."""
        self.tag = 'meta'
        content = kwargs.get('content', None)
        self.qualifier = kwargs.get('qualifier', None)
        # Set the element's content.
        self.content = getattr(self, 'content', content)
        escape = kwargs.get('escape', False)
        # Escape the content if needed.
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
        """Get the title content."""
        pass


class CitationAuthor(HighwireElement):
    def __init__(self, **kwargs):
        self.name = 'citation_author'
        self.content = self.get_author(**kwargs)
        super(CitationAuthor, self).__init__(**kwargs)

    def get_author(self, **kwargs):
        """Determine the authors from the creator field."""
        qualifier = kwargs.get('qualifier', '')
        children = kwargs.get('children', [])
        creator_type_per = False
        author_name = None
        # Find the creator type in children.
        for child in children:
            if child.tag == 'type' and child.content == 'per':
                creator_type_per = True
            # Get the author name.
            elif child.tag == 'name':
                author_name = child.content
        if qualifier == 'aut' and creator_type_per and author_name:
            return author_name

        return None


class CitationPublisher(HighwireElement):
    def __init__(self, **kwargs):
        self.name = 'citation_publisher'
        self.content = self.get_publisher_name(**kwargs)
        super(CitationPublisher, self).__init__(**kwargs)

    def get_publisher_name(self, **kwargs):
        """Get the publisher name."""
        children = kwargs.get('children', [])
        # Find the creator type in children.
        for child in children:
            if child.tag == 'name':
                return child.content
        return None


class CitationPublicationDate(HighwireElement):
    def __init__(self, **kwargs):
        self.name = 'citation_publication_date'
        self.content = self.get_publication_date(**kwargs)
        super(CitationPublicationDate, self).__init__(**kwargs)

    def get_publication_date(self, **kwargs):
        """Determine the creation date for the publication date."""
        date_string = kwargs.get('content', '')
        date_match = CREATION_DATE_REGEX.match(date_string)
        month_match = CREATION_MONTH_REGEX.match(date_string)
        year_match = CREATION_YEAR_REGEX.match(date_string)
        # Check if a date match exists.
        if date_match:
            (year, month, day) = date_match.groups('')
            # Create the date.
            try:
                creation_date = datetime.date(int(year), int(month), int(day))
            except ValueError:
                return None
            else:
                return '%s/%s/%s' % (
                    format_date_string(creation_date.month),
                    format_date_string(creation_date.day),
                    creation_date.year,
                )
        elif month_match:
            (year, month) = month_match.groups('')
            # Create the date.
            try:
                creation_date = datetime.date(int(year), int(month), 1)
            except ValueError:
                return None
            else:
                return '%s/%s' % (
                    format_date_string(creation_date.month),
                    creation_date.year,
                )
        elif year_match:
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
        """Get the online date from the meta creation date."""
        qualifier = kwargs.get('qualifier', '')
        content = kwargs.get('content', '')
        # Handle meta-creation-date element.
        if qualifier == 'metadataCreationDate':
            date_match = META_CREATION_DATE_REGEX.match(content)
            (year, month, day) = date_match.groups('')
            # Create the date.
            creation_date = datetime.date(int(year), int(month), int(day))
            return '%s/%s/%s' % (
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
        """Get the dissertation institution."""
        qualifier = kwargs.get('qualifier', '')
        content = kwargs.get('content', '')
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
    """Direct the citation elements based on their qualifier."""
    qualifier = kwargs.get('qualifier', '')
    content = kwargs.get('content', '')
    if qualifier == 'publicationTitle':
        return CitationJournalTitle(content=content)
    elif qualifier == 'volume':
        return CitationVolume(content=content)
    elif qualifier == 'issue':
        return CitationIssue(content=content)
    elif qualifier == 'pageStart':
        return CitationFirstpage(content=content)
    elif qualifier == 'pageEnd':
        return CitationLastpage(content=content)
    else:
        return None


def identifier_director(**kwargs):
    """Direct the identifier elements based on their qualifier."""
    qualifier = kwargs.get('qualifier', '')
    content = kwargs.get('content', '')
    if qualifier == 'ISBN':
        return CitationISBN(content=content)
    elif qualifier == 'ISSN':
        return CitationISSN(content=content)
    elif qualifier == 'DOI':
        return CitationDOI(content=content)
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
