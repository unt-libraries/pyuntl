class UNTLValidatorException(Exception):
    """Base exception for the UNTL validator"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "%s" % (self.value,)


class ValidationElement(object):
    """A class for containing UNTL validation elements"""


UNTL_VALIDATION_DISPATCH = {
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
}
