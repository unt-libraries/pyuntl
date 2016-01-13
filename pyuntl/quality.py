import re


# These are common legacy values for attributes that do not have data.
COMMON_DEFAULT_ATTRIBUTE_VALUES = [
    "change as necessary",
    "change template values when appropriate",
]

DEFAULT_VALUE_REGEX = re.compile("{{{.*}}}")

# These are the children of a pyuntl record
# that get scored for completeness.
PYUNTL_COMPLETENESS_SCORED_ATTRIBUTES = [
    'title',
    'description',
    'collection',
    'institution',
    'language',
    'resourceType',
    'format',
    'subject',
    'meta',
]


def determine_completeness(py_untl):
    """Take a Python untl and calculate the completeness.

    Completeness is based on this: metadata_quality.rst documentation.
    Returns a float 0.0 - 1.0.
    """
    # Default values for the completeness dictionary.
    completeness_dict = {
        'title': {'present': False, 'weight': 10, },
        'description': {'present': False, 'weight': 1, },
        'language': {'present': False, 'weight': 1, },
        'collection': {'present': False, 'weight': 10, },
        'institution': {'present': False, 'weight': 10, },
        'resourceType': {'present': False, 'weight': 5, },
        'format': {'present': False, 'weight': 1, },
        'subject': {'present': False, 'weight': 1, },
        'meta': {'present': False, 'weight': 20, },
    }

    total_points = sum(item['weight'] for item in completeness_dict.values())
    py_untl_object_score = 0.0

    # Iterate through the attributes of the pyuntl record.
    # This loop will toggle the Boolean for scoring.
    for i in py_untl.children:
        # Process attribute that is scorable and has content.
        if i.tag in PYUNTL_COMPLETENESS_SCORED_ATTRIBUTES:
            if i.content:
                content = i.content.lower()
                # Try and match against new default placeholders.
                match = bool(DEFAULT_VALUE_REGEX.search(content))
                # The content is not a legacy placeholder.
                if content not in COMMON_DEFAULT_ATTRIBUTE_VALUES and not match:
                    # Only consider <meta qualifier="system"> records.
                    if i.tag == 'meta':
                        if i.qualifier == 'system':
                            completeness_dict['%s' % i.tag]['present'] = True
                    else:
                        completeness_dict['%s' % i.tag]['present'] = True
    # Get total score of the pyuntl object.
    for k, v in completeness_dict.iteritems():
        # If presence was toggled true, adjust score based on weight.
        if v['present']:
            py_untl_object_score += completeness_dict[k]['weight']
    # Calculate the float score completeness.
    completeness = py_untl_object_score / total_points
    return completeness


if __name__ == '__main__':
    import glob
    import os

    from pyuntl import untldoc

    path = os.getcwd()
    for infile in glob.glob(os.path.join(path, '../tests/*.untl.xml')):
        py_untl = untldoc.untlxml2py(infile)
        completeness = determine_completeness(py_untl)
        print '|||||| %s' % infile.split('/')[-1]
        print 'completeness score: %s\n' % completeness
