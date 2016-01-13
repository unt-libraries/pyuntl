import re


def normalize_LCSH(subject):
    """Normalize a LCSH subject heading prior to indexing."""
    # Strip then divide on -- which is a delimiter for LCSH;
    # rejoin after stripping parts.
    subject_parts = subject.strip().split('--')
    joined_subject = ' -- '.join([part.strip() for part in subject_parts])

    # Check if there is punctuation at the end of the string,
    # and if not, add a trailing period.
    if re.search(r'[^a-zA-Z0-9]$', joined_subject) is None:
        joined_subject = joined_subject + '.'

    return joined_subject


def normalize_UNTL(subject):
    """Normalize a UNTL subject heading for consistency."""
    subject = subject.strip()
    subject = re.sub(r'[\s]+', ' ', subject)
    return subject


def UNTL_to_encodedUNTL(subject):
    """Normalize a UNTL subject heading to be used in SOLR."""
    subject = normalize_UNTL(subject)
    subject = subject.replace(' ', '_')
    subject = subject.replace('_-_', '/')
    return subject


def encodedUNTL_to_UNTL(subject):
    """Return a normalized UNTL subject heading back to string."""
    subject = subject.replace('/', '_-_')
    subject = subject.replace('_', ' ')
    return subject


def untldict_normalizer(untl_dict, normalizations):
    """Normalize UNTL elements by their qualifier.

    Takes a UNTL descriptive metadata dictionary and a dictionary of
    the elements and the qualifiers for normalization:
    {'element1': ['qualifier1', 'qualifier2'],
     'element2': ['qualifier3']}
    and normalizes the elements with that qualifier.
    """
    # Loop through the element types in the UNTL metadata.
    for element_type, element_list in untl_dict.items():
        # A normalization is required for that element type.
        if element_type in normalizations:
            # Get the required normalizations for specific qualifiers list.
            norm_qualifier_list = normalizations.get(element_type)
            # Loop through the element lists within that element type.
            for element in element_list:
                # Determine if the qualifier requires normalization.
                qualifier = element.get('qualifier', None)
                if qualifier in norm_qualifier_list:
                    content = element.get('content', None)
                    # Determine if there is normalizing for the element.
                    if element_type in ELEMENT_NORMALIZERS:
                        elem_norms = ELEMENT_NORMALIZERS.get(element_type,
                                                             None)
                        # If the qualified element requires a
                        # normalization and has content, replace the
                        # content with the normalized.
                        if qualifier in elem_norms:
                            if content and content != '':
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
