import re
try:
    # the json module was included in the stdlib in python 2.6
    # http://docs.python.org/library/json.html
    import json
except ImportError:
    # simplejson 2.0.9 is available for python 2.4+
    # http://pypi.python.org/pypi/simplejson/2.0.9
    # simplejson 1.7.3 is available for python 2.3+
    # http://pypi.python.org/pypi/simplejson/1.7.3
    import simplejson as json
from lxml.etree import iterparse, Element
import urllib2
import datetime
import sys
from rdflib import Namespace, Literal, URIRef, ConjunctiveGraph, URIRef
from untl_structure import PYUNTL_DISPATCH, PARENT_FORM
from pyuntl import UNTL_XML_ORDER, DC_ORDER, ETD_MS_ORDER, VOCABULARIES_URL, \
    HIGHWIRE_ORDER
from dc_structure import DC_CONVERSION_DISPATCH, DC_NAMESPACES, XSI
from highwire_structure import HIGHWIRE_CONVERSION_DISPATCH
from etd_ms_structure import ETD_MS_CONVERSION_DISPATCH, \
    ETD_MS_DEGREE_DISPATCH, ETD_MS_NAMESPACES
from form_logic import REQUIRES_QUALIFIER
from metadata_generator import py2dict, pydict2xml, pydict2xmlstring, \
    writeANVLString, highwiredict2xmlstring, etd_ms_py2dict, \
    MetadataGeneratorException


class PyuntlException(Exception):
    """Base exception for UNTL"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "%s" % (self.value,)

"""
    How to use pyuntl:
    Create a untl object (children are required to exist in the class)
    from pyuntl.untldoc import PYUNTL_DISPATCH
    root_element = PYUNTL_DISPATCH['metadata']()
    publisher_element = PYUNTL_DISPATCH['publisher']()
    publisher_element.add_child(PYUNTL_DISPATCH['name'](content=content))
    root_element.add_child(publisher_element)
