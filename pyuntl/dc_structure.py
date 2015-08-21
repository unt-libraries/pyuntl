import string
from pyuntl import DC_ORDER

XSI = 'http://www.w3.org/2001/XMLSchema-instance'

# Namespaces for the DC xml
DC_NAMESPACES = {
    'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'xsi': XSI,
}

VOCAB_INDEX = {
    'coverage': {
        'timePeriod': 'coverage-eras',
    },
    'format': {
        'None': 'formats',
    },
    'language': 'languages',
    'type': 'resource-types',
    'rights': {
        'access': 'rights-access',
        'license': 'rights-licenses',
    },
}


class DC_StructureException(Exception):
    """Base exception for the DC python structure"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "%s" % (self.value,)


class DCElement(object):
    """A class for containing DC elements"""
    def __init__(self, **kwargs):
        """Set all the defaults if inheriting class hasn't defined them"""
        content = kwargs.get('content', None)
        vocab_data = kwargs.get('vocab_data', None)
        # Set the elements content
        self.content = getattr(self, 'content', content)
        # list of allowed child elements
        self.contained_children = getattr(self, 'contained_children', [])
        # list of child elements
        self.children = getattr(self, 'children', [])
        # Get the qualifier
        qualifier = kwargs.get('qualifier', None)
        # Determine the vocab from the qualifier
        self.content_vocab = self.determine_vocab(qualifier)
        # If the value needs to be resolved by accessing the vocabularies
        if kwargs.get('resolve_values', False) and self.content_vocab and \
                vocab_data:
            self.content = self.resolver(vocab_data, 'label')
        elif kwargs.get('resolve_urls', False) and self.content_vocab and \
                vocab_data:
            self.content = self.resolver(vocab_data, 'url')

    def add_child(self, child):
        """This adds a child object to the current one.  It will check the
        contained_children list to make sure that the object is allowable, and
        throw an exception if not"""
        # Make sure the child exists before adding it
        if child:
            # If the child is allowed to exist under the parent
            if child.tag in self.contained_children:
                self.children.append(child)
            else:
                raise DC_StructureException(
                    "Invalid child \"%s\" for parent \"%s\"" %
                    (child.tag, self.tag)
                )

    def get_child_content(self, children, element_name):
        """Gets the requested element content from a list of children"""
        # Loop through the children and get the specified element
        for child in children:
            # if the child is the requested element
            if child.tag == element_name:
                return child.content
        return ''

    def determine_vocab(self, qualifier):
        """Determine the vocab from the qualifier"""
        vocab_value = VOCAB_INDEX.get(self.tag, None)
        # If the vocab index returns a dictionary
        if isinstance(vocab_value, dict):
            # Change a None qualifier into a string
            if qualifier is None:
                qualifier = 'None'
            # Find the value based on the qualifier
            return vocab_value.get(qualifier, None)
        elif vocab_value is not None:
            return vocab_value
        else:
            return None

    def resolver(self, vocab_data, attribute):
        """
        Pulls the requested attribute based on the given vocabulary and content
        """
        term_list = vocab_data.get(self.content_vocab, [])
        # Loop through the terms from the vocabulary
        for term_dict in term_list:
            # Match the name to the current content
            if term_dict['name'] == self.content:
                return term_dict[attribute]
        return self.content


class DC(DCElement):
    def __init__(self, **kwargs):
        self.tag = 'dc'
        self.contained_children = DC_ORDER
        super(DC, self).__init__(**kwargs)


class DCCoverage(DCElement):
    def __init__(self, **kwargs):
        self.tag = 'coverage'
        super(DCCoverage, self).__init__(**kwargs)


class DCCreator(DCElement):
    def __init__(self, **kwargs):
        self.tag = 'creator'
        children = kwargs.get('children', [])
        self.content = self.get_child_content(children, 'name')
        super(DCCreator, self).__init__(**kwargs)


class DCDate(DCElement):
    def __init__(self, **kwargs):
        self.tag = 'date'
        super(DCDate, self).__init__(**kwargs)


