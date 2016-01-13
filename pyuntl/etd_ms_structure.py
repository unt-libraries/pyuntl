from pyuntl import ETD_MS_ORDER


DEGREE_ORDER = [
    'name',
    'level',
    'discipline',
    'grantor',
]

# Namespaces for the DC XML.
ETD_MS_NAMESPACES = {
    'xsi': 'http://www.ndltd.org/standards/metadata/etdms/1.0/etdms.xsd/',
    None: 'http://www.ndltd.org/standards/metadata/etdms/1.0/',
}

ETD_MS_CONTRIBUTOR_EXPANSION = {
    'ths': 'advisor',
    'cmr': 'committee member',
    'cha': 'chair',
    'jrr': 'juror',
}


class ETD_MS_StructureException(Exception):
    """Base exception for the ETD_MS Python structure."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return '%s' % (self.value,)


class ETD_MSElement(object):
    """A class for containing ETD MS elements."""

    def __init__(self, **kwargs):
        """Set all the defaults if inheriting class hasn't
        defined them.
        """
        content = kwargs.get('content', None)
        # Set the element's content.
        self.content = getattr(self, 'content', content)
        # Get list of allowed child elements.
        self.contained_children = getattr(self, 'contained_children', [])
        # Get list of child elements.
        self.children = getattr(self, 'children', [])
        # Get the qualifier.
        self.qualifier = kwargs.get('qualifier', None)

    def add_child(self, child):
        """Add a child object to the current one.

        Checks the contained_children list to make sure that the object
        is allowable, and throws an exception if not.
        """
        # Make sure the child exists before adding it.
        if child:
            # Add the child if it is allowed to exist under the parent.
            if child.tag in self.contained_children:
                self.children.append(child)
            else:
                raise ETD_MS_StructureException(
                    'Invalid child "%s" for parent "%s"' %
                    (child.tag, self.tag)
                )

    def get_child_content(self, children, element_name):
        """Get the requested element content from a list of children."""
        # Loop through the children and get the specified element.
        for child in children:
            # If the child is the requested element, return its content.
            if child.tag == element_name:
                return child.content
        return ''


class ETD_MS(ETD_MSElement):
    def __init__(self, **kwargs):
        self.tag = 'thesis'
        self.contained_children = ETD_MS_ORDER
        super(ETD_MS, self).__init__(**kwargs)


class ETD_MSTitle(ETD_MSElement):
    def __init__(self, **kwargs):
        self.tag = 'title'
        self.content = kwargs.get('content')
        super(ETD_MSTitle, self).__init__(**kwargs)


class ETD_MSCreator(ETD_MSElement):
    def __init__(self, **kwargs):
        self.tag = 'creator'
        children = kwargs.get('children', [])
        self.content = self.get_child_content(children, 'name')
        super(ETD_MSCreator, self).__init__(**kwargs)


class ETD_MSSubject(ETD_MSElement):
    def __init__(self, **kwargs):
        self.tag = 'subject'
        if kwargs.get('scheme'):
            self.scheme = kwargs.get('scheme')
        super(ETD_MSSubject, self).__init__(**kwargs)


class ETD_MSDescription(ETD_MSElement):
    def __init__(self, **kwargs):
        self.tag = 'description'
        super(ETD_MSDescription, self).__init__(**kwargs)


class ETD_MSPublisher(ETD_MSElement):
    def __init__(self, **kwargs):
        self.tag = 'publisher'
        children = kwargs.get('children', [])
        self.content = self.get_child_content(children, 'name')
        super(ETD_MSPublisher, self).__init__(**kwargs)


class ETD_MSContributor(ETD_MSElement):
    def __init__(self, **kwargs):
        self.tag = 'contributor'
        self.role = kwargs.get('role')
        children = kwargs.get('children', [])
        self.content = self.get_child_content(children, 'name')
        super(ETD_MSContributor, self).__init__(**kwargs)


class ETD_MSDate(ETD_MSElement):
    def __init__(self, **kwargs):
        self.tag = 'date'
        super(ETD_MSDate, self).__init__(**kwargs)


class ETD_MSType(ETD_MSElement):
    def __init__(self, **kwargs):
        self.tag = 'type'
        super(ETD_MSType, self).__init__(**kwargs)


class ETD_MSFormat(ETD_MSElement):
    def __init__(self, **kwargs):
        self.tag = 'format'
        super(ETD_MSFormat, self).__init__(**kwargs)


class ETD_MSIdentifier(ETD_MSElement):
    def __init__(self, **kwargs):
        self.tag = 'identifier'
        super(ETD_MSIdentifier, self).__init__(**kwargs)


class ETD_MSLanguage(ETD_MSElement):
    def __init__(self, **kwargs):
        self.tag = 'language'
        super(ETD_MSLanguage, self).__init__(**kwargs)


class ETD_MSCoverage(ETD_MSElement):
    def __init__(self, **kwargs):
        self.tag = 'coverage'
        super(ETD_MSCoverage, self).__init__(**kwargs)


class ETD_MSRights(ETD_MSElement):
    def __init__(self, **kwargs):
        self.tag = 'rights'
        super(ETD_MSRights, self).__init__(**kwargs)


class ETD_MSDegree(ETD_MSElement):
    def __init__(self, **kwargs):
        self.tag = 'degree'
        self.allows_content = False
        self.contained_children = [
            'name',
            'level',
            'discipline',
            'grantor',
        ]
        super(ETD_MSDegree, self).__init__(**kwargs)


class ETD_MSDegreeName(ETD_MSElement):
    def __init__(self, **kwargs):
        self.tag = 'name'
        super(ETD_MSDegreeName, self).__init__(**kwargs)


class ETD_MSDegreeLevel(ETD_MSElement):
    def __init__(self, **kwargs):
        self.tag = 'level'
        super(ETD_MSDegreeLevel, self).__init__(**kwargs)


class ETD_MSDegreeDiscipline(ETD_MSElement):
    def __init__(self, **kwargs):
        self.tag = 'discipline'
        super(ETD_MSDegreeDiscipline, self).__init__(**kwargs)


class ETD_MSDegreeGrantor(ETD_MSElement):
    def __init__(self, **kwargs):
        self.tag = 'grantor'
        super(ETD_MSDegreeGrantor, self).__init__(**kwargs)


def contributor_director(**kwargs):
    """Define the expanded qualifier name."""
    if kwargs.get('qualifier') in ETD_MS_CONTRIBUTOR_EXPANSION:
        # Return the element object.
        return ETD_MSContributor(
            role=ETD_MS_CONTRIBUTOR_EXPANSION[kwargs.get('qualifier')],
            **kwargs
        )
    else:
        return None


def description_director(**kwargs):
    """Direct which class should be used based on the description
    qualifier.
    """
    if kwargs.get('qualifier') == 'content':
        # Return the element object.
        return ETD_MSDescription(content=kwargs.get('content'))
    else:
        return None


def date_director(**kwargs):
    """Direct which class should be used based on the date qualifier
    or if the date should be converted at all.
    """
    # If the date is a creation date, return the element object.
    if kwargs.get('qualifier') == 'creation':
        return ETD_MSDate(content=kwargs.get('content').strip())
    elif kwargs.get('qualifier') != 'digitized':
        # Return the element object.
        return ETD_MSDate(content=kwargs.get('content').strip())
    else:
        return None


def identifier_director(**kwargs):
    """Direct how to handle the identifier element."""
    ark = kwargs.get('ark', None)
    qualifier = kwargs.get('qualifier', None)
    content = kwargs.get('content', '')

    # See if the ark and domain name were given.
    if ark:
        content = 'http://digital.library.unt.edu/%s' % ark
    elif qualifier:
        content = '%s: %s' % (qualifier, content)
    return ETD_MSIdentifier(content=content)


def subject_director(**kwargs):
    """Direct how to handle a subject element."""
    if kwargs.get('qualifier') not in ['KWD', '']:
        return ETD_MSSubject(scheme=kwargs.get('qualifier'), **kwargs)
    else:
        return ETD_MSSubject(content=kwargs.get('content'))

ETD_MS_CONVERSION_DISPATCH = {
    'thesis': ETD_MS,
    'title': ETD_MSTitle,
    'coverage': ETD_MSCoverage,
    'creator': ETD_MSCreator,
    'date': date_director,
    'description': description_director,
    'language': ETD_MSLanguage,
    'publisher': ETD_MSPublisher,
    'subject': subject_director,
    'resourceType': ETD_MSType,
    'identifier': identifier_director,
    'contributor': contributor_director,
    'rights': ETD_MSRights,
    'degree': ETD_MSDegree,
}

ETD_MS_DEGREE_DISPATCH = {
    'name': ETD_MSDegreeName,
    'level': ETD_MSDegreeLevel,
    'discipline': ETD_MSDegreeDiscipline,
    'grantor': ETD_MSDegreeGrantor,
}