"""
NAMESPACE_REGEX = re.compile(r'^{[^}]+}(.*)')


def untlxml2py(untl_filename):
    """Takes a untl xml filename and parses it into a python object
        You can also pass this a string as file input like so:
        import StringIO
        untlxml2py(StringIO.StringIO(untl_string))
    """
    #Create a stack to hold parents
    parent_stack = []
    #Use iterparse to open the file and loop through elements
    for event, element in iterparse(untl_filename, events=("start", "end")):
        if NAMESPACE_REGEX.search(element.tag, 0):
            element_tag = NAMESPACE_REGEX.search(element.tag, 0).group(1)
        else:
            element_tag = element.tag
            #If the element exists in untl
        if element_tag in PYUNTL_DISPATCH:
            #If it is the opening tag of the element
            if event == 'start':
                if element.text != None:
                    content = element.text.strip()
                else:
                    content = ''
                    #if the element has a qualifier and content
                if element.get('qualifier', False) and content != '':
                    #Add the element to the parent stack
                    parent_stack.append(
                        PYUNTL_DISPATCH[element_tag](
                            qualifier=element.get('qualifier'),
                            content=element.text,
                        )
                    )
                #if the element has a qualifier
                elif element.get('qualifier', False):
                    #Add the element to the parent stack
                    parent_stack.append(
                        PYUNTL_DISPATCH[element_tag](
                            qualifier=element.get('qualifier')
                        )
                    )
                #if the element has content
                elif content != '':
                    #Add the element to the parent stack
                    parent_stack.append(
                        PYUNTL_DISPATCH[element_tag](content=element.text)
                    )
                #if the element has no content or attributes
                else:
                    #Add the element to the parent stack
                    parent_stack.append(PYUNTL_DISPATCH[element_tag]())
            #if it is the closing tag of the element
            elif event == 'end':
                #Take the element off the parent and add it to its own parent
                child = parent_stack.pop()
                if len(parent_stack) > 0:
                    parent_stack[-1].add_child(child)
                #if it doesn't have a parent, it must be the root element
                else:
                    #Return the root element
                    return child
        else:
            raise PyuntlException(
                "Element \"%s\" not in untl dispatch." % (element_tag)
            )


def untlxml2pydict(untl_filename):
    """ Convert a untl xml file to a python dictionary
        You can also pass this a string as file input like so:
        import StringIO
        untlxml2pydict(StringIO.StringIO(untl_string))
    """
    #Create a untl python object from the xml file
    untl_elements = untlxml2py(untl_filename)
    #Convert the python object to a python dictionary and return it
    return untlpy2dict(untl_elements)


def untlpy2dict(untl_elements):
    """ Converts a untl python object into a untl python dictionary """
    return py2dict(untl_elements)


def untlpydict2xml(untl_filename, untl_dict):
    """
    Takes a untl filename and a untl python dictionary.
    Returns a untl file
    """
    return pydict2xml(untl_filename, untl_dict)


def untlpydict2xmlstring(untl_dict):
    """Creates an xml string from a python untl dictionary"""
    return pydict2xmlstring(untl_dict)


def untldict2py(untl_dict):
    """Converts a untl dictionary into a python object """
    #Create root element
    untl_root = PYUNTL_DISPATCH['metadata']()
    untl_py_list = []
    #Loop through the dictionary elements
    for element_name, element_list in untl_dict.items():
        #Loop through the element dictionaries in the element list
        for element_dict in element_list:
            #Get the element qualifier
            qualifier = element_dict.get('qualifier', None)
            #Get the element content
            content = element_dict.get('content', None)
            child_list = []
            #if the content is children elements
            if isinstance(content, dict):
                #loop through the dictionary's content values
                for key, value in content.items():
                    child_list.append(
                        PYUNTL_DISPATCH[key](content=value),
                    )
                    #Create the untl element that will have children elements
                    #added to it
                if qualifier != None:
                    untl_element = PYUNTL_DISPATCH[element_name](
                        qualifier=qualifier
                    )
                else:
                    untl_element = PYUNTL_DISPATCH[element_name]()
                    #Loop through the element's children and add them
                    #to the element
                for child in child_list:
                    untl_element.add_child(child)
            #if the element has a qualifier and content
            elif content != None and qualifier != None:
                #Create the untl element using the pyuntl dispatch
                untl_element = PYUNTL_DISPATCH[element_name](
                    qualifier=qualifier,
                    content=content,
                )
            #if the element has a qualifier
            elif qualifier != None:
                #Create the untl element using the pyuntl dispatch
                untl_element = PYUNTL_DISPATCH[element_name](
                    qualifier=qualifier,
                )
            #if the element has content
            elif content != None:
                #Create the untl element using the pyuntl dispatch
                untl_element = PYUNTL_DISPATCH[element_name](
                    content=content,
                )
            #The element only has children
            elif len(child_list) > 0:
                #Create the untl element using the pyuntl dispatch
                untl_element = PYUNTL_DISPATCH[element_name]()
                #Add the untl element to the python element list
            untl_py_list.append(untl_element)
        #Add the untl elements to the root element
    for untl_element in untl_py_list:
        untl_root.add_child(untl_element)
        #return the untl python object
    return untl_root


def post2pydict(post, ignore_list):
    """Convert the untl posted data to a python dictionary """
    #Create the root element
    root_element = PYUNTL_DISPATCH['metadata']()
    untl_form_dict = {}
    #Turns the posted data into usable data (otherwise the value lists get messed up)
    form_post = dict(post.copy())
    #Loop through all the field lists
    for key, value_list in form_post.items():
        if not key in ignore_list:
            #split the key into the element_tag (ex. title)
            #and element attribute (ex. qualifier, content)
            (element_tag, element_attribute) = key.split('-', 1)
            #if a dictionary for element_tag doesn't exist, create it
            if not element_tag in untl_form_dict:
                untl_form_dict[element_tag] = ()
            #Add the value list to the dictionary
            untl_form_dict[element_tag] += (element_attribute, value_list),

    #Loop through the newly formed form dictionary
    for element_tag, attribute_tuple in untl_form_dict.items():
        #Gets the amount of attributes/content in the element tuple
        attribute_count = len(attribute_tuple)
        #Gets the count of the first attribute values
        value_count = len(attribute_tuple[0][1])
        #Check to see that all attribute/content values align numerically
        for i in range(0, attribute_count):
            if not len(attribute_tuple[i][1]) == value_count:
                raise PyuntlException, "Field values did not match up numerically for %s" \
                    % (element_tag)
        #Create a value loop to get all values from the tuple
        for i in range(0, value_count):
            #Set content and qualifier empty
            untl_element = None
            content = ''
            qualifier = ''
            child_list = []
            #Loop through the attributes
            #attribute_tuple[j][0] represents the attribute/content name
            #attribute_tuple[j][1][i] represents the current attribute/content value
            for j in range(0, attribute_count):
                #Capture the content
                if attribute_tuple[j][0] == 'content':
                    content = unicode(attribute_tuple[j][1][i])
                #Capture the qualifier
                elif attribute_tuple[j][0] == 'qualifier':
                    qualifier = attribute_tuple[j][1][i]
                #Create a child untl element from the data
                else:
                    #If the child has content, append it to the child list
                    if attribute_tuple[j][1][i] != '':
                        #Get the child's tag name
                        child_tag = attribute_tuple[j][0]
                        #If the child is the actual attribute of the element
                        if child_tag in PARENT_FORM:
                            qualifier = attribute_tuple[j][1][i]
                        #Else if the child is a normal child of the element
                        else:
                            child_list.append(
                                PYUNTL_DISPATCH[attribute_tuple[j][0]](
                                    content=attribute_tuple[j][1][i]
                                    )
                                )
            #Create the untl element
            #if the element has both content and qualifier
            if content != '' and qualifier != '':
                untl_element = PYUNTL_DISPATCH[element_tag](
                    content = content,
                    qualifier = qualifier,
                    )
            #if the element has only content
            elif content != '':
                untl_element = PYUNTL_DISPATCH[element_tag](
                    content = content,
                    )
            #if the element has only qualifier
            elif qualifier != '':
                untl_element = PYUNTL_DISPATCH[element_tag](
                    qualifier = qualifier,
                    )
            #Else the element has only children elements
            elif len(child_list) > 0:
                untl_element = PYUNTL_DISPATCH[element_tag]()
            #if the element has children
            if len(child_list) > 0 and untl_element != None:
                #add all the children to the new element
                for child in child_list:
                    untl_element.add_child(child)
            #add the untl element to the root element
            if untl_element != None:
                root_element.add_child(untl_element)
    return root_element.create_element_dict()


def untlpy2dcpy(untl_elements, **kwargs):
    """Converts the untl elements structure into a DC structure
        kwargs can be passed to the function for certain effects:

        ark : Takes an ark string and creates and identifier element out of it
        domain_name : Takes a domain string and creates an ark url from it
        (ark and domain_name must be passed together to work properly)

        resolve_values : Converts abbreviated content into resolved vocabulary
        labels
        resolve_urls : Converts abbreviated content into resolved vocabulary
        urls
        verbose_vocabularies: Uses the verbose vocabularies passed to the
        function instead of this function being required to retrieve them

        #Create a dc python object from a UNTL XML file
        from pyuntl.untldoc import untlxml2py
        untl_elements = untlxml2py(untl_filename) #Or pass a file-like object

        #OR Create a dc python object from a UNTL dictionary
        from pyuntl.untldoc import untldict2py
        untl_elements = untldict2py(untl_dict)

        #Convert to UNTL python object to DC python object
        dc_elements = untlpy2dcpy(untl_elements)
        dc_dict = dcpy2dict(dc_elements)

        #Output DC in a specified string format
        from pyuntl.untldoc
        import generate_dc_xml, generate_dc_json, generate_dc_txt
        #Create a DC XML string
        generate_dc_xml(dc_dict)
        #Create a DC JSON string
        generate_dc_json(dc_dict)
        #Create a DC text string
        generate_dc_txt(dc_dict)
    """
    sDate = None
    eDate = None
    #Get the ark and the domain name if they were passed
    ark = kwargs.get('ark', None)
    domain_name = kwargs.get('domain_name', None)
    #Determine if the resolved values or URLS have been requested
    resolve_values = kwargs.get('resolve_values', None)
    resolve_urls = kwargs.get('resolve_urls', None)
    #Get the verbose vocabularies, if it was passed to the function
    verbose_vocabularies = kwargs.get('verbose_vocabularies', None)
    #If either resolvers were requested, get the vocabulary data
    if resolve_values or resolve_urls:
        if verbose_vocabularies:
            #if the vocabularies were passed to the function, use them
            vocab_data = verbose_vocabularies
        else:
            #Otherwise, retrieve them using the pyuntl method
            vocab_data = retrieve_vocab()
    else:
        vocab_data = None
        #Create the DC parent element
    dc_root = DC_CONVERSION_DISPATCH['dc']()
    added_identifiers = False
    #Loop through all untl elements in the python object
    for element in untl_elements.children:
        #if the untl element should be converted to DC
        if element.tag in DC_CONVERSION_DISPATCH:
            #If the element has its content stored in children nodes
            if element.children:
                #Create the DC element
                dc_element = DC_CONVERSION_DISPATCH[element.tag](
                    qualifier=element.qualifier,
                    children=element.children,
                    resolve_values=resolve_values,
                    resolve_urls=resolve_urls,
                    vocab_data=vocab_data,
                )
            #It is a normal element
            else:
                #Create the DC element
                dc_element = DC_CONVERSION_DISPATCH[element.tag](
                    qualifier=element.qualifier,
                    content=element.content,
                    resolve_values=resolve_values,
                    resolve_urls=resolve_urls,
                    vocab_data=vocab_data,
                )
            #if it is a coverage element
            if element.tag == 'coverage':
                #If it is a start date
                if element.qualifier == 'sDate':
                    sDate = dc_element
                #if it is an end date
                elif element.qualifier == 'eDate':
                    eDate = dc_element
                #Otherwise add the element to the structure
                else:
                    dc_root.add_child(dc_element)
            #Otherwise add the element to the structure if the element exists
            elif dc_element:
                dc_root.add_child(dc_element)
        #Add DC identifiers
    #if the domain and ark were specified
    #try to turn them into indentifier elements
    if ark and domain_name:
        #Create the permalink identifier
        permalink_identifier = DC_CONVERSION_DISPATCH['identifier'](
            qualifier='permalink',
            domain_name=domain_name,
            ark=ark,
        )
        #Add the permalink indentifier element
        dc_root.add_child(permalink_identifier)
        #Create the ark identifier
        ark_identifier = DC_CONVERSION_DISPATCH['identifier'](
            qualifier='ark',
            content=ark,
        )
        #Add the ark identifier element
        dc_root.add_child(ark_identifier)
        #If a start date and end date exist
    if sDate and eDate:
        #combine them into one element
        dc_element = DC_CONVERSION_DISPATCH['coverage'](
            content="%s-%s" % (sDate.content, eDate.content),
        )
        dc_root.add_child(dc_element)
    #if just start date exists
    elif sDate:
        dc_root.add_child(sDate)
    #if just end date exists
    elif eDate:
        dc_root.add_child(eDate)
    return dc_root


def untlpy2highwirepy(untl_elements, **kwargs):
    """Converts a untl python object to a highwire python object"""
    highwire_list = []
    title = None
    publisher = None
    creation = None
    escape = kwargs.get('escape', False)
    #Loop through all untl elements in the python object
    for element in untl_elements.children:
        #if the untl element should be converted to highwire
        if element.tag in HIGHWIRE_CONVERSION_DISPATCH:
            #Create the highwire
            highwire_element = HIGHWIRE_CONVERSION_DISPATCH[element.tag](
                qualifier=element.qualifier,
                content=element.content,
                children=element.children,
                escape=escape,
            )
            #if a highwire element was created
            if highwire_element:
                #if it is a coverage element
                if element.tag == 'title':
                    #If it is a start date
                    if element.qualifier != 'officialtitle' and not title:
                        title = highwire_element
                    elif element.qualifier == 'officialtitle':
                        title = highwire_element
                #if it is a publisher element
                elif element.tag == 'publisher':
                    #Found the first publisher
                    if not publisher:
                        publisher = highwire_element
                        highwire_list.append(publisher)
                #if it is a date element
                elif element.tag == 'date':
                    #If a creation data hasn't been found yet
                    if not creation and element.qualifier == 'creation':
                        #Check to make sure the date was acceptable
                        if highwire_element.content:
                            #Found a creation date
                            creation = highwire_element
                            #If a proper creation date was found
                            if creation:
                                highwire_list.append(creation)
                #Otherwise add the element to the list if the element exists
                elif highwire_element.content:
                    highwire_list.append(highwire_element)
        #If the title was found, add it to the list
    if title:
        highwire_list.append(title)
    return highwire_list


def untlpydict2dcformatteddict(untl_dict, **kwargs):
    """Converts a untl data dictionary to a formmated DC data dictionary"""
    #Get the ark and the domain name if they were passed
    ark = kwargs.get('ark', None)
    domain_name = kwargs.get('domain_name', None)
    #Determine if the resolved values or URLS have been requested
    resolve_values = kwargs.get('resolve_values', None)
    resolve_urls = kwargs.get('resolve_urls', None)
    #Get the verbose vocabularies, if it was passed to the function
    verbose_vocabularies = kwargs.get('verbose_vocabularies', None)
    #Get the untl object
    untl_py = untldict2py(untl_dict)
    #Convert it to a DC object
    dc_py = untlpy2dcpy(
        untl_py,
        ark=ark,
        domain_name=domain_name,
        resolve_values=resolve_values,
        resolve_urls=resolve_urls,
        verbose_vocabularies=verbose_vocabularies,
    )
    #Return the formatted DC dictionary
    return dcpy2formatteddcdict(dc_py)


def dcpy2formatteddcdict(dc_py):
    """Converts a dc python object to a formatted DC data dictionary"""
    #Convert dc py to a dictionary (structured like untl's dictionary format)
    dc_dict = dcpy2dict(dc_py)
    #Return the formatted dictionary
    return formatted_dc_dict(dc_dict)


def dcpy2dict(dc_elements):
    """Converts the dc python structure to a dictionary"""
    return py2dict(dc_elements)


def formatted_dc_dict(dc_dict):
    """Changes the formatting of the DC data dictionary into a dictionary
        with a list of values for each element.
        i.e. {'publisher': ['someone', 'someone else'], 'title': ['a title'],}
    """
    #Loop through the dc data dictionary
    for key, element_list in dc_dict.items():
        new_element_list = []
        #Retrieve the elements out of the element list
        for element in element_list:
            #Add the content to the new element list data
            new_element_list.append(element['content'])
            #Set the dictionary value to the newly structured element list
        dc_dict[key] = new_element_list
    return dc_dict


def generate_dc_xml(dc_dict):
    """Generates a DC xml string"""
    #Define the root namespace
    root_namespace = "{%s}" % DC_NAMESPACES['oai_dc']
    #Set the elements namespace url
    elements_namespace = "{%s}" % DC_NAMESPACES['dc']
    root = Element(root_namespace + "dc", nsmap=DC_NAMESPACES)
    #Define the schema location
    schema_location = 'http://www.openarchives.org/OAI/2.0/oai_dc/ ' +\
                      'http://www.openarchives.org/OAI/2.0/oai_dc.xsd'
    #Create the root attributes
    root_attributes = {
        "{%s}schemaLocation" % XSI: schema_location,
    }
    #Create the dc xml string
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
    """Generates DC json data, changes the structure of the data"""
    formatted_dict = formatted_dc_dict(dc_dict)
    #Return the structure as a json string
    return json.dumps(formatted_dict, sort_keys=True, indent=4)


def generate_dc_txt(dc_dict):
    """Generates DC json data"""
    return writeANVLString(dc_dict, DC_ORDER)


def highwirepy2dict(highwire_elements):
    """Converts a list of highwire elements into a dictionary of
        listed elements, using the untl dict format
    """
    highwire_dict = {}
    #Loop through the element list
    for element in highwire_elements:
        #Make sure the element list is created
        if not element.name in highwire_dict:
            highwire_dict[element.name] = []
            #Add the highwire element to the highwire dictionary
        highwire_dict[element.name].append({'content': element.content})
    return highwire_dict


def generate_highwire_xml(highwire_elements):
    """Generates a highwire xml string"""
    return highwiredict2xmlstring(highwire_elements)


def generate_highwire_json(highwire_elements):
    """Converts highwire elements into a json structure"""
    highwire_dict = highwirepy2dict(highwire_elements)
    #Return the structure as a json string
    return json.dumps(highwire_dict, sort_keys=True, indent=4)


def generate_highwire_text(highwire_elements):
    """Converts highwire elements into a text structure"""
    highwire_dict = highwirepy2dict(highwire_elements)
    return writeANVLString(highwire_dict, HIGHWIRE_ORDER)


def dcdict2rdfpy(dc_dict):
    """Converts a dc dictionary into an rdf python object"""
    ark_prefix = 'ark: ark:'
    uri = URIRef('')
    #Create the rdf python object
    rdf_py = ConjunctiveGraph()
    #DC namespace definition
    DC = Namespace('http://purl.org/dc/elements/1.1/')
    #Get the ark for the subject URI from the ark identifier
    for element_value in dc_dict['identifier']:
        if element_value['content'].startswith(ark_prefix):
            uri = URIRef(
                element_value['content'].replace(
                    ark_prefix, 'info:ark'
                )
            )
        #Bind the prefix/namespace pair
    rdf_py.bind('dc', DC)
    #Loop through the ordered dc elements
    for element_name in DC_ORDER:
        #Get the values for the element
        element_value_list = dc_dict.get(element_name, [])
        #Loop through the element values
        for element_value in element_value_list:
            #if the value is a url
            if 'http' in element_value['content'] and \
                    not ' ' in element_value['content']:
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
    """Converts an rdf python structure to an xml string"""
    #Create the rdf python object
    rdf_py = dcdict2rdfpy(dc_dict)
    #Return in an xml serialized format
    return rdf_py.serialize(format="pretty-xml")


def retrieve_vocab():
    """Get the vocabulary data for the field"""
    #Determine the url to the vocabulary
    url = VOCABULARIES_URL.replace('all', 'all-verbose')
    try:
        #Retrieve the vocabulary data
        return eval(urllib2.urlopen(url).read())
    except:
        return None


def add_empty_fields(untl_dict):
    """If certain UNTL fields don't have values, add empty values"""
    #Walk through all the elements
    for element in UNTL_XML_ORDER:
        #Determine if there isn't any value for that element
        if not element in untl_dict:
            #Try to create an element with content
            try:
                py_object = PYUNTL_DISPATCH[element](
                    content='',
                    qualifier='',
                )
            except:
                #Try to create an element with content
                try:
                    py_object = PYUNTL_DISPATCH[element](content='')
                except:
                    #if that failed, try to create and element without content
                    try:
                        py_object = PYUNTL_DISPATCH[element]()
                    except:
                        raise PyuntlException(
                            "Could not add empty element field."
                        )
                    else:
                        untl_dict[element] = [{'content': {}}]
                else:
                    #If the element doesn't have children
                    if not py_object.contained_children:
                        untl_dict[element] = [{'content': ''}]
                    else:
                        untl_dict[element] = [{'content': {}}]
            else:
                #If the element doesn't have children
                if not py_object.contained_children:
                    untl_dict[element] = [{'content': '', 'qualifier': ''}]
                else:
                    untl_dict[element] = [{'content': {}, 'qualifier': ''}]
                #Add empty contained children
            for child in py_object.contained_children:
                untl_dict[element][0].setdefault('content', {})
                untl_dict[element][0]['content'][child] = ''
    return untl_dict


