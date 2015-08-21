from pyuntl import UNTL_XML_ORDER, HIGHWIRE_ORDER
from lxml.etree import Element, SubElement, tostring
from etd_ms_structure import DEGREE_ORDER


class MetadataGeneratorException(Exception):
    """Base exception for Metadata Generation"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "%s" % (self.value,)

XSI = 'http://www.w3.org/2001/XMLSchema-instance'

# Namespaces for the DC xml
DC_NAMESPACES = {
    'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'xsi': XSI,
}


def py2dict(elements):
    """ Converts a python object into a python dictionary """
    metadata_dict = {}
    # Loop through all  elements in the python object
    for element in elements.children:
        # if an entry for the element list hasn't been made in the dictionary
        if element.tag not in metadata_dict:
            # start an empty element list
            metadata_dict[element.tag] = []
        # Create a dictionary to put the element into
        element_dict = {}
        # If the element has a qualifier
        if hasattr(element, 'qualifier') and element.qualifier is not None:
            element_dict['qualifier'] = element.qualifier
        # if the element has children
        if len(element.children) > 0:
            child_dict = {}
            # Loop through the child elements
            for child in element.children:
                # if the child has content
                if child.content is not None:
                    child_dict[child.tag] = child.content
            # Set the elements content as the dictionary of children elements
            element_dict['content'] = child_dict
        # if the element has content, but no children
        elif element.content is not None:
            # if the content, stipped of whitespace, isn't an empty string
            if element.content.strip() != '':
                element_dict['content'] = element.content
        # if the element has content or children
        if element_dict.get('content', False):
            # append the dictionary element to the element list
            metadata_dict[element.tag].append(element_dict)

    return metadata_dict


def etd_ms_py2dict(elements):
    """
    Converts a python object into a python dictionary
    """

    # create metadata dictionary
    metadata_dict = {}
    # Loop through all  elements in the python object
    for element in elements.children:
        # if an entry for the element list hasn't been made in the dictionary
        if element.tag not in metadata_dict:
            # start an empty element list
            metadata_dict[element.tag] = []
        # Create a dictionary to put the element into
        element_dict = {}
        # If element has role
        if hasattr(element, 'role'):
            element_dict['role'] = element.role
        # If element has scheme
        elif hasattr(element, 'scheme'):
            element_dict['scheme'] = element.scheme
        # If the element has a qualifier
        elif hasattr(element, 'qualifier') and element.qualifier is not None \
                and element.tag is 'title':
            element_dict['qualifier'] = element.qualifier
        # if the element has children
        if element.children:
            child_dict = {}
            # Loop through the child elements
            for child in element.children:
                # if the child has content
                if child.content is not None:
                    child_dict[child.tag] = child.content
            # Set the elements content as the dictionary of children elements
            element_dict['content'] = child_dict
        # if the element has content, but no children
        elif element.content is not None:
            # if the content, stipped of whitespace, isn't an empty string
            if element.content.strip() is not '':
                element_dict['content'] = element.content
        # if the element doesn't have content or children
        if element_dict.get('content', False):
            # append the dictionary element to the element list
            metadata_dict[element.tag].append(element_dict)

    return metadata_dict


def pydict2xml(filename, metadata_dict, **kwargs):
    """Takes a filename and a  python dictionary, and creates an xml file """
    try:
        f = open(filename, 'w')
        f.write(pydict2xmlstring(metadata_dict, **kwargs).encode("utf-8"))
        f.close()
    except:
        raise MetadataGeneratorException(
            "Failed to create an XML file. Filename: %s" % (filename)
        )


def pydict2xmlstring(metadata_dict, **kwargs):
    """Creates an xml string from a python  dictionary"""
    ordering = kwargs.get('ordering', UNTL_XML_ORDER)
    root_label = kwargs.get('root_label', 'metadata')
    root_namespace = kwargs.get('root_namespace', None)
    elements_namespace = kwargs.get('elements_namespace', None)
    namespace_map = kwargs.get('namespace_map', None)
    root_attributes = kwargs.get('root_attributes', None)
    # if the root's namespace and namespace map are defined
    if root_namespace and namespace_map:
        root = Element(root_namespace + root_label, nsmap=namespace_map)
    # if just the namespace map is defined
    elif namespace_map:
        root = Element(root_label, nsmap=namespace_map)
    else:
        root = Element(root_label)
    # If the room element has attributes
    if root_attributes:
        # Loop through the attributes
        for key, value in root_attributes.items():
            root.attrib[key] = value
    # Create an xml structure from field list
    for metadata_key in ordering:
        if metadata_key in metadata_dict:
            for element in metadata_dict[metadata_key]:
                if 'content' in element and 'qualifier' in element:
                    create_dict_subelement(
                        root,
                        metadata_key,
                        element['content'],
                        attribs={'qualifier': element['qualifier']},
                        namespace=elements_namespace,
                        )
                elif 'content' in element and 'role' in element:
                    create_dict_subelement(
                        root,
                        metadata_key,
                        element['content'],
                        attribs={'role': element['role']},
                        namespace=elements_namespace,
                    )
                elif 'content' in element and 'scheme' in element:
                    create_dict_subelement(
                        root,
                        metadata_key,
                        element['content'],
                        attribs={'scheme': element['scheme']},
                        namespace=elements_namespace,
                    )
                elif 'content' in element:
                    create_dict_subelement(
                        root,
                        metadata_key,
                        element['content'],
                        namespace=elements_namespace,
                    )
    # Create xml tree
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(
        root,
        pretty_print=True
    )


def create_dict_subelement(root, subelement, content, **kwargs):
    """Creates a xml subelement from a python dictionary"""
    attribs = kwargs.get('attribs', None)
    namespace = kwargs.get('namespace', None)
    key = subelement

    # if the element has a namespace and attributes
    if namespace and attribs:
        subelement = SubElement(root, namespace + subelement, attribs)
    # if the element has just a namespace
    elif namespace:
        subelement = SubElement(root, namespace + subelement)
    # if it just has attributes
    elif attribs:
        subelement = SubElement(root, subelement, attribs)
    # if it doesn't have any extra data
    else:
        subelement = SubElement(root, subelement)
    if not isinstance(content, dict):
        subelement.text = content
    # special case ordering for degree children on etd_ms
    elif key is 'degree':
        for degree_order_key in DEGREE_ORDER:
            for descriptor, value in content.items():
                if descriptor == degree_order_key:
                    sub_descriptors = SubElement(subelement, descriptor)
                    sub_descriptors.text = value
    else:
        for descriptor, value in content.items():
            sub_descriptors = SubElement(subelement, descriptor)
            sub_descriptors.text = value


def highwiredict2xmlstring(highwire_elements, ordering=HIGHWIRE_ORDER):
    """Create an xml string from the highwire data dictionary"""
    # sort the elements by the ordering list
    highwire_elements.sort(key=lambda obj: ordering.index(obj.name))
    root = Element('metadata')
    for element in highwire_elements:
        attribs = {'name': element.name, 'content': element.content}
        SubElement(root, 'meta', attribs)
    # Create xml tree
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(
        root,
        pretty_print=True
    )


def breakString(string, width=79, firstLineOffset=0):
    originalWidth = width
    width = width - firstLineOffset
    if len(string) < width + 1:
        return string
    index = width
    while index > 0:
        if ' ' == string[index]:
            if not string[index + 1].isspace() and \
                    not string[index - 1].isspace():
                stringPart1 = string[0:index]
                stringPart2 = string[index:]
                # do not pass firstLineOffset
                return stringPart1 + "\n" + breakString(
                    stringPart2,
                    originalWidth
                )

        index = index - 1
    return string


def writeANVLString(ANVLDict, ordering=UNTL_XML_ORDER):
    """
    Take a dictionary and write out they key/value pairs in ANVL format
    """
    lines = []
    # Loop through the ordering for the data
    for key in ordering:
        # Make sure the element exists in the data set
        if key in ANVLDict:
            # Get the list of elements
            element_list = ANVLDict[key]
            # Loop through the element contents
            for element in element_list:
                value = element.get('content', '')
                offset = len(key) + 1
                line = "%s: %s" % (key, breakString(value, 79, offset))
                lines.append(line)
    return "\n".join(lines)
