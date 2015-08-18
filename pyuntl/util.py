import re


def normalize_LCSH(subject):
    """ Function to normalize a LCSH subject heading prior to indexing """
    #strip then divide on -- which is a delimiter for LCSH,
    #rejoin after stripping parts
    subject_parts = subject.strip().split("--")
    joined_subject = " -- ".join([part.strip() for part in subject_parts])

    # Check if there is punctuation at the end of the string
    # If not add a trailing period
    if re.search(r"[^a-zA-Z0-9]$", joined_subject) is None:
        joined_subject = joined_subject + "."

    return joined_subject


def normalize_UNTL(subject):
    """ normalize a UNTL subject heading for consistency """

    subject = subject.strip()
    subject = re.sub(r"[\s]+", " ", subject)
    return subject


def UNTL_to_encodedUNTL(subject):
    """ normalize a UNTL subject heading to be used in SOLR """

    subject = normalize_UNTL(subject)
    subject = subject.replace(" ", "_")
    subject = subject.replace("_-_", "/")
    return subject


def encodedUNTL_to_UNTL(subject):
    """ return a normalized UNTL subject heading back to string. """

    subject = subject.replace("/", "_-_")
    subject = subject.replace("_", " ")
    return subject


def untldict_normalizer(untl_dict, normalizations):
    """
    Takes a untl descriptive metadata dictionary also takes a dictionary of
    the elements and the qualifiers for normalization:
    {'element1': ['qualifier1', 'qualifier2'], 'element2': ['qualifier3']}
    and normalizes the elements with that qualifier
    """
    #Loop through the element types in the untl metadata
    for element_type, element_list in untl_dict.items():
        #if a normalization is required for that element type
        if element_type in normalizations:
            #Get the required normalizations for specific qualifiers list
            norm_qualifier_list = normalizations.get(element_type)
            #Loop through the element lists within that element type
            for element in element_list:
                #Determine the qualifier
                qualifier = element.get('qualifier', None)
                #if this qualifier requires normalization
                if qualifier in norm_qualifier_list:
                    #Get the content of the element
                    content = element.get('content', None)
                    #Determine if there is normalizing for the element
                    if element_type in ELEMENT_NORMALIZERS:
                        elem_norms = ELEMENT_NORMALIZERS.get(
                            element_type,
                            None
                        )
                        #if the qualified element requires a normalization
                        if qualifier in elem_norms:
                            #If the content exists and isn't empty
                            if content and content != '':
                                #Replace the content with the normalized
                                element['content'] = \
                                    elem_norms[qualifier](content)
    return untl_dict

SUBJECT_NORMALIZERS = {
    'LCSH': normalize_LCSH,
    'UNTL-BS': normalize_UNTL,
}

ELEMENT_NORMALIZERS = {
    'subject': SUBJECT_NORMALIZERS,
}