def add_empty_etd_ms_fields(etd_ms_dict):
    """If certain ETD_MS fields don't have values, add empty values"""
    #Walk through all the elements
    for element in ETD_MS_ORDER:
        #Determine if there isn't any value for that element
        if element not in etd_ms_dict:
            #Try to create an element with content
            try:
                py_object = ETD_MS_CONVERSION_DISPATCH[element](
                    content='',
                    qualifier='',
                )
            except:
                #Try to create an element with content
                try:
                    py_object = ETD_MS_CONVERSION_DISPATCH[element](content='')
                except:
                    #if that failed, try to create and element without content
                    try:
                        py_object = ETD_MS_CONVERSION_DISPATCH[element]()
                    except:
                        raise PyuntlException(
                            "Could not add empty element field."
                        )
                    else:
                        etd_ms_dict[element] = [{'content': {}}]
                else:
                    #If the element doesn't have children
                    if not py_object.contained_children:
                        etd_ms_dict[element] = [{'content': ''}]
                    else:
                        etd_ms_dict[element] = [{'content': {}}]
            else:
                #If the element doesn't have children
                if py_object:
                    if not py_object.contained_children:
                        etd_ms_dict[element] = [{'content': '', 'qualifier': ''}]
                else:
                    etd_ms_dict[element] = [{'content': {}, 'qualifier': ''}]
            #Add empty contained children
            if py_object:
                for child in py_object.contained_children:
                    etd_ms_dict[element][0].setdefault('content', {})
                    etd_ms_dict[element][0]['content'][child] = ''
    return etd_ms_dict


