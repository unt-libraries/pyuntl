"""
    How to use pyuntl:
    Create a UNTL object (children are required to exist in the class)
    from pyuntl.untldoc import PYUNTL_DISPATCH
    root_element = PYUNTL_DISPATCH['metadata']()
    publisher_element = PYUNTL_DISPATCH['publisher']()
    publisher_element.add_child(PYUNTL_DISPATCH['name'](content=content))
    root_element.add_child(publisher_element)
"""
import json
import re
import hashlib
from copy import deepcopy
from lxml.etree import iterparse
from rdflib import Namespace, Literal, URIRef, ConjunctiveGraph

from pyuntl import (UNTL_XML_ORDER, DC_ORDER,
                    HIGHWIRE_ORDER)
from pyuntl.dc_structure import DC_CONVERSION_DISPATCH, DC_NAMESPACES, XSI
from pyuntl.form_logic import REQUIRES_QUALIFIER
from pyuntl.highwire_structure import HIGHWIRE_CONVERSION_DISPATCH
from pyuntl.metadata_generator import (py2dict, pydict2xml, pydict2xmlstring,
                                       writeANVLString, highwiredict2xmlstring)
from pyuntl.untl_structure import (PYUNTL_DISPATCH, PARENT_FORM, get_vocabularies,
                                   UNTLStructureException)


NAMESPACE_REGEX = re.compile(r'^{[^}]+}(.*)')


