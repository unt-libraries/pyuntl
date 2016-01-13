import re


# Ordered list of UNTL elements
UNTL_XML_ORDER = [
    'title',
    'creator',
    'contributor',
    'publisher',
    'date',
    'language',
    'description',
    'subject',
    'primarySource',
    'coverage',
    'source',
    'citation',
    'relation',
    'collection',
    'institution',
    'rights',
    'resourceType',
    'format',
    'identifier',
    'degree',
    'note',
    'meta',
]

UNTL_PTH_ORDER = [
    'hidden',
    'title',
    'creator',
    'contributor',
    'publisher',
    'date',
    'language',
    'description',
    'subject',
    'primarySource',
    'coverage',
    'source',
    'citation',
    'relation',
    'collection',
    'institution',
    'rights',
    'resourceType',
    'format',
    'identifier',
    'degree',
    'note',
    'meta',
]

DC_ORDER = [
    'title',
    'creator',
    'contributor',
    'publisher',
    'date',
    'language',
    'description',
    'subject',
    'coverage',
    'source',
    'relation',
    'rights',
    'type',
    'format',
    'identifier',
]

ETD_MS_ORDER = [
    'title',
    'creator',
    'subject',
    'description',
    'publisher',
    'contributor',
    'date',
    'type',
    'identifier',
    'language',
    'coverage',
    'rights',
    'degree',
]

HIGHWIRE_ORDER = [
    'citation_title',
    'citation_author',
    'citation_publisher',
    'citation_publication_date',
    'citation_online_date',
    'citation_journal_title',
    'citation_conference_title',
    'citation_issn',
    'citation_isbn',
    'citation_doi',
    'citation_volume',
    'citation_issue',
    'citation_firstpage',
    'citation_lastpage',
    'citation_dissertation_insitution',
    'citation_technical_report_insitution',
    'citation_technical_report_number',
]

# Namespaces for the UNTL xml
UNTL_NAMESPACES = {
    'untl': 'http://digitalprojects.library.unt.edu/'
}

# All Vocabularies Location
VOCABULARIES_URL = 'http://digital2.library.unt.edu/vocabularies/all/'

# URL of the UNTL metadata usage page
UNTL_USAGE_LINK = 'http://www.library.unt.edu/digital-projects-unit/'

# Creation Year/Month/Day regexes
CREATION_DATE_REGEX = re.compile(
    r'^(\d\d\d\d)[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])$'
)

CREATION_MONTH_REGEX = re.compile(r'^(\d\d\d\d)[- /.](0[1-9]|1[012])$')

CREATION_YEAR_REGEX = re.compile(r'(\d\d\d\d)')

META_CREATION_DATE_REGEX = re.compile(
    r'(\d\d\d\d)[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])'
)
