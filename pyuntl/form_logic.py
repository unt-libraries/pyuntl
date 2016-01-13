import json

from pyuntl import UNTL_USAGE_LINK


REQUIRES_QUALIFIER = [
    'title',
    'date',
    'description',
    'subject',
    'coverage',
    'citation',
    'rights',
    'identifier',
    'degree',
    'note',
]


class UNTLFormException(Exception):
    """Base exception for the UNTL form Python structure."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return '%s' % (self.value,)


def get_qualifier_dict(vocabularies, qualifier_vocab):
    """Get the qualifier dictionary based on the element's qualifier
    vocabulary.
    """
    # Raise exception if the vocabulary can't be found.
    if vocabularies.get(qualifier_vocab, None) is None:
        raise UNTLFormException(
            'Could not retrieve qualifier vocabulary "%s" for the form.'
            % (qualifier_vocab)
        )
    else:
        # Return the sorted vocabulary.
        return vocabularies.get(qualifier_vocab)


def get_content_dict(vocabularies, content_vocab):
    """Get the content dictionary based on the element's content
    vocabulary.
    """
    # Raise exception if the vocabulary can't be found.
    if vocabularies.get(content_vocab, None) is None:
        raise UNTLFormException(
            'Could not retrieve content vocabulary "%s" for the form.'
            % (content_vocab)
        )
    else:
        # Return the sorted vocabulary.
        return vocabularies.get(content_vocab)


class FormGroup(object):
    """Class used to group forms."""

    def __init__(self, **kwargs):
        # Get the vocabularies that contain the qualifiers.
        self.vocabularies = kwargs.get('vocabularies', {})
        # Get the group name (element name).
        self.group_name = kwargs.get('group_name', None)
        # Get the group list (list of elements).
        self.group_list = kwargs.get('group_list', [])
        # Get the vocabularies that contain the qualifiers.
        self.solr_response = kwargs.get('solr_response', 'error')
        self.group_label = self.get_group_label()
        self.group_hidden = self.get_group_hidden()
        self.group_usage_link = self.get_group_usage_link()
        # Determine if the element's form is adjustable.
        self.adjustable_form = getattr(self, 'adjustable_form', None)
        # Determine if the group goes into the separate display.
        self.separate_display = getattr(self, 'separate_display', False)

    def get_group_label(self):
        """Extract the group label from the group list."""
        first_element = self.group_list[0]
        return first_element.form.label

    def get_group_hidden(self):
        """Determine if the entire group of elements is hidden
        (decide whether to hide the entire group).
        """
        # Loop through all the elements in the group.
        for element in self.group_list:
            # Handle element that is not hidden or has a form.
            if element.form.view_type != 'none':
                return False
            # Loop through the children to make sure elements aren't hidden.
            for child_element in element.children:
                # Handle child element that is not hidden or has a form.
                if child_element.form.view_type != 'none':
                    return False
        return True

    def get_group_usage_link(self):
        """Get the usage link for the group element."""
        first_element = self.group_list[0]
        usage_link = getattr(first_element.form, 'usage_link', None)
        return usage_link

    def get_adjustable_form(self, element_dispatch):
        """Create an adjustable form from an element dispatch table."""
        adjustable_form = {}
        # Loop through the qualifiers to create the adjustable form.
        for key in element_dispatch.keys():
            adjustable_form[key] = element_dispatch[key]()
        return adjustable_form

    def set_qualified_input(self):
        """Determine the properties for the blank qualified input
        fields.
        """
        form_dict = {
            'view_type': 'qualified-input',
            'value_json': None,
            'value_py': None,
        }
        return form_dict


class CoverageGroup(FormGroup):
    """Class for defining the coverage group."""

    def __init__(self, **kwargs):
        super(CoverageGroup, self).__init__(**kwargs)
        coverage_dispatch = {
            'date': self.set_qualified_input,
            'eDate': self.set_qualified_input,
            'sDate': self.set_qualified_input,
            'placeName': self.set_coverage_placeName,
            'timePeriod': self.set_coverage_timePeriod,
        }
        # Create the adjustable form property
        # (data structure for adjusting form with JavaScript).
        self.adjustable_form = self.get_adjustable_form(coverage_dispatch)

    def set_coverage_placeName(self):
        """Determine the properties for the placeName coverage field."""
        if (self.solr_response and
                self.solr_response != 'error' and
                self.solr_response.response != 'error'):
            location_list = self.solr_response.get_location_list_facet().facet_list
        else:
            location_list = []
        form_dict = {
            'view_type': 'prefill',
            'value_json': json.dumps(location_list, ensure_ascii=False),
            'value_py': location_list,
        }
        return form_dict

    def set_coverage_timePeriod(self):
        """Determine the properties for the timePeriod coverage field."""
        content_dict = get_content_dict(self.vocabularies, 'coverage-eras')
        form_dict = {
            'view_type': 'dd-value',
            'value_json': json.dumps(content_dict, ensure_ascii=False),
            'value_py': content_dict,
        }
        return form_dict


class RightsGroup(FormGroup):
    """Class for defining the rights group."""

    def __init__(self, **kwargs):
        super(RightsGroup, self).__init__(**kwargs)
        rights_dispatch = {
            'access': self.set_rights_access,
            'holder': self.set_qualified_input,
            'license': self.set_rights_license,
            'statement': self.set_qualified_input,
        }
        # Create the adjustable form property
        # (datastructure for adjusting form with JavaScript).
        self.adjustable_form = self.get_adjustable_form(rights_dispatch)

    def set_rights_access(self):
        """Determine the properties for the access rights field."""
        content_dict = get_content_dict(self.vocabularies, 'rights-access')
        form_dict = {
            'view_type': 'dd-value',
            'value_json': json.dumps(content_dict, ensure_ascii=False),
            'value_py': content_dict,
        }
        return form_dict

    def set_rights_license(self):
        """Determine the properties for the license rights field."""
        content_dict = get_content_dict(self.vocabularies, 'rights-licenses')
        form_dict = {
            'view_type': 'dd-value',
            'value_json': json.dumps(content_dict, ensure_ascii=False),
            'value_py': content_dict,
        }
        return form_dict


class CitationGroup(FormGroup):
    """Class for defining the citation group."""

    def __init__(self, **kwargs):
        super(CitationGroup, self).__init__(**kwargs)
        citation_dispatch = {
            'peerReviewed': self.set_citation_peerReviewed,
        }
        qualifier_list = get_content_dict(
            self.vocabularies,
            'citationQualifiers'
        )
        # Loop through the qualifiers for Citation.
        for qualifier in qualifier_list:
            # See if there is not a specific way to handle the qualifier.
            if not qualifier['name'] in citation_dispatch:
                # Add the generic qualifier to dispatch with a generic input.
                citation_dispatch[
                    qualifier['name']
                ] = self.set_qualified_input
        # Create the adjustable form property
        # (datastructure for adjusting form with JavaScript).
        self.adjustable_form = self.get_adjustable_form(citation_dispatch)

    def set_citation_peerReviewed(self):
        content_list = [
            {'name': 'True', 'label': 'True'},
            {'name': 'False', 'label': 'False'}
        ]
        form_dict = {
            'view_type': 'dd-value',
            'value_json': json.dumps(content_list, ensure_ascii=False),
            'value_py': content_list,
        }
        return form_dict


class DegreeGroup(FormGroup):
    """Class for defining the degree group."""

    def __init__(self, **kwargs):
        super(DegreeGroup, self).__init__(**kwargs)
        degree_dispatch = {
            'publicationType': self.set_degree_publication_types,
        }
        qualifier_list = get_content_dict(
            self.vocabularies,
            'degree-information'
        )
        # Loop through the qualifiers for degree.
        for qualifier in qualifier_list:
            # See if there is not a specific way to handle the qualifier.
            if not qualifier['name'] in degree_dispatch:
                # Add generic qualifier to the dispatch with a generic input.
                degree_dispatch[qualifier['name']] = self.set_qualified_input
        # Create the adjustable form property
        # (datastructure for adjusting form with JavaScript).
        self.adjustable_form = self.get_adjustable_form(degree_dispatch)

    def set_degree_publication_types(self):
        content_dict = get_content_dict(self.vocabularies, 'publication-types')
        form_dict = {
            'view_type': 'dd-value',
            'value_json': json.dumps(content_dict, ensure_ascii=False),
            'value_py': content_dict,
        }
        return form_dict


class HiddenGroup(FormGroup):
    """Class for defining the rights group."""

    def __init__(self, **kwargs):
        super(HiddenGroup, self).__init__(**kwargs)
        self.separate_display = True


class FormElement(object):
    """Class for containing UNTL form elements."""

    def __init__(self, **kwargs):
        # Set all the defaults if inheriting class hasn't defined them.
        # Set name of the element.
        self.name = getattr(self, 'name', None)
        # Set verbose name of the field.
        self.label = getattr(self, 'label', self.name)
        # Set whether the label of the element is inline with the input.
        self.label_inline = getattr(self, 'label_inline', False)
        # Set text that defines what the field is for.
        self.help_text = getattr(self, 'help_text', '')
        # Set the view type for the form object.
        self.view_type = getattr(self, 'view_type', None)
        # Determine if the qualifiers of an object are editable.
        self.editable_qualifiers = getattr(self, 'editable_qualifiers', True)
        if self.view_type is None:
            self.view_type_error()
        # Set URL for the usage of the element.
        self.usage_link = getattr(
            self,
            'usage_link',
            self.create_link(''),
        )
        # Get the vocabularies that contain the qualifiers.
        self.vocabularies = kwargs.get('vocabularies', {})
        # Get whether the element is repeatable in the form.
        self.repeatable = getattr(self, 'repeatable', True)
        # Get whether the user is able to edit the field.
        self.editable = getattr(self, 'editable', True)
        # Get whether the element has child elements.
        self.has_children = getattr(self, 'has_children', False)
        # Determine if the qualifier is required.
        if self.name in REQUIRES_QUALIFIER:
            self.qualifier_required = True
        else:
            self.qualifier_required = False

    def create_link(self, element_path):
        """Create the usage link from the base usage_link and the path
        to the specific elements usage.
        """
        return '%s%s' % (UNTL_USAGE_LINK, element_path)

    def view_type_error(self):
        """Throw an error if no view type is used."""
        raise UNTLFormException(
            'Element "%s" needs a view type' % (self.name)
        )


# Element Form Definitions #

class Title(FormElement):
    def __init__(self, **kwargs):
        # Get the UNTL object associated with the form object.
        self.untl_object = kwargs.get('untl_object', None)
        # Set the attributes attached to the form element.
        self.name = 'title'
        self.label = 'Title'
        self.help_text = 'The name given to the resource'
        self.view_type = 'qualified-input'
        self.usage_link = self.create_link('title')
        super(Title, self).__init__(**kwargs)
        self.qualifier_vocab = 'title-qualifiers'
        self.qualifier_dd = get_qualifier_dict(
            self.vocabularies,
            self.qualifier_vocab
        )


class Identifier(FormElement):
    def __init__(self, **kwargs):
        # Get the UNTL object associated with the form object.
        self.untl_object = kwargs.get('untl_object', None)
        # Set the attributes attached to the form element.
        self.name = 'identifier'
        self.label = 'Identifier'
        self.help_text = "A unique code or 'permanent name' for a resource"
        self.view_type = 'qualified-input'
        self.usage_link = self.create_link('identifier')
        super(Identifier, self).__init__(**kwargs)
        self.qualifier_vocab = 'identifier-qualifiers'
        self.qualifier_dd = get_qualifier_dict(
            self.vocabularies,
            self.qualifier_vocab
        )


class Note(FormElement):
    def __init__(self, **kwargs):
        # Get the UNTL object associated with the form object.
        self.untl_object = kwargs.get('untl_object', None)
        # Set the attributes attached to the form element.
        self.name = 'note'
        self.label = 'Note'
        self.help_text = ('A "catch-all" field for additional information '
                          'important for users (Display Note) or for internal '
                          'maintenance (Non-Displaying Note)')
        self.view_type = 'textbox'
        self.usage_link = self.create_link('note')
        super(Note, self).__init__(**kwargs)
        self.qualifier_vocab = 'note-qualifiers'
        self.qualifier_dd = get_qualifier_dict(
            self.vocabularies,
            self.qualifier_vocab
        )


class Institution(FormElement):
    def __init__(self, **kwargs):
        # Get the UNTL object associated with the form object.
        self.untl_object = kwargs.get('untl_object', None)
        # Set the attributes attached to the form element.
        self.name = 'institution'
        self.label = 'Institution'
        self.help_text = ('The institution or administrating unit that owns '
                          'the original resource')
        self.view_type = 'dd-value-no-qualifier'
        self.usage_link = self.create_link('institution')
        super(Institution, self).__init__(**kwargs)
        self.content_vocab = 'institutions'
        # Get the content dictionary for the drop down list.
        self.content_dd = get_content_dict(
            self.vocabularies,
            self.content_vocab
        )


class Collection(FormElement):
    def __init__(self, **kwargs):
        # Get the UNTL object associated with the form object.
        self.untl_object = kwargs.get('untl_object', None)
        # Set the attributes attached to the form element.
        self.name = 'collection'
        self.label = 'Collection'
        self.help_text = 'Name of the collection in which the resource belongs'
        self.view_type = 'dd-value-no-qualifier'
        self.usage_link = self.create_link('collection')
        super(Collection, self).__init__(**kwargs)
        self.content_vocab = 'collections'
        # Get the content dictionary for the drop down list.
        self.content_dd = get_content_dict(
            self.vocabularies,
            self.content_vocab
        )


class Subject(FormElement):
    def __init__(self, **kwargs):
        # Get the UNTL object associated with the form object.
        self.untl_object = kwargs.get('untl_object', None)
        # Set the attributes attached to the form element.
        self.name = 'subject'
        self.label = 'Subject'
        self.help_text = ('Topic words and phrases that succinctly describe '
                          'the content of the resource')
        self.view_type = 'qualified-input'
        self.usage_link = self.create_link('subject')
        super(Subject, self).__init__(**kwargs)
        self.qualifier_vocab = 'subject-qualifiers'
        self.qualifier_dd = get_qualifier_dict(
            self.vocabularies,
            self.qualifier_vocab
        )


class Creator(FormElement):
    def __init__(self, **kwargs):
        # Get the UNTL object associated with the form object.
        self.untl_object = kwargs.get('untl_object', None)
        # Set the attributes attached to the form element.
        self.name = 'creator'
        self.label = 'Creator'
        self.qualifier_name = 'role'
        self.help_text = ('The person, agency, or organization primarily '
                          'responsible for creating the intellectual '
                          'content of the resource')
        self.view_type = 'none'
        self.usage_link = self.create_link('creator')
        self.has_children = True
        self.child_sort = [
            'name',
            'type',
            'role',
            'info',
        ]
        super(Creator, self).__init__(**kwargs)


class PrimarySource(FormElement):
    def __init__(self, **kwargs):
        # Get the UNTL object associated with the form object.
        self.untl_object = kwargs.get('untl_object', None)
        # Set the attributes attached to the form element.
        self.name = 'primarySource'
        self.label = 'Primary Source'
        self.help_text = 'Designates firsthand accounts of historical subjects'
        self.view_type = 'radio-no-qualifier'
        self.repeatable = False
        self.usage_link = self.create_link('primary-source')
        super(PrimarySource, self).__init__(**kwargs)


class Description(FormElement):
    def __init__(self, **kwargs):
        # Get the UNTL object associated with the form object.
        self.untl_object = kwargs.get('untl_object', None)
        # Set the attributes attached to the form element.
        self.name = 'description'
        self.label = 'Description'
        self.help_text = ('Statements summarizing the content and physical '
                          'aspects of the resource')
        self.view_type = 'textbox'
        self.usage_link = self.create_link('description')
        super(Description, self).__init__(**kwargs)
        self.qualifier_vocab = 'description-qualifiers'
        self.qualifier_dd = get_qualifier_dict(
            self.vocabularies,
            self.qualifier_vocab
        )


class Date(FormElement):
    def __init__(self, **kwargs):
        # Get the UNTL object associated with the form object.
        self.untl_object = kwargs.get('untl_object', None)
        # Set the attributes attached to the form element.
        self.name = 'date'
        self.label = 'Date'
        self.help_text = ('Date that the resource was originally created, '
                          'harvested from the web, or submitted to and '
                          'accepted by a third party')
        self.view_type = 'qualified-input'
        self.usage_link = self.create_link('date')
        super(Date, self).__init__(**kwargs)
        self.qualifier_vocab = 'date-qualifiers'
        self.qualifier_dd = get_qualifier_dict(
            self.vocabularies,
            self.qualifier_vocab
        )
        # Special form definition for digitized date.
        if self.untl_object.qualifier == 'digitized':
            self.editable = False
            self.editable_qualifiers = False


class Publisher(FormElement):
    def __init__(self, **kwargs):
        # Get the UNTL object associated with the form object.
        self.untl_object = kwargs.get('untl_object', None)
        # Set the attributes attached to the form element.
        self.name = 'publisher'
        self.label = 'Publisher'
        self.help_text = 'The publisher of the original work'
        self.view_type = 'none'
        self.usage_link = self.create_link('publisher')
        self.has_children = True
        self.child_sort = [
            'name',
            'location',
            'info',
        ]
        super(Publisher, self).__init__(**kwargs)


class Contributor(FormElement):
    def __init__(self, **kwargs):
        # Get the UNTL object associated with the form object.
        self.untl_object = kwargs.get('untl_object', None)
        # Set the attributes attached to the form element.
        self.name = 'contributor'
        self.label = 'Contributor'
        self.qualifier_name = 'role'
        self.help_text = ('The name of a person or organization that has '
                          'played an important but secondary role in creating '
                          'the content of the resource and is not specified '
                          'in the creator element')
        self.view_type = 'none'
        self.usage_link = self.create_link('contributor')
        self.has_children = True
        self.child_sort = [
            'name',
            'type',
            'role',
            'info',
        ]
        super(Contributor, self).__init__(**kwargs)


class Source(FormElement):
    def __init__(self, **kwargs):
        # Get the UNTL object associated with the form object.
        self.untl_object = kwargs.get('untl_object', None)
        # Set the attributes attached to the form element.
        self.name = 'source'
        self.label = 'Source'
        self.help_text = ('Information about a resource or event from which '
                          'the current resource is derived')
        self.view_type = 'qualified-input'
        self.usage_link = self.create_link('source')
        super(Source, self).__init__(**kwargs)
        self.qualifier_vocab = 'sourceQualifiers'
        self.qualifier_dd = get_qualifier_dict(
            self.vocabularies,
            self.qualifier_vocab
        )


class Language(FormElement):
    def __init__(self, **kwargs):
        # Get the UNTL object associated with the form object.
        self.untl_object = kwargs.get('untl_object', None)
        # Set the attributes attached to the form element.
        self.name = 'language'
        self.label = 'Language'
        self.help_text = "The language of the resource's content"
        self.view_type = 'dd-value-no-qualifier'
        self.usage_link = self.create_link('language')
        super(Language, self).__init__(**kwargs)
        self.content_vocab = 'languages'
        self.content_dd = get_content_dict(
            self.vocabularies,
            self.content_vocab
        )


class Coverage(FormElement):
    def __init__(self, **kwargs):
        # Get the UNTL object associated with the form object.
        self.untl_object = kwargs.get('untl_object', None)
        # Set the attributes attached to the form element.
        self.name = 'coverage'
        self.label = 'Coverage'
        self.help_text = ('Geographic region, historic era, and specific date '
                          'or range of dates covered by the resource content')
        self.view_type = 'qualified-input'
        self.usage_link = self.create_link('coverage')
        super(Coverage, self).__init__(**kwargs)
        self.qualifier_vocab = 'coverage-qualifiers'
        self.qualifier_dd = get_qualifier_dict(
            self.vocabularies,
            self.qualifier_vocab
        )


class ResourceType(FormElement):
    def __init__(self, **kwargs):
        # Get the UNTL object associated with the form object.
        self.untl_object = kwargs.get('untl_object', None)
        # Set the attributes attached to the form element.
        self.name = 'resourceType'
        self.label = 'Resource Type'
        self.help_text = 'The kind of item that best describes the resource'
        self.view_type = 'dd-value-no-qualifier'
        self.usage_link = self.create_link('resource-type')
        super(ResourceType, self).__init__(**kwargs)
        self.content_vocab = 'resource-types'
        # Get the content dictionary for the drop down list.
        self.content_dd = get_content_dict(
            self.vocabularies,
            self.content_vocab
        )


class Relation(FormElement):
    def __init__(self, **kwargs):
        # Get the UNTL object associated with the form object.
        self.untl_object = kwargs.get('untl_object', None)
        # Set the attributes attached to the form element.
        self.name = 'relation'
        self.label = 'Relation'
        self.help_text = ('Information about another resource that is related '
                          'to the current resource')
        self.view_type = 'qualified-input'
        self.qualifier_vocab = 'relation-qualifiers'
        self.usage_link = self.create_link('relation')
        super(Relation, self).__init__(**kwargs)
        self.qualifier_vocab = 'relation-qualifiers'
        self.qualifier_dd = get_qualifier_dict(
            self.vocabularies,
            self.qualifier_vocab
        )


class Format(FormElement):
    def __init__(self, **kwargs):
        # Get the UNTL object associated with the form object.
        self.untl_object = kwargs.get('untl_object', None)
        # Set the attributes attached to the form element.
        self.name = 'format'
        self.label = 'Format'
        self.help_text = 'The digital manifestation of the resource'
        self.view_type = 'dd-value-no-qualifier'
        self.usage_link = self.create_link('format')
        super(Format, self).__init__(**kwargs)
        self.content_vocab = 'formats'
        # Get the content dictionary for the drop down list.
        self.content_dd = get_content_dict(
            self.vocabularies,
            self.content_vocab
        )


class Rights(FormElement):
    def __init__(self, **kwargs):
        # Get the UNTL object associated with the form object.
        self.untl_object = kwargs.get('untl_object', None)
        # Set the attributes attached to the form element.
        self.name = 'rights'
        self.label = 'Rights'
        self.help_text = ('Information about licenses or rights for the '
                          'resource and level of access that will be '
                          'allowed to users')
        self.view_type = 'qualified-input'
        self.usage_link = self.create_link('rights')
        super(Rights, self).__init__(**kwargs)
        self.qualifier_vocab = 'rights-qualifiers'
        self.qualifier_dd = get_qualifier_dict(
            self.vocabularies,
            self.qualifier_vocab
        )


class Degree(FormElement):
    def __init__(self, **kwargs):
        # Get the UNTL object associated with the form object.
        self.untl_object = kwargs.get('untl_object', None)
        # Set the attributes attached to the form element.
        self.name = 'degree'
        self.label = 'Degree'
        self.help_text = ('Information related to theses and dissertations or '
                          'other items created within the UNT community')
        self.view_type = 'qualified-input'
        self.usage_link = self.create_link('degree-information')
        super(Degree, self).__init__(**kwargs)
        self.qualifier_vocab = 'degree-information'
        self.qualifier_dd = get_qualifier_dict(
            self.vocabularies,
            self.qualifier_vocab
        )


class Meta(FormElement):
    def __init__(self, **kwargs):
        # Get the UNTL object associated with the form object.
        self.untl_object = kwargs.get('untl_object', None)
        # Set the attributes attached to the form element.
        self.name = 'meta'
        self.repeatable = False
        self.label = 'Meta'
        self.editable_qualifiers = False
        self.help_text = ('Information captured by the system including the '
                          'most recent metadata editor')
        self.usage_link = self.create_link('meta-information')
        self.get_meta_attributes(**kwargs)
        super(Meta, self).__init__(**kwargs)
        self.qualifier_vocab = 'meta-qualifiers'
        self.qualifier_dd = get_qualifier_dict(
            self.vocabularies,
            self.qualifier_vocab
        )

    def get_meta_attributes(self, **kwargs):
        """Determine the form attributes for the meta field."""
        superuser = kwargs.get('superuser', False)
        if (self.untl_object.qualifier == 'recordStatus' or
                self.untl_object.qualifier == 'system'):
            if superuser:
                self.editable = True
                self.repeatable = True
            else:
                self.editable = False
            self.view_type = 'qualified-input'
        elif self.untl_object.qualifier == 'hidden':
            self.label = 'Object Hidden'
            self.view_type = 'radio'
        else:
            self.editable = False
            self.view_type = 'qualified-input'


class Citation(FormElement):
    def __init__(self, **kwargs):
        # Get the UNTL object associated with the form object.
        self.untl_object = kwargs.get('untl_object', None)
        # Set the attributes attached to the form element.
        self.name = 'citation'
        self.label = 'Citation'
        self.help_text = 'Citation information related to the source item'
        self.view_type = 'qualified-input'
        self.usage_link = self.create_link('citation')
        super(Citation, self).__init__(**kwargs)
        self.qualifier_vocab = 'citationQualifiers'
        self.qualifier_dd = get_qualifier_dict(
            self.vocabularies,
            self.qualifier_vocab
        )


class Info(FormElement):
    def __init__(self, **kwargs):
        # Get the UNTL object associated with the form object.
        self.untl_object = kwargs.get('untl_object', None)
        # Set the attributes attached to the form element.
        self.name = 'info'
        self.label = 'Info'
        self.help_text = ('Additional information about the %s related to the '
                          'specific item' % kwargs['parent_tag'])
        self.view_type = 'inputbox'
        super(Info, self).__init__(**kwargs)


class Type(FormElement):
    def __init__(self, **kwargs):
        # Get the UNTL object associated with the form object.
        self.untl_object = kwargs.get('untl_object', None)
        # Set the attributes attached to the form element.
        self.name = 'type'
        self.label = 'Type'
        self.help_text = ('Used to designate if a %s is an individual or an '
                          'organization' % kwargs['parent_tag'])
        self.view_type = 'dd-value-no-qualifier'
        super(Type, self).__init__(**kwargs)
        self.qualifier_vocab = 'agent-type'
        self.qualifier_dd = get_qualifier_dict(
            self.vocabularies,
            self.qualifier_vocab
        )


class Name(FormElement):

    # Determines which help text to use based on the parent element.
    HELP_TEXT_DICT = {
        'creator': ('The name of a person, organization, or event '
                    '(conference, meeting, etc.) associated in some way '
                    'with the resource'),
        'contributor': ('The name of a person, organization, or event '
                        '(conference, meeting, etc.) associated in some way '
                        'with the resource'),
        'publisher': ('The name of the person or organization that '
                      'published the item'),
    }

    def __init__(self, **kwargs):
        # Get the UNTL object associated with the form object.
        self.untl_object = kwargs.get('untl_object', None)
        # Set the attributes attached to the form element.
        self.name = 'name'
        self.label = 'Name'
        self.help_text = self.HELP_TEXT_DICT[kwargs['parent_tag']]
        self.view_type = 'inputbox'
        super(Name, self).__init__(**kwargs)


class Role(FormElement):

    # Determines which help text to use based on the parent element.
    HELP_TEXT_DICT = {
        'creator': ('The role that the person or organization played in the '
                    'creation of the item'),
        'contributor': ('The role that the person or organization played in '
                        'the creation or lifecycle of the item'),
    }

    def __init__(self, **kwargs):
        # Get the UNTL object associated with the form object.
        self.untl_object = kwargs.get('untl_object', None)
        # Set the attributes attached to the form element.
        self.name = 'role'
        self.label = 'Role'
        self.help_text = self.HELP_TEXT_DICT[kwargs['parent_tag']]
        self.view_type = 'dd-qualifier'
        super(Role, self).__init__(**kwargs)
        self.qualifier_vocab = 'agent-qualifiers'
        self.qualifier_dd = get_qualifier_dict(
            self.vocabularies,
            self.qualifier_vocab
        )


class Location(FormElement):
    def __init__(self, **kwargs):
        # Get the UNTL object associated with the form object.
        self.untl_object = kwargs.get('untl_object', None)
        # Set the attributes attached to the form element.
        self.name = 'location'
        self.label = 'Location'
        self.help_text = 'The place of publication of the original work'
        self.view_type = 'inputbox'
        super(Location, self).__init__(**kwargs)

UNTL_GROUP_DISPATCH = {
    'title': FormGroup,
    'identifier': FormGroup,
    'note': FormGroup,
    'institution': FormGroup,
    'collection': FormGroup,
    'subject': FormGroup,
    'creator': FormGroup,
    'primarySource': FormGroup,
    'description': FormGroup,
    'date': FormGroup,
    'publisher': FormGroup,
    'contributor': FormGroup,
    'source': FormGroup,
    'language': FormGroup,
    'coverage': CoverageGroup,
    'resourceType': FormGroup,
    'relation': FormGroup,
    'format': FormGroup,
    'rights': RightsGroup,
    'degree': DegreeGroup,
    'meta': FormGroup,
    'citation': CitationGroup,
    'info': FormGroup,
    'type': FormGroup,
    'name': FormGroup,
    'role': FormGroup,
    'location': FormGroup,
    'hidden': HiddenGroup,
}

UNTL_FORM_DISPATCH = {
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
    'citation': Citation,
    'info': Info,
    'type': Type,
    'name': Name,
    'role': Role,
    'location': Location,
}