class PyuntlException(Exception):
    """Base exception for UNTL."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return '%s' % (self.value,)


def untlxml2py(untl_filename):
    """Parse a UNTL XML file object into a pyuntl element tree.

    You can also pass input like so:
    from io import BytesIO
    untlxml2py(BytesIO(untl_xml_bytes))
    """
    # Create a stack to hold parents.
    parent_stack = []
    # Use iterparse to open the file and loop through elements.
    for event, element in iterparse(untl_filename, events=('start', 'end')):
        if NAMESPACE_REGEX.search(element.tag, 0):
            element_tag = NAMESPACE_REGEX.search(element.tag, 0).group(1)
        else:
            element_tag = element.tag
        # Process the element if it exists in UNTL.
        if element_tag in PYUNTL_DISPATCH:
            # If it is the element's opening tag,
            # add it to the parent stack.
            if event == 'start':
                parent_stack.append(PYUNTL_DISPATCH[element_tag]())
            # If it is the element's closing tag,
            # remove element from stack. Add qualifier and content.
            elif event == 'end':
                child = parent_stack.pop()
                if element.text is not None:
                    content = element.text.strip()
                    if content != '':
                        child.set_content(element.text)
                if element.get('qualifier', False):
                    child.set_qualifier(element.get('qualifier'))

                # Add the element to its parent.
                if len(parent_stack) > 0:
                    parent_stack[-1].add_child(child)
                # If it doesn't have a parent, it is the root element,
                # so return it.
                else:
                    return child
        else:
            raise PyuntlException(
                'Element "%s" not in UNTL dispatch.' % (element_tag)
            )


def untlxml2pydict(untl_filename):
    """Convert a UNTL XML file to a Python dictionary.

    You can also pass input like so:
    from io import BytesIO
    untlxml2pydict(BytesIO(untl_xml_bytes))
    """
    # Create a UNTL Python object from the XML file.
    untl_elements = untlxml2py(untl_filename)
    # Convert the Python object to a Python dictionary, and return it.
    return untlpy2dict(untl_elements)


def untlpy2dict(untl_elements):
    """Convert a UNTL Python object into a UNTL Python dictionary."""
    return py2dict(untl_elements)


def untlpydict2xml(untl_filename, untl_dict):
    """Return a UNTL file.

    Takes a UNTL filename and a UNTL Python dictionary.
    """
    return pydict2xml(untl_filename, untl_dict)


def untlpydict2xmlstring(untl_dict):
    """Create an XML string from a Python UNTL dictionary."""
    return pydict2xmlstring(untl_dict)


def untldict2py(untl_dict):
    """Convert a UNTL dictionary into a Python object."""
    # Create the root element.
    untl_root = PYUNTL_DISPATCH['metadata']()
    untl_py_list = []
    for element_name, element_list in untl_dict.items():
        # Loop through the element dictionaries in the element list.
        for element_dict in element_list:
            qualifier = element_dict.get('qualifier', None)
            content = element_dict.get('content', None)
            child_list = []
            # Handle content that is children elements.
            if isinstance(content, dict):
                for key, value in content.items():
                    child_list.append(
                        PYUNTL_DISPATCH[key](content=value),
                    )
                # Create the UNTL element that will have children elements
                # added to it.
                untl_element = PYUNTL_DISPATCH[element_name](qualifier=qualifier)
                # Add the element's children to the element.
                for child in child_list:
                    untl_element.add_child(child)
            # If not child element, create the element and
            # add qualifier and content as available.
            else:
                untl_element = PYUNTL_DISPATCH[element_name](
                    qualifier=qualifier,
                    content=content,
                )
            # Add the UNTL element to the Python element list.
            untl_py_list.append(untl_element)
    # Add the UNTL elements to the root element.
    for untl_element in untl_py_list:
        untl_root.add_child(untl_element)
    return untl_root


def post2pydict(post, ignore_list):
    """Convert the UNTL posted data to a Python dictionary."""
    root_element = PYUNTL_DISPATCH['metadata']()
    untl_form_dict = {}
    # Turn the posted data into usable data
    # (otherwise the value lists get messed up).
    form_post = dict(post.copy())
    # Loop through all the field lists.
    for key, value_list in form_post.items():
        if key not in ignore_list:
            # Split the key into the element_tag (ex. title)
            # and element attribute (ex. qualifier, content).
            (element_tag, element_attribute) = key.split('-', 1)
            if element_tag not in untl_form_dict:
                untl_form_dict[element_tag] = ()
            # Add the value list to the dictionary.
            untl_form_dict[element_tag] += (element_attribute, value_list),

    for element_tag, attribute_tuple in untl_form_dict.items():
        # Get the count of attributes/content in the element tuple.
        attribute_count = len(attribute_tuple)
        # Get the count of the first attribute's values.
        value_count = len(attribute_tuple[0][1])
        # Check to see that all attribute/content values align numerically.
        for i in range(0, attribute_count):
            if not len(attribute_tuple[i][1]) == value_count:
                raise PyuntlException('Field values did not match up '
                                      'numerically for %s' % (element_tag))
        # Create a value loop to get all values from the tuple.
        for i in range(0, value_count):
            untl_element = None
            content = ''
            qualifier = ''
            child_list = []
            # Loop through the attributes.
            # attribute_tuple[j][0] represents the attribute/content name.
            # attribute_tuple[j][1][i] represents the
            # current attribute/content value.
            for j in range(0, attribute_count):
                if attribute_tuple[j][0] == 'content':
                    content = attribute_tuple[j][1][i]
                elif attribute_tuple[j][0] == 'qualifier':
                    qualifier = attribute_tuple[j][1][i]
                # Create a child UNTL element from the data.
                else:
                    # If the child has content, append it to the child list.
                    if attribute_tuple[j][1][i] != '':
                        child_tag = attribute_tuple[j][0]
                        # Check if the child is the attribute of the element.
                        if child_tag in PARENT_FORM:
                            qualifier = attribute_tuple[j][1][i]
                        # Else, the child is a normal child of the element.
                        else:
                            child_list.append(
                                PYUNTL_DISPATCH[attribute_tuple[j][0]](
                                    content=attribute_tuple[j][1][i]
                                )
                            )
            # Create the UNTL element.
            if content == '':
                content = None
            if qualifier == '':
                qualifier = None
            if content or qualifier or child_list:
                untl_element = PYUNTL_DISPATCH[element_tag](content=content, qualifier=qualifier)
            # If the element has children, add them.
            if child_list and untl_element:
                for child in child_list:
                    untl_element.add_child(child)
            # Add the UNTL element to the root element.
            if untl_element is not None:
                root_element.add_child(untl_element)
    return root_element.create_element_dict()


def generate_untl_json(untl_elements, json_indent=4):
    """Convert UNTL elements into a JSON structure."""
    untl_dict = untlpy2dict(untl_elements)
    return json.dumps(untl_dict, sort_keys=True, indent=json_indent)


def untljson2py(untl_json):
    """Convert UNTL JSON into a Python object."""
    untl_dict = json.loads(untl_json)
    return untldict2py(untl_dict)


def untlpy2dcpy(untl_elements, **kwargs):
    """Convert the UNTL elements structure into a DC structure.

    kwargs can be passed to the function for certain effects:

    ark: Takes an ark string and creates an identifier element out of it.
    domain_name: Takes a domain string and creates an ark URL from it
    (ark and domain_name must be passed together to work properly).

    resolve_values: Converts abbreviated content into resolved vocabulary
    labels.
    resolve_urls: Converts abbreviated content into resolved vocabulary
    URLs.
    verbose_vocabularies: Uses the verbose vocabularies passed to the
    function instead of this function being required to retrieve them.

    # Create a DC Python object from a UNTL XML file.
    from pyuntl.untldoc import untlxml2py
    untl_elements = untlxml2py(untl_filename) # Or pass a file-like object.

    # OR Create a DC Python object from a UNTL dictionary.
    from pyuntl.untldoc import untldict2py
    untl_elements = untldict2py(untl_dict)

    # Convert to UNTL Python object to DC Python object.
    dc_elements = untlpy2dcpy(untl_elements)
    dc_dict = dcpy2dict(dc_elements)

    # Output DC in a specified string format.
    from pyuntl.untldoc
    import generate_dc_xml, generate_dc_json, generate_dc_txt
    # Create a DC XML string.
    generate_dc_xml(dc_dict)
    # Create a DC JSON string.
    generate_dc_json(dc_dict)
    # Create a DC text string.
    generate_dc_txt(dc_dict)
    """
    sDate = None
    eDate = None
    ark = kwargs.get('ark', None)
    domain_name = kwargs.get('domain_name', None)
    scheme = kwargs.get('scheme', 'http')
    resolve_values = kwargs.get('resolve_values', None)
    resolve_urls = kwargs.get('resolve_urls', None)
    verbose_vocabularies = kwargs.get('verbose_vocabularies', None)
    # If either resolvers were requested, get the vocabulary data.
    if resolve_values or resolve_urls:
        if verbose_vocabularies:
            # If the vocabularies were passed to the function, use them.
            vocab_data = verbose_vocabularies
        else:
            # Otherwise, retrieve them using the pyuntl method.
            vocab_data = retrieve_vocab()
    else:
        vocab_data = None
    # Create the DC parent element.
    dc_root = DC_CONVERSION_DISPATCH['dc']()
    for element in untl_elements.children:
        # Check if the UNTL element should be converted to DC.
        if element.tag in DC_CONVERSION_DISPATCH:
            # Check if the element has its content stored in children nodes.
            if element.children:
                dc_element = DC_CONVERSION_DISPATCH[element.tag](
                    qualifier=element.qualifier,
                    children=element.children,
                    resolve_values=resolve_values,
                    resolve_urls=resolve_urls,
                    vocab_data=vocab_data,
                )
            # It is a normal element.
            else:
                dc_element = DC_CONVERSION_DISPATCH[element.tag](
                    qualifier=element.qualifier,
                    content=element.content,
                    resolve_values=resolve_values,
                    resolve_urls=resolve_urls,
                    vocab_data=vocab_data,
                )
            if element.tag == 'coverage':
                # Handle start and end dates.
                if element.qualifier == 'sDate':
                    sDate = dc_element
                elif element.qualifier == 'eDate':
                    eDate = dc_element
                # Otherwise, add the coverage element to the structure.
                else:
                    dc_root.add_child(dc_element)
            # Add non coverage DC element to the structure.
            elif dc_element:
                dc_root.add_child(dc_element)
    # If the domain and ark were specified
    # try to turn them into indentifier elements.
    if ark and domain_name:
        # Create and add the permalink identifier.
        permalink_identifier = DC_CONVERSION_DISPATCH['identifier'](
            qualifier='permalink',
            domain_name=domain_name,
            ark=ark,
            scheme=scheme
        )
        dc_root.add_child(permalink_identifier)
        # Create and add the ark identifier.
        ark_identifier = DC_CONVERSION_DISPATCH['identifier'](
            qualifier='ark',
            content=ark,
        )
        dc_root.add_child(ark_identifier)
    if sDate and eDate:
        # If a start and end date exist, combine them into one element.
        dc_element = DC_CONVERSION_DISPATCH['coverage'](
            content='%s-%s' % (sDate.content, eDate.content),
        )
        dc_root.add_child(dc_element)
    elif sDate:
        dc_root.add_child(sDate)
    elif eDate:
        dc_root.add_child(eDate)
    return dc_root


def untlpy2highwirepy(untl_elements, **kwargs):
    """Convert a UNTL Python object to a highwire Python object."""
    highwire_list = []
    title = None
    publisher = None
    creation = None
    escape = kwargs.get('escape', False)
    for element in untl_elements.children:
        # If the UNTL element should be converted to highwire,
        # create highwire element.
        if element.tag in HIGHWIRE_CONVERSION_DISPATCH:
            highwire_element = HIGHWIRE_CONVERSION_DISPATCH[element.tag](
                qualifier=element.qualifier,
                content=element.content,
                children=element.children,
                escape=escape,
            )
            if highwire_element:
                if element.tag == 'title':
                    if element.qualifier != 'officialtitle' and not title:
                        title = highwire_element
                    elif element.qualifier == 'officialtitle':
                        title = highwire_element
                elif element.tag == 'publisher':
                    if not publisher:
                        # This is the first publisher element.
                        publisher = highwire_element
                        highwire_list.append(publisher)
                elif element.tag == 'date':
                    # If a creation date hasn't been found yet,
                    # verify this date is acceptable.
                    if not creation and element.qualifier == 'creation':
                        if highwire_element.content:
                            creation = highwire_element
                            if creation:
                                highwire_list.append(creation)
                # Otherwise, add the element to the list if it has content.
                elif highwire_element.content:
                    highwire_list.append(highwire_element)
    # If the title was found, add it to the list.
    if title:
        highwire_list.append(title)
    return highwire_list


def untlpydict2dcformatteddict(untl_dict, **kwargs):
    """Convert a UNTL data dictionary to a formatted DC data dictionary."""
    ark = kwargs.get('ark', None)
    domain_name = kwargs.get('domain_name', None)
    scheme = kwargs.get('scheme', 'http')
    resolve_values = kwargs.get('resolve_values', None)
    resolve_urls = kwargs.get('resolve_urls', None)
    verbose_vocabularies = kwargs.get('verbose_vocabularies', None)
    # Get the UNTL object.
    untl_py = untldict2py(untl_dict)
    # Convert it to a DC object.
    dc_py = untlpy2dcpy(
        untl_py,
        ark=ark,
        domain_name=domain_name,
        resolve_values=resolve_values,
        resolve_urls=resolve_urls,
        verbose_vocabularies=verbose_vocabularies,
        scheme=scheme
    )
    # Return a formatted DC dictionary.
    return dcpy2formatteddcdict(dc_py)


def dcpy2formatteddcdict(dc_py):
    """Convert a DC Python object to a formatted DC data dictionary."""
    # Convert DC py to a dictionary (structured like UNTL's dictionary format).
    dc_dict = dcpy2dict(dc_py)
    # Return the formatted dictionary.
    return formatted_dc_dict(dc_dict)


def dcpy2dict(dc_elements):
    """Convert the DC Python structure to a dictionary."""
    return py2dict(dc_elements)


def formatted_dc_dict(dc_dict):
    """Change the formatting of the DC data dictionary.

    Change the passed in DC data dictionary into a dictionary
    with a list of values for each element.
    i.e. {'publisher': ['someone', 'someone else'], 'title': ['a title'],}
    """
    # Don't modify the unformatted dictionary in place.
    dc_dict = deepcopy(dc_dict)
    for key, element_list in dc_dict.items():
        new_element_list = []
        # Add the content for each element to the new element list.
        for element in element_list:
            new_element_list.append(element['content'])
        dc_dict[key] = new_element_list
    return dc_dict


def generate_dc_xml(dc_dict):
    """Generate a DC XML string."""
    # Define the root namespace.
    root_namespace = '{%s}' % DC_NAMESPACES['oai_dc']
    # Set the elements namespace URL.
    elements_namespace = '{%s}' % DC_NAMESPACES['dc']
    schema_location = ('http://www.openarchives.org/OAI/2.0/oai_dc/ '
                       'http://www.openarchives.org/OAI/2.0/oai_dc.xsd')
    root_attributes = {
        '{%s}schemaLocation' % XSI: schema_location,
    }
    # Return the DC XML string.
    return pydict2xmlstring(
        dc_dict,
        ordering=DC_ORDER,
        root_label='dc',
        root_namespace=root_namespace,
        elements_namespace=elements_namespace,
        namespace_map=DC_NAMESPACES,
        root_attributes=root_attributes,
    )


def generate_dc_json(dc_dict):
    """Generate DC JSON data.

    Returns data as a JSON formatted string.
    """
    formatted_dict = formatted_dc_dict(dc_dict)
    return json.dumps(formatted_dict, sort_keys=True, indent=4)


def generate_dc_txt(dc_dict):
    """Generate DC data as ANVL formatted string."""
    return writeANVLString(dc_dict, DC_ORDER)


def highwirepy2dict(highwire_elements):
    """Convert a list of highwire elements into a dictionary.

    The dictionary returned contains the elements in the
    UNTL dict format.
    """
    highwire_dict = {}
    # Make a list of content dictionaries for each element name.
    for element in highwire_elements:
        if element.name not in highwire_dict:
            highwire_dict[element.name] = []
        highwire_dict[element.name].append({'content': element.content})
    return highwire_dict


def generate_highwire_xml(highwire_elements):
    """Generate a highwire XML string."""
    return highwiredict2xmlstring(highwire_elements)


def generate_highwire_json(highwire_elements):
    """Convert highwire elements into a JSON structure.

    Returns data as a JSON formatted string.
    """
    highwire_dict = highwirepy2dict(highwire_elements)
    return json.dumps(highwire_dict, sort_keys=True, indent=4)


def generate_highwire_text(highwire_elements):
    """Convert highwire elements into an ANVL formatted string."""
    highwire_dict = highwirepy2dict(highwire_elements)
    return writeANVLString(highwire_dict, HIGHWIRE_ORDER)


def dcdict2rdfpy(dc_dict):
    """Convert a DC dictionary into an RDF Python object."""
    ark_prefix = 'ark: ark:'
    uri = URIRef('')
    # Create the RDF Python object.
    rdf_py = ConjunctiveGraph()
    # Set DC namespace definition.
    DC = Namespace('http://purl.org/dc/elements/1.1/')
    # Get the ark for the subject URI from the ark identifier.
    for element_value in dc_dict['identifier']:
        if element_value['content'].startswith(ark_prefix):
            uri = URIRef(
                element_value['content'].replace(
                    ark_prefix, 'info:ark'
                )
            )
    # Bind the prefix/namespace pair.
    rdf_py.bind('dc', DC)
    # Get the values for each element in the ordered DC elements.
    for element_name in DC_ORDER:
        element_value_list = dc_dict.get(element_name, [])
        # Add the values to the RDF object.
        for element_value in element_value_list:
            # Handle URL values differently.
            if 'http' in element_value['content'] and ' ' not in element_value['content']:
                rdf_py.add((
                    uri,
                    DC[element_name],
                    URIRef(element_value['content'])
                ))
            else:
                rdf_py.add((
                    uri,
                    DC[element_name],
                    Literal(element_value['content'])
                ))
    return rdf_py


def generate_rdf_xml(dc_dict):
    """Convert an RDF Python structure to an XML string.

    Takes a DC dict. Converts it to an RDF Python object.
    Returns in XML serialized format.
    """
    rdf_py = dcdict2rdfpy(dc_dict)
    return rdf_py.serialize(format='pretty-xml', encoding='utf-8')


def retrieve_vocab():
    """Get the vocabulary data for the field.

    Retrieves and returns the vocabulary. Upon failure, returns None.
    """
    try:
        return get_vocabularies()
    except UNTLStructureException:
        return None


def add_empty_fields(untl_dict):
    """Add empty values if UNTL fields don't have values."""
    # Iterate the ordered UNTL XML element list to determine
    # which elements are missing from the untl_dict.
    for element in UNTL_XML_ORDER:
        if element not in untl_dict:
            # Try to create an element with content and qualifier.
            try:
                py_object = PYUNTL_DISPATCH[element](
                    content='',
                    qualifier='',
                )
            except:
                # Try to create an element with content.
                try:
                    py_object = PYUNTL_DISPATCH[element](content='')
                except:
                    # Try to create an element without content.
                    try:
                        py_object = PYUNTL_DISPATCH[element]()
                    except:
                        raise PyuntlException(
                            'Could not add empty element field.'
                        )
                    else:
                        untl_dict[element] = [{'content': {}}]
                else:
                    # Handle element without children.
                    if not py_object.contained_children:
                        untl_dict[element] = [{'content': ''}]
                    else:
                        untl_dict[element] = [{'content': {}}]
            else:
                # Handle element without children.
                if not py_object.contained_children:
                    untl_dict[element] = [{'content': '', 'qualifier': ''}]
                else:
                    untl_dict[element] = [{'content': {}, 'qualifier': ''}]
            # Add empty contained children.
            for child in py_object.contained_children:
                untl_dict[element][0].setdefault('content', {})
                untl_dict[element][0]['content'][child] = ''
    return untl_dict


