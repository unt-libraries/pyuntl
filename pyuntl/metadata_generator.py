from lxml.etree import Element, SubElement, tostring

from pyuntl import UNTL_XML_ORDER, HIGHWIRE_ORDER
from pyuntl.etd_ms_structure import DEGREE_ORDER


XSI = 'http://www.w3.org/2001/XMLSchema-instance'

# Namespaces for the DC XML.
DC_NAMESPACES = {
    'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'xsi': XSI,
}


class MetadataGeneratorException(Exception):
    """Base exception for Metadata Generation."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return '%s' % (self.value,)


def py2dict(elements):
    """Convert a Python object into a Python dictionary."""
    metadata_dict = {}
    # Loop through all elements in the Python object.
    for element in elements.children:
        # Start an empty element list if an entry for the element
        # list hasn't been made in the dictionary.
        if element.tag not in metadata_dict:
            metadata_dict[element.tag] = []
        element_dict = {}
        if hasattr(element, 'qualifier') and element.qualifier is not None:
            element_dict['qualifier'] = element.qualifier
        # Set the element's content as a dictionary
        # of children elements.
        if len(element.children) > 0:
            child_dict = {}
            for child in element.children:
                if child.content is not None:
                    child_dict[child.tag] = child.content
            element_dict['content'] = child_dict
        # Set element content that is not children.
        elif element.content is not None:
            if element.content.strip() != '':
                element_dict['content'] = element.content
        # Append the dictionary to the element list
        # if the element has content or children.
        if element_dict.get('content', False):
            metadata_dict[element.tag].append(element_dict)

    return metadata_dict


def etd_ms_py2dict(elements):
    """Convert a Python object into a Python dictionary."""
    metadata_dict = {}
    # Loop through all elements in the Python object.
    for element in elements.children:
        # Start an empty element list if an entry for the element
        # list hasn't been made in the dictionary.
        if element.tag not in metadata_dict:
            metadata_dict[element.tag] = []
        element_dict = {}
        if hasattr(element, 'role'):
            element_dict['role'] = element.role
        elif hasattr(element, 'scheme'):
            element_dict['scheme'] = element.scheme
        elif hasattr(element, 'qualifier') and element.qualifier is not None \
                and element.tag is 'title':
            element_dict['qualifier'] = element.qualifier
        # Set the element's content as a dictionary
        # of children elements.
        if element.children:
            child_dict = {}
            for child in element.children:
                if child.content is not None:
                    child_dict[child.tag] = child.content
            element_dict['content'] = child_dict
        # Set element content that is not children.
        elif element.content is not None:
            if element.content.strip() is not '':
                element_dict['content'] = element.content
        # Append the dictionary to the element list
        # if the element has content or children.
        if element_dict.get('content', False):
            metadata_dict[element.tag].append(element_dict)

    return metadata_dict


def pydict2xml(filename, metadata_dict, **kwargs):
    """Create an XML file.

    Takes a path to where the XML file should be created
    and a metadata dictionary.
    """
    try:
        f = open(filename, 'w')
        f.write(pydict2xmlstring(metadata_dict, **kwargs).encode('utf-8'))
        f.close()
    except:
        raise MetadataGeneratorException(
            'Failed to create an XML file. Filename: %s' % (filename)
        )


def pydict2xmlstring(metadata_dict, **kwargs):
    """Create an XML string from a metadata dictionary."""
    ordering = kwargs.get('ordering', UNTL_XML_ORDER)
    root_label = kwargs.get('root_label', 'metadata')
    root_namespace = kwargs.get('root_namespace', None)
    elements_namespace = kwargs.get('elements_namespace', None)
    namespace_map = kwargs.get('namespace_map', None)
    root_attributes = kwargs.get('root_attributes', None)
    # Set any root namespace and namespace map.
    if root_namespace and namespace_map:
        root = Element(root_namespace + root_label, nsmap=namespace_map)
    elif namespace_map:
        root = Element(root_label, nsmap=namespace_map)
    else:
        root = Element(root_label)
    # Set any root element attributes.
    if root_attributes:
        for key, value in root_attributes.items():
            root.attrib[key] = value
    # Create an XML structure from field list.
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
    # Create the XML tree.
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(
        root,
        pretty_print=True
    )


def create_dict_subelement(root, subelement, content, **kwargs):
    """Create a XML subelement from a Python dictionary."""
    attribs = kwargs.get('attribs', None)
    namespace = kwargs.get('namespace', None)
    key = subelement

    # Add subelement's namespace and attributes.
    if namespace and attribs:
        subelement = SubElement(root, namespace + subelement, attribs)
    elif namespace:
        subelement = SubElement(root, namespace + subelement)
    elif attribs:
        subelement = SubElement(root, subelement, attribs)
    # Otherwise, create SubElement without any extra data.
    else:
        subelement = SubElement(root, subelement)
    if not isinstance(content, dict):
        subelement.text = content
    # Do special case ordering for degree children on etd_ms.
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
    """Create an XML string from the highwire data dictionary."""
    # Sort the elements by the ordering list.
    highwire_elements.sort(key=lambda obj: ordering.index(obj.name))
    root = Element('metadata')
    for element in highwire_elements:
        attribs = {'name': element.name, 'content': element.content}
        SubElement(root, 'meta', attribs)
    # Create the XML tree.
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
            if (not string[index + 1].isspace() and
                    not string[index - 1].isspace()):
                stringPart1 = string[0:index]
                stringPart2 = string[index:]
                # Do not pass firstLineOffset.
                return stringPart1 + '\n' + breakString(
                    stringPart2,
                    originalWidth
                )

        index = index - 1
    return string


def writeANVLString(ANVLDict, ordering=UNTL_XML_ORDER):
    """Take a dictionary and write out the key/value pairs
    in ANVL format.
    """
    lines = []
    # Loop through the ordering for the data.
    for key in ordering:
        # Make sure the element exists in the data set.
        if key in ANVLDict:
            # Get the list of elements.
            element_list = ANVLDict[key]
            # Loop through the element contents.
            for element in element_list:
                value = element.get('content', '')
                offset = len(key) + 1
                line = '%s: %s' % (key, breakString(value, 79, offset))
                lines.append(line)
    return '\n'.join(lines)