class DCDescription(DCElement):
    def __init__(self, **kwargs):
        self.tag = 'description'
        super(DCDescription, self).__init__(**kwargs)


class DCFormat(DCElement):
    def __init__(self, **kwargs):
        self.tag = 'format'
        super(DCFormat, self).__init__(**kwargs)


class DCLanguage(DCElement):
    def __init__(self, **kwargs):
        self.tag = 'language'
        super(DCLanguage, self).__init__(**kwargs)


class DCPublisher(DCElement):
    def __init__(self, **kwargs):
        self.tag = 'publisher'
        children = kwargs.get('children', [])
        self.content = self.get_child_content(children, 'name')
        super(DCPublisher, self).__init__(**kwargs)


class DCSubject(DCElement):
    def __init__(self, **kwargs):
        self.tag = 'subject'
        super(DCSubject, self).__init__(**kwargs)


class DCTitle(DCElement):
    def __init__(self, **kwargs):
        self.tag = 'title'
        super(DCTitle, self).__init__(**kwargs)


class DCType(DCElement):
    def __init__(self, **kwargs):
        self.tag = 'type'
        super(DCType, self).__init__(**kwargs)


class DCIdentifier(DCElement):
    def __init__(self, **kwargs):
        self.tag = 'identifier'
        super(DCIdentifier, self).__init__(**kwargs)


class DCContributor(DCElement):
    def __init__(self, **kwargs):
        self.tag = 'contributor'
        children = kwargs.get('children', [])
        self.content = self.get_child_content(children, 'name')
        super(DCContributor, self).__init__(**kwargs)


class DCSource(DCElement):
    def __init__(self, **kwargs):
        self.tag = 'source'
        super(DCSource, self).__init__(**kwargs)


class DCRelation(DCElement):
    def __init__(self, **kwargs):
        self.tag = 'relation'
        super(DCRelation, self).__init__(**kwargs)


class DCRights(DCElement):
    def __init__(self, **kwargs):
        self.tag = 'rights'
        super(DCRights, self).__init__(**kwargs)


def description_director(**kwargs):
    """Directs which class should be used based the directors qualifier"""
    description_type = {'physical': DCFormat}
    qualifier = kwargs.get('qualifier')
    # Determine the type of element needed, based on the qualifier
    element_class = description_type.get(qualifier, DCDescription)
    # Create the element object of that element type
    element = element_class(
        qualifier=qualifier,
        content=kwargs.get('content'),
    )
    return element


def date_director(**kwargs):
    """Directs which class should be used based on the date qualifier
        or if the date should be converted at all
    """
    # If the date is a creation date
    if kwargs.get('qualifier') == 'creation':
        # return the element object
        return DCDate(content=kwargs.get('content'))
    # Otherwise return nothing
    else:
        return None


def identifier_director(**kwargs):
    """Directs how to handle the identifier element"""
    ark = kwargs.get('ark', None)
    domain_name = kwargs.get('domain_name', None)
    qualifier = kwargs.get('qualifier', None)
    content = kwargs.get('content', '')
    # See if the ark and domain name were given
    if ark and qualifier == 'ark':
        content = "ark: %s" % ark
    if domain_name and ark and qualifier == 'permalink':
        # Create the permalink URL
        if not domain_name.endswith('/'):
            domain_name += '/'
        permalink_url = 'http://' + domain_name + ark
        # Make sure it has a trailing slash
        if not permalink_url.endswith('/'):
            permalink_url += '/'
        content = permalink_url
    else:
        if qualifier:
            content = "%s: %s" % (string.lower(qualifier), content)
    return DCIdentifier(content=content)

DC_CONVERSION_DISPATCH = {
    'dc': DC,
    'coverage': DCCoverage,
    'creator': DCCreator,
    'date': date_director,
    'description': description_director,
    'format': DCFormat,
    'language': DCLanguage,
    'publisher': DCPublisher,
    'subject': DCSubject,
    'title': DCTitle,
    'resourceType': DCType,
    'identifier': identifier_director,
    'contributor': DCContributor,
    'source': DCSource,
    'relation': DCRelation,
    'rights': DCRights,
}