def find_untl_errors(untl_dict, **kwargs):
    """Add empty required qualifiers to create valid UNTL."""
    fix_errors = kwargs.get('fix_errors', False)
    error_dict = {}
    # Loop through all elements that require qualifiers.
    for element_name in REQUIRES_QUALIFIER:
        # Loop through the existing elements that require qualifers.
        for element in untl_dict.get(element_name, []):
            # If there is no qualifier, record the error.
            if not element.get('qualifier', None):
                error_dict[element_name] = 'no_qualifier'
                # If it should be fixed, set an empty qualifier.
                if fix_errors:
                    element.setdefault('qualifier', '')
    # Combine the error dict and UNTL dict into a dict.
    found_data = {
        'untl_dict': untl_dict,
        'error_dict': error_dict,
    }
    return found_data


def untl_dict_to_tuple(untl_dict):
    """Convert untl_dict values to list of lists of tuples."""
    untl_dict = deepcopy(untl_dict)
    untl_tuple = {}
    for elem, value in untl_dict.items():
        for i, v in enumerate(value):
            # We are trying to get a consistent ordering of values
            # so reordering doesn't count as a change.
            if isinstance(value[i]['content'], dict):
                value[i]['content'] = sorted(list(value[i]['content'].items()))
            value[i] = sorted(list(value[i].items()))
        untl_tuple[elem] = value
    return untl_tuple


def generate_hash(input):
    """Return an md5 hash of an object by first converting it to bytes."""
    return hashlib.md5(repr(input).encode()).hexdigest()


def untl_to_hash_dict(untl_elements, meaningfulMeta=True):
    """Produce a dictionary of hashed values for untl elements.

    Converts untl elements into a dictionary of elements where
    the value is a hash of the sorted list of tuples of the elements'
    values. If meaningfulMeta is True, ignore metadata fields that
    show no meaningful change to metadata records.
    """
    untl_dict = untlpy2dict(untl_elements)
    if meaningfulMeta and untl_dict.get('meta') is not None:
        unmeaningful = ('metadataModificationDate', 'metadataModifier')
        untl_dict['meta'] = [
            e for e in untl_dict['meta'] if e.get('qualifier') not in unmeaningful
        ]
    untl_tuple = untl_dict_to_tuple(untl_dict)
    return {k: generate_hash(v) for k, v in untl_tuple.items()}


def get_record_version(untl_elements):
    """Produce a version hash from the hashed UNTL dictionary."""
    hash_results = untl_to_hash_dict(untl_elements, True)
    return generate_hash(hash_results)
