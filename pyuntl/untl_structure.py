import urllib2
import socket
from metadata_generator import py2dict
from lxml.etree import Element, SubElement, tostring
from pyuntl import UNTL_XML_ORDER, VOCABULARIES_URL
from pyuntl.quality import determine_completeness
from pyuntl.form_logic import UNTL_FORM_DISPATCH, UNTL_GROUP_DISPATCH


class UNTLStructureException(Exception):
    """Base exception for the UNTL python structure"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "%s" % (self.value,)


def create_untl_xml_subelement(parent, element, prefix=""):
    """Helper element for the creation of untl xml files"""
    subelement = SubElement(parent, prefix + element.tag)
    if element.content is not None:
        subelement.text = element.content
    if element.qualifier is not None:
        subelement.attrib["qualifier"] = element.qualifier
    if element.children > 0:
        for child in element.children:
            SubElement(subelement, prefix + child.tag).text = child.content
    else:
        subelement.text = element.content

    return subelement


def add_missing_children(required_children, element_children):
        """Determine if there are elements not in the children
            that need to be included as blank elements in the form
        """
        element_tags = [element.tag for element in element_children]
        # Loop through the elements that should be in the form
        for contained_element in required_children:
            # if the element doesn't exist in the form
            if contained_element not in element_tags:
                # Add the element to the children
                try:
                    added_child = PYUNTL_DISPATCH[contained_element](
                        content=""
                    )
                except:
                    added_child = PYUNTL_DISPATCH[contained_element]()
                element_children.append(added_child)
        return element_children


class UNTLElement(object):
    """A class for containing UNTL elements"""

    def __init__(self, **kwargs):
        # Set all the defaults if inheriting class hasn't defined them
        # set the element's tag to None if it isn't defined
        self.tag = getattr(self, 'tag', None)
        # list of allowed child elements
        self.contained_children = getattr(self, 'contained_children', [])
        # by default, objects have textual content
        self.allows_content = getattr(self, 'allows_content', True)
        # by default, objects have qualifiers
        self.allows_qualifier = getattr(self, 'allows_qualifier', True)
        # element qualier, None by default
        self.qualifier = getattr(self, 'qualifier', None)
        # child element wrappers go here
        self.children = []
        # textual content, if any
        self.content = None

        # Set the content, if it exists, and if it's allowed
        arg_content = kwargs.get('content', None)
        if arg_content is not None:
            self.set_content(arg_content)
        # Set the qualifier, if it exists, and if it's allowed
        arg_qualifier = kwargs.get('qualifier', None)
        if arg_qualifier is not None:
            self.set_qualifier(arg_qualifier)

    def set_qualifier(self, value):
        """This sets the qualifier for the element.  It checks to make
        sure that the element is allowed to have a qualifier and throws an
        exception if not"""
        if self.allows_qualifier:
            self.qualifier = value.strip()
        else:
            raise UNTLStructureException(
                "Element \"%s\" does not allow a qualifier" % (self.tag,)
            )

    def add_child(self, child):
        """This adds a child object to the current one.  It will check the
        contained_children list to make sure that the object is allowable, and
        throw an exception if not"""
        if child.tag in self.contained_children:
            self.children.append(child)
        else:
            raise UNTLStructureException(
                "Invalid child \"%s\" for parent \"%s\"" % (
                    child.tag,
                    self.tag
                )
            )

    def set_content(self, content):
        """This sets textual content for the object/node.  It checks to make
        sure that the node is allowed to contain content and throws an
        exception if not"""
        if self.allows_content:
            self.content = content.strip()
        else:
            raise UNTLStructureException(
                "Element \"%s\" does not allow textual content" % (self.tag,)
            )

    def add_form(self, **kwargs):
        """ Adds the form attribute to the untl python object """
        vocabularies = kwargs.get('vocabularies', None)
        qualifier = kwargs.get('qualifier', None)
        content = kwargs.get('content', None)
        parent_tag = kwargs.get('parent_tag', None)
        superuser = kwargs.get('superuser', False)
        # if the element has both the qualifier and content
        if qualifier is not None and content is not None:
            # create the form attribute
            self.form = UNTL_FORM_DISPATCH[self.tag](
                vocabularies=vocabularies,
                qualifier_value=qualifier,
                input_value=content,
                untl_object=self,
                superuser=superuser,
            )
        # if the element just has a qualifier
        elif qualifier is not None:
            # create the form attribute
            self.form = UNTL_FORM_DISPATCH[self.tag](
                vocabularies=vocabularies,
                qualifier_value=qualifier,
                untl_object=self,
                superuser=superuser,
            )
        # if the element just has content
        elif content is not None:
            # if the element is a child element
            if parent_tag is None:
                # create the form attribute
                self.form = UNTL_FORM_DISPATCH[self.tag](
                    vocabularies=vocabularies,
                    input_value=content,
                    untl_object=self,
                    superuser=superuser,
                )
            else:
                # create the form attribute
                self.form = UNTL_FORM_DISPATCH[self.tag](
                    vocabularies=vocabularies,
                    input_value=content,
                    untl_object=self,
                    parent_tag=parent_tag,
                    superuser=superuser,
                )
        # if the element has children, and no qualifiers or content
        # or is blank (not originally in the UNTL record)
        else:
            # if the element is a child element
            if parent_tag is None:
                # create the form attribute
                self.form = UNTL_FORM_DISPATCH[self.tag](
                    vocabularies=vocabularies,
                    untl_object=self,
                    superuser=superuser,
                )
            else:
                # create the form attribute
                self.form = UNTL_FORM_DISPATCH[self.tag](
                    vocabularies=vocabularies,
                    untl_object=self,
                    parent_tag=parent_tag,
                    superuser=superuser,
                )

    @property
    def completeness(self):
        """Calculates completeness, returns double"""
        return determine_completeness(self)

    @property
    def record_length(self):
        """Calculates full length of total record, including metadata"""
        return len(str(py2dict(self)))

    @property
    def record_content_length(self):
        """Calculates length of record, excluding metadata"""
        untldict = py2dict(self)
        del untldict['meta']
        return len(str(untldict))


class FormGenerator(object):

    def __init__(self, **kwargs):
        self.adjustable_items = []
        self.element_groups = self.create_form_data(**kwargs)

    def create_form_data(self, **kwargs):
        """Creates groupings of form elements"""
        # Get the the specified keyword arguments
        children = kwargs.get('children', [])
        sort_order = kwargs.get('sort_order', None)
        solr_response = kwargs.get('solr_response', None)
        superuser = kwargs.get('superuser', False)
        # Get the vocabularies to pull the qualifiers from
        vocabularies = self.get_vocabularies()
        # Loop through all untl elements in the python object
        for element in children:
            # Add children that are missing from the form
            element.children = add_missing_children(
                element.contained_children,
                element.children,
            )
            # Add the form attribute to the element
            element.add_form(
                vocabularies=vocabularies,
                qualifier=element.qualifier,
                content=element.content,
                superuser=superuser,
            )
            # if the element can contain children
            if element.form.has_children:
                # If the parent has a qualifier
                if getattr(element.form, 'qualifier_name', False):
                    # Create a representative form element for the parent
                    add_parent = PARENT_FORM[element.form.qualifier_name](
                        content=element.qualifier,
                    )
                    # Add the parent to the list of child elements
                    element.children.append(add_parent)
                # sort the elements by the index of child sort
                element.children.sort(
                    key=lambda obj: element.form.child_sort.index(obj.tag)
                )
                # Loop through the element's children (if it has any)
                for child in element.children:
                    # Add the form attribute to the element
                    child.add_form(
                        vocabularies=vocabularies,
                        qualifier=child.qualifier,
                        content=child.content,
                        parent_tag=element.tag,
                        superuser=superuser,
                    )
        element_group_dict = {}
        # Group related objects together
        for element in children:
            # Make meta-hidden its own group
            if element.form.name == 'meta' and element.qualifier == 'hidden':
                element_group_dict['hidden'] = [element]
            # Element is not meta-hidden
            else:
                # Make sure the dictionary key exists
                if element.form.name not in element_group_dict:
                    element_group_dict[element.form.name] = []
                element_group_dict[element.form.name].append(element)
        # If the hidden meta element doesn't exist, add it to its own group
        if 'hidden' not in element_group_dict:
            hidden_element = PYUNTL_DISPATCH['meta'](
                qualifier='hidden',
                content='False')
            hidden_element.add_form(
                vocabularies=vocabularies,
                qualifier=hidden_element.qualifier,
                content=hidden_element.content,
                superuser=superuser,
            )
            element_group_dict['hidden'] = [hidden_element]
        # Create a list of group object elements
        element_list = self.create_form_groupings(
            vocabularies,
            solr_response,
            element_group_dict,
            sort_order,
        )
        # Return the list of untl elements with form data added
        return element_list

    def create_form_groupings(
            self,
            vocabularies,
            solr_response,
            element_group_dict,
            sort_order
    ):
        """Creates a group object from groupings of element objects """
        element_list = []
        # Loop through the group dictionary
        for group_name, group_list in element_group_dict.items():
            # Create the element group
            element_group = UNTL_GROUP_DISPATCH[group_name](
                vocabularies=vocabularies,
                solr_response=solr_response,
                group_name=group_name,
                group_list=group_list,
            )
            # Loop through the adjustable forms of the group if they exist
            if element_group.adjustable_form is not None:
                for adj_name, form_dict in \
                        element_group.adjustable_form.items():
                    # if an item has an adjustable form,
                    # append it to the adjustable list
                    if form_dict['value_py'] is not None:
                        self.adjustable_items.append(adj_name)
            # Append the group to the element group list
            element_list.append(element_group)
        # sort the elements by the index of sort_order pre-ordered list
        element_list.sort(key=lambda obj: sort_order.index(obj.group_name))
        return element_list

    def get_vocabularies(self):
        """Get the vocabularies to pull the qualifiers from """
        # timeout in seconds
        timeout = 15
        socket.setdefaulttimeout(timeout)
        # Create the ordered vocabulary url
        vocab_url = VOCABULARIES_URL.replace('all', 'all-verbose')
        # Request the vocabularies dictionary
        try:
            vocab_dict = eval(urllib2.urlopen(vocab_url).read())
        except:
            raise UNTLStructureException("Could not retrieve the vocabularies")
        return vocab_dict

# Element Definitions #


class Metadata(UNTLElement):

    def __init__(self, **kwargs):
        self.tag = 'metadata'
        self.allows_content = False
        self.allows_qualifier = False
        self.contained_children = [
            'title', 'identifier', 'note',
            'institution', 'collection', 'subject', 'creator',
            'primarySource', 'description', 'date', 'publisher',
            'contributor', 'source', 'language', 'coverage',
            'resourceType', 'relation', 'format', 'rights',
            'degree', 'meta', 'citation',
        ]
        super(Metadata, self).__init__(**kwargs)

    def create_xml_string(self):
        """
        Creates a untl xml document in a string from a untl metadata root
        object untl_xml_string = metadata_root_object.create_xml_string()
        """
        root = self.create_xml()

        xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(
            root, pretty_print=True
        )
        return xml

    def create_xml(self, useNamespace=False):
        """
        Creates an elementtree representation of the object
        """

        UNTL_NAMESPACE = "http://digital2.library.unt.edu/untl/"
        UNTL = "{%s}" % UNTL_NAMESPACE

        NSMAP = {"untl": UNTL_NAMESPACE}

        if useNamespace:
            root = Element(UNTL + self.tag, nsmap=NSMAP)
        else:
            root = Element(self.tag)

        # sort the elements by the index of UNTL_XML_ORDER pre-ordered list
        self.sort_untl(UNTL_XML_ORDER)
        # Create an xml structure from field list
        for element in self.children:

            if useNamespace:
                create_untl_xml_subelement(root, element, UNTL)
            else:
                create_untl_xml_subelement(root, element)

        # xml = '<?xml version="1.0" encoding="UTF-8"?>\n'+\
        # tostring(root, pretty_print=True)
        # return xml
        return root

    def create_element_dict(self):
        """ Converts a untl python object into a untl python dictionary """
        untl_dict = {}
        # Loop through all untl elements in the python object
        for element in self.children:
            # if an entry for the element list hasn't
            # been made in the dictionary
            if element.tag not in untl_dict:
                # start an empty element list
                untl_dict[element.tag] = []
            # Create a dictionary to put the element into
            element_dict = {}
            # If the element has a qualifier
            if element.qualifier is not None:
                element_dict['qualifier'] = element.qualifier
            # if the element allows children
            if len(element.contained_children) > 0:
                child_dict = {}
                # Loop through the child elements
                for child in element.children:
                    # if the child has content
                    if child.content is not None:
                        child_dict[child.tag] = child.content
                # Set the elements content as the dictionary
                # of children elements
                element_dict['content'] = child_dict
            # if the element has content, but no children
            elif element.content is not None:
                element_dict['content'] = element.content
            # append the dictionary element to the element list
            untl_dict[element.tag].append(element_dict)

        return untl_dict

    def create_xml_file(self, untl_filename):
        """Takes a untl filename and creates a untl file """
        try:
            f = open(untl_filename, 'w')
            f.write(self.create_xml_string().encode("utf-8"))
            f.close()
        except:
            raise UNTLStructureException(
                "Failed to create UNTL XML file. File: %s" % (untl_filename)
            )

    def sort_untl(self, sort_structure):
        """
        Sorts the untl python object by the
        index of a sort structure pre-ordered list
        """
        self.children.sort(key=lambda obj: sort_structure.index(obj.tag))

    def validate(self):
        """ Validate all of the untl elements """
        pass

    def generate_form_data(self, **kwargs):
        """ Creates a form dictionary with the key being the element name
             and the value being a list of form element objects
        """
        # Add elements that are missing from the form
        self.children = add_missing_children(
            self.contained_children,
            self.children
        )
        # Add children to the keyword arguments
        kwargs['children'] = self.children
        # Create the form object
        return FormGenerator(**kwargs)


class Title(UNTLElement):
    def __init__(self, **kwargs):
        self.tag = 'title'
        super(Title, self).__init__(**kwargs)


class Identifier(UNTLElement):
    def __init__(self, **kwargs):
        self.tag = 'identifier'
        super(Identifier, self).__init__(**kwargs)


class Note(UNTLElement):
    def __init__(self, **kwargs):
        self.tag = 'note'
        super(Note, self).__init__(**kwargs)


class Institution(UNTLElement):
    def __init__(self, **kwargs):
        self.tag = 'institution'
        self.allows_qualifier = False
        super(Institution, self).__init__(**kwargs)


class Collection(UNTLElement):
    def __init__(self, **kwargs):
        self.tag = 'collection'
        self.allows_qualifier = False
        super(Collection, self).__init__(**kwargs)


class Subject(UNTLElement):
    def __init__(self, **kwargs):
        self.tag = 'subject'
        super(Subject, self).__init__(**kwargs)


class Creator(UNTLElement):
    def __init__(self, **kwargs):
        self.tag = 'creator'
        self.allows_content = False
        self.contained_children = [
            'info',
            'type',
            'name',
        ]
        super(Creator, self).__init__(**kwargs)


class PrimarySource(UNTLElement):
    def __init__(self, **kwargs):
        self.tag = 'primarySource'
        self.allows_qualifier = False
        super(PrimarySource, self).__init__(**kwargs)


class Description(UNTLElement):
    def __init__(self, **kwargs):
        self.tag = 'description'
        super(Description, self).__init__(**kwargs)


class Date(UNTLElement):
    def __init__(self, **kwargs):
        self.tag = 'date'
        super(Date, self).__init__(**kwargs)


class Publisher(UNTLElement):
    def __init__(self, **kwargs):
        self.tag = 'publisher'
        self.allows_content = False
        self.allows_qualifier = False
        self.contained_children = [
            'info',
            'name',
            'location',
        ]
        super(Publisher, self).__init__(**kwargs)


class Contributor(UNTLElement):
    def __init__(self, **kwargs):
        self.tag = 'contributor'
        self.allows_content = False
        self.contained_children = [
            'info',
            'type',
            'name',
        ]
        super(Contributor, self).__init__(**kwargs)


class Source(UNTLElement):
    def __init__(self, **kwargs):
        self.tag = 'source'
        super(Source, self).__init__(**kwargs)


class Language(UNTLElement):
    def __init__(self, **kwargs):
        self.tag = 'language'
        self.allows_qualifier = False
        super(Language, self).__init__(**kwargs)


class Coverage(UNTLElement):
    def __init__(self, **kwargs):
        self.tag = 'coverage'
        super(Coverage, self).__init__(**kwargs)


class ResourceType(UNTLElement):
    def __init__(self, **kwargs):
        self.tag = 'resourceType'
        self.allows_qualifier = False
        super(ResourceType, self).__init__(**kwargs)


class Relation(UNTLElement):
    def __init__(self, **kwargs):
        self.tag = 'relation'
        super(Relation, self).__init__(**kwargs)


class Format(UNTLElement):
    def __init__(self, **kwargs):
        self.tag = 'format'
        self.allows_qualifier = False
        super(Format, self).__init__(**kwargs)


class Rights(UNTLElement):
    def __init__(self, **kwargs):
        self.tag = 'rights'
        super(Rights, self).__init__(**kwargs)


class Degree(UNTLElement):
    def __init__(self, **kwargs):
        self.tag = 'degree'
        super(Degree, self).__init__(**kwargs)


class Meta(UNTLElement):
    def __init__(self, **kwargs):
        self.tag = 'meta'
        super(Meta, self).__init__(**kwargs)


class Citation(UNTLElement):
    def __init__(self, **kwargs):
        self.tag = 'citation'
        super(Citation, self).__init__(**kwargs)


class Info(UNTLElement):
    def __init__(self, **kwargs):
        self.tag = 'info'
        self.allows_qualifier = False
        super(Info, self).__init__(**kwargs)


class Type(UNTLElement):
    def __init__(self, **kwargs):
        self.tag = 'type'
        self.allows_qualifier = False
        super(Type, self).__init__(**kwargs)


class Name(UNTLElement):
    def __init__(self, **kwargs):
        self.tag = 'name'
        self.allows_qualifier = False
        super(Name, self).__init__(**kwargs)


class Location(UNTLElement):
    def __init__(self, **kwargs):
        self.tag = 'location'
        self.allows_qualifier = False
        super(Location, self).__init__(**kwargs)


PYUNTL_DISPATCH = {
    'metadata': Metadata,
    'title': Title,
    'identifier': Identifier,
    'note': Note,
    'institution': Institution,
    'collection': Collection,
    'subject': Subject,
    'creator': Creator,
    'primarySource': PrimarySource,
    'description': Description,
    'date': Date,
    'publisher': Publisher,
    'contributor': Contributor,
    'source': Source,
    'language': Language,
    'coverage': Coverage,
    'resourceType': ResourceType,
    'relation': Relation,
    'format': Format,
    'rights': Rights,
    'degree': Degree,
    'meta': Meta,
    'info': Info,
    'type': Type,
    'name': Name,
    'location': Location,
    'citation': Citation,
}


class Role(UNTLElement):
    def __init__(self, **kwargs):
        self.tag = 'role'
        super(Role, self).__init__(**kwargs)

PARENT_FORM = {
    'role': Role,
}