def find_untl_errors(untl_dict, **kwargs):
    """Add empty required qualifiers so that it creates valid UNTL"""
    fix_errors = kwargs.get('fix_errors', False)
    error_dict = {}
    #Loop through the elements that require qualifiers
    for element_name in REQUIRES_QUALIFIER:
        #Loop through the existing elements that require qualifers
        for element in untl_dict.get(element_name, []):
            error_dict[element_name] = 'no_qualifier'
            #If it should be fixed
            if fix_errors:
                #Set an empty qualifier if it doesn't have one
                element.setdefault('qualifier', "")
        #Combine the error dict and untl dict into a dict
    found_data = {
        'untl_dict': untl_dict,
        'error_dict': error_dict,
    }
    return found_data


def untlpy2etd_ms(untl_elements, **kwargs):
    """
    Converts the untl elements structure into a ETD_MS structure
    kwargs can be passed to the function for certain effects
    """
    degree_children = {}
    date_exists = False
    seen_creation = False
    #make the root
    etd_ms_root = ETD_MS_CONVERSION_DISPATCH['thesis']()
    #Loop through all untl elements in the python object
    for element in untl_elements.children:
        etd_ms_element = None
        #if the untl element should be converted to etd_ms
        if element.tag in ETD_MS_CONVERSION_DISPATCH:
            #If the element has its content stored in children nodes
            if element.children:
                #Create the etd_ms element
                etd_ms_element = ETD_MS_CONVERSION_DISPATCH[element.tag](
                    qualifier=element.qualifier,
                    children=element.children,
                )
            #if we hit a degree element, we want to make just one
            elif element.tag == 'degree':
                #make a dict of the degree children information
                if element.qualifier in [
                    'name',
                    'level',
                    'discipline',
                    'grantor',
                ]:
                    degree_children[element.qualifier] = element.content
            #if we encounter a date, limit to 1st instance of creation date
            elif element.tag == 'date':
                #creation date or not?
                if element.qualifier == 'creation':
                    #does the root already have a date?
                    for child in etd_ms_root.children:
                        if child.tag == 'date':
                            #if so, kill the child
                            del child
                            if not seen_creation:
                                date_exists = False
                    seen_creation = True
                    if not date_exists:
                        #Create the etd_ms element
                        etd_ms_element = ETD_MS_CONVERSION_DISPATCH[element.tag](
                            qualifier=element.qualifier,
                            content=element.content,
                        )
                        date_exists = True
            #It is a normal element
            elif element.tag not in ['date', 'degree']:
                #Create the etd_ms element
                etd_ms_element = ETD_MS_CONVERSION_DISPATCH[element.tag](
                    qualifier=element.qualifier,
                    content=element.content,
                )
            #add the element to the structure if the element exists
            if etd_ms_element:
                etd_ms_root.add_child(etd_ms_element)
        if element.tag == 'meta':
            #initialize ark to False becuase we are unsure if it exists yet
            ark = False
            #iterate through children and look for ark
            for i in etd_ms_root.children:
                if i.tag == 'identifier' and i.content.startswith(
                    'http://digital.library.unt.edu/'
                ):
                    #if found, flag it as existing
                    ark = True
            #if the ark doesn't yet exist, try and create it.
            if ark != True:
                #reset for future tests
                ark = False
                #Get the ark
                if element.qualifier == 'ark':
                    ark = element.content
                #try to turn them into indentifier elements
                if ark != None:
                    #Create the ark identifier
                    ark_identifier = ETD_MS_CONVERSION_DISPATCH['identifier'](
                        ark=ark,
                    )
                    #Add the ark identifier element
                    etd_ms_root.add_child(ark_identifier)
    # If children exist for the degree, make a degree element
    if degree_children:
        degree_element = ETD_MS_CONVERSION_DISPATCH['degree']()
        #when we have all the elements stored, add the children to the
        #degree node
        degree_child_element = None
        for k, v in degree_children.iteritems():
            #create the individual classes for degrees
            degree_child_element = ETD_MS_DEGREE_DISPATCH[k](
                content=v,
            )
            #if the keys in degree_children are valid, it makes the child
            if degree_child_element:
                degree_element.add_child(degree_child_element)
        etd_ms_root.add_child(degree_element)
    return etd_ms_root


def generate_etd_ms_xml(etd_ms_dict):
    """Generates a DC xml string"""

    return pydict2xmlstring(
        etd_ms_dict,
        ordering=ETD_MS_ORDER,
        root_label='thesis',
        namespace_map=ETD_MS_NAMESPACES,
    )


def etd_ms_dict2xmlfile(filename, metadata_dict):
    """Takes a filename and a  python dictionary, and creates an xml file """
    try:
        f = open(filename, 'w')
        f.write(generate_etd_ms_xml(metadata_dict).encode("utf-8"))
        f.close()
    except:
        raise MetadataGeneratorException(
            "Failed to create an XML file. Filename: %s" % (filename)
        )
