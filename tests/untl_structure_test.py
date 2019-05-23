# -*- coding: utf-8 -*-
"""Unit tests for untl_structure."""

import pytest
from mock import patch
from lxml.etree import Element
from pyuntl import untl_structure as us, UNTL_PTH_ORDER
from pyuntl.form_logic import FormGroup, HiddenGroup, FormElement
from tests import VOCAB


def test_UNTLStructureException():
    """Check the error string."""
    msg = 'msg about error'
    exception = us.UNTLStructureException(msg)
    assert str(exception) == msg


def test_create_untl_xml_subelement_no_children():
    """Test subelement is added to tree with content and qualifier."""
    parent = Element('metadata')
    title = us.UNTLElement(content='A title',
                           qualifier='officialtitle')
    title.tag = 'title'
    subelement = us.create_untl_xml_subelement(parent, title, prefix='')
    assert subelement.text == title.content
    assert subelement.attrib['qualifier'] == title.qualifier


def test_create_untl_xml_subelement_children():
    """Test children are added as subelements to initial subelement."""
    parent = Element('metadata')
    contributor = us.UNTLElement(qualifier='cmp')
    contributor.tag = 'contributor'
    contributor.contained_children = ['name']
    name = us.UNTLElement(content='Bob, A.')
    name.tag = 'name'
    contributor.add_child(name)
    subelement = us.create_untl_xml_subelement(parent, contributor)
    assert subelement.attrib['qualifier'] == contributor.qualifier
    # Check that the first child's text is the name.
    assert subelement[0].text == name.content


def test_add_missing_children():
    """Test adding expected children that don't exist for a form."""
    required = ['title', 'format', 'publisher']
    parent = us.UNTLElement()
    parent.contained_children = required
    title_child = us.Title(content='A title',
                           qualifier='officialtitle')
    children = [title_child]
    parent.children = children
    padded_children = us.add_missing_children(required, children)
    # Now there are Format and Publisher elements after Title.
    assert len(padded_children) == 3
    assert isinstance(padded_children[1], us.Format)
    assert isinstance(padded_children[2], us.Publisher)


def test_UNTLElement_init():
    """Check initialized UNTLElement."""
    element = us.UNTLElement(content='test_content',
                             qualifier='test_qualifier')
    assert element.tag is None
    assert element.contained_children == []
    assert element.allows_content
    assert element.allows_qualifier
    assert element.qualifier == 'test_qualifier'
    assert element.children == []
    assert element.content == 'test_content'


def test_UNTLElement_set_qualifier():
    """Test setting and stripping of qualifier value."""
    element = us.UNTLElement()
    element.set_qualifier('  test_qualifier ')
    assert element.qualifier == 'test_qualifier'


def test_UNTLElement_set_qualifier_exception():
    """Test a qualifier must be allowed to set one."""
    element = us.UNTLElement()
    element.allows_qualifier = False
    with pytest.raises(us.UNTLStructureException):
        element.set_qualifier('test_qualifier')


def test_UNTLElement_add_child():
    """Test children in contained_children are allowed for adding."""
    child_element = us.UNTLElement()
    child_tag = 'child1'
    child_element.tag = child_tag
    element = us.UNTLElement()
    element.contained_children.append(child_tag)
    element.add_child(child_element)
    assert child_element in element.children


def test_UNTLElement_add_child_exception():
    """Test random children are not allowed."""
    child_element = us.UNTLElement()
    child_element.tag = 'child1'
    element = us.UNTLElement()
    with pytest.raises(us.UNTLStructureException):
        element.add_child(child_element)


def test_UNTLElement_set_content():
    """Test setting and stripping of content value."""
    element = us.UNTLElement()
    element.set_content(u'  содержани ')
    assert element.content == u'содержани'


def test_UNTLElement_set_content_exception():
    """Test content must be allowed to set it."""
    element = us.UNTLElement()
    element.allows_content = False
    with pytest.raises(us.UNTLStructureException):
        element.set_content('test_content')


def test_UNTLElement_add_form_qualifier_and_content():
    """Test form is created with qualifier and content passed."""
    element = us.UNTLElement()
    element.tag = 'title'
    qualifiers = ['test']
    element.add_form(vocabularies={'title-qualifiers': qualifiers},
                     qualifier='test_qualifier',
                     content='test_content')
    assert isinstance(element.form, FormElement)
    assert element.form.untl_object == element
    assert element.form.qualifier_dd == qualifiers


@patch('pyuntl.form_logic.Title.__init__', return_value=None)
def test_UNTLElement_add_form_qualifier_and_content_mocked(mock_title):
    """Verify FormElement subclass call with qualifier and content passed."""
    element = us.UNTLElement()
    element.tag = 'title'
    vocabularies = {'title-qualifiers': ['test']}
    qualifier = 'test_qualifier'
    content = 'test_content'
    element.add_form(vocabularies=vocabularies,
                     qualifier=qualifier,
                     content=content)
    mock_title.assert_called_once_with(vocabularies=vocabularies,
                                       qualifier_value=qualifier,
                                       input_value=content,
                                       untl_object=element,
                                       superuser=False)


def test_UNTLElement_add_form_qualifier_only():
    """Test form is created with qualifier but not content passed."""
    element = us.UNTLElement()
    element.tag = 'creator'
    element.add_form(qualifier='test_qualifier')
    assert isinstance(element.form, FormElement)
    assert element.form.untl_object == element


@patch('pyuntl.form_logic.Creator.__init__', return_value=None)
def test_UNTLElement_add_form_qualifier_only_mocked(mock_creator):
    """Verify FormElement subclass call with qualifier but not content passed."""
    element = us.UNTLElement()
    element.tag = 'creator'
    qualifier = 'test_qualifier'
    element.add_form(qualifier=qualifier)
    mock_creator.assert_called_once_with(vocabularies=None,
                                         qualifier_value=qualifier,
                                         untl_object=element,
                                         superuser=False)


def test_UNTLElement_add_form_content_only_no_parent_tag():
    """Test form is created with content but no qualifier nor parent tag."""
    element = us.UNTLElement()
    element.tag = 'primarySource'
    element.add_form(content='test_content')
    assert isinstance(element.form, FormElement)
    assert element.form.untl_object == element


@patch('pyuntl.form_logic.PrimarySource.__init__', return_value=None)
def test_UNTLElement_add_form_content_only_no_parent_tag_mocked(mock_ps):
    """Verify FormElement subclass call with content but no qualifier nor parent tag."""
    element = us.UNTLElement()
    element.tag = 'primarySource'
    content = 'test_content'
    element.add_form(content=content)
    mock_ps.assert_called_once_with(vocabularies=None,
                                    input_value=content,
                                    untl_object=element,
                                    superuser=False)


def test_UNTLElement_add_form_content_and_parent_tag():
    """Test form is created with content and parent tag passed."""
    element = us.UNTLElement()
    element.tag = 'type'
    qualifiers = ['test']
    element.add_form(vocabularies={'agent-type': qualifiers},
                     content='test_content',
                     parent_tag='test_parent')
    assert isinstance(element.form, FormElement)
    assert element.form.untl_object == element
    assert element.form.qualifier_dd == qualifiers
    assert 'designate if a test_parent' in element.form.help_text


@patch('pyuntl.form_logic.Type.__init__', return_value=None)
def test_UNTLElement_add_form_content_and_parent_tag_mocked(mock_type):
    """Verify FormElement subclass call with content and parent tag passed."""
    element = us.UNTLElement()
    element.tag = 'type'
    vocabularies = {'agent-type': ['test']}
    content = 'test_content'
    parent_tag = 'test_parent'
    element.add_form(vocabularies=vocabularies,
                     content=content,
                     parent_tag=parent_tag)
    mock_type.assert_called_once_with(vocabularies=vocabularies,
                                      input_value=content,
                                      untl_object=element,
                                      parent_tag='test_parent',
                                      superuser=False)


def test_UNTLElement_add_form_no_qualifier_no_content_no_parent_tag():
    """Test form is created with no parent tag, no content, no qualifier."""
    element = us.UNTLElement()
    element.tag = 'publisher'
    element.add_form()
    assert isinstance(element.form, FormElement)
    assert element.form.untl_object == element


@patch('pyuntl.form_logic.Publisher.__init__', return_value=None)
def test_UNTLElement_add_form_no_qualifier_no_content_no_parent_tag_mocked(mock_pub):
    """Verify FormElement subclass call with no parent tag, no content, no qualifier."""
    element = us.UNTLElement()
    element.tag = 'publisher'
    element.add_form()
    mock_pub.assert_called_once_with(vocabularies=None,
                                     untl_object=element,
                                     superuser=False)


def test_UNTLElement_add_form_no_qualifier_no_content_parent_tag():
    """Test form is created with parent tag, no content nor qualifier."""
    element = us.UNTLElement()
    element.tag = 'type'
    qualifiers = ['test']
    element.add_form(vocabularies={'agent-type': qualifiers},
                     parent_tag='test_parent')
    assert isinstance(element.form, FormElement)
    assert element.form.untl_object == element
    assert element.form.qualifier_dd == qualifiers


@patch('pyuntl.form_logic.Type.__init__', return_value=None)
def test_UNTLElement_add_form_no_qualifier_no_content_parent_tag_mocked(mock_type):
    """Verify FormElement subclass call with parent tag, no content nor qualifier."""
    element = us.UNTLElement()
    element.tag = 'type'
    vocabularies = {'agent-type': ['test']}
    parent_tag = 'test_parent'
    element.add_form(vocabularies=vocabularies,
                     parent_tag=parent_tag)
    mock_type.assert_called_once_with(vocabularies=vocabularies,
                                      untl_object=element,
                                      parent_tag=parent_tag,
                                      superuser=False)


def test_UNTLElement_completeness():
    """Test there is a completeness score."""
    element = us.UNTLElement()
    assert isinstance(element.completeness, float)


def test_UNTLElement_record_length():
    """Check the record_length with meta field included."""
    # Create an element with collection and meta fields.
    root = us.UNTLElement()
    root.tag = 'metadata'
    root.contained_children = ['collection', 'meta']
    collection = us.UNTLElement(content=u'Colección')
    collection.tag = 'collection'
    root.add_child(collection)
    meta = us.UNTLElement(content='fake',
                          qualifier='ark')
    meta.tag = 'meta'
    root.add_child(meta)
    # NOTE: in utf-8 length is 94:
    # "{'meta': [{'qualifier': 'ark', 'content': 'fake'}], 'collection': [{'content': 'Colección'}]}"  # noqa 
    # We are getting that it is length 97 for:
    # "{'meta': [{'content': 'fake', 'qualifier': 'ark'}], 'collection': [{'content': u'Colecci\xf3n'}]}"  # noqa
    assert root.record_length == 97


def test_UNTLElement_record_content_length():
    """Check the record_length with meta field excluded."""
    # Create an element with collection and meta fields.
    root = us.UNTLElement()
    root.tag = 'metadata'
    root.contained_children = ['collection', 'meta']
    collection = us.UNTLElement(content=u'Colección')
    collection.tag = 'collection'
    root.add_child(collection)
    meta = us.UNTLElement(content='fake',
                          qualifier='ark')
    meta.tag = 'meta'
    root.add_child(meta)
    # NOTE: in utf-8 length is 42:
    # "{'collection': [{'content': 'Colección'}]}"
    # We are getting that it is length 46 for:
    # "{'collection': [{'content': u'Colecci\xf3n'}]}"
    assert root.record_content_length == 46


@patch('pyuntl.untl_structure.FormGenerator.get_vocabularies', return_value=VOCAB)
def test_FormGenerator(_):
    """Test same UNTLElement subclasses are grouped together.

    Official and series titles should be in same group. A hidden
    group should be created if it doesn't exist.
    """
    creator = us.Creator(qualifier='')
    official_title = us.Title(content='A Title', qualifier='officialtitle')
    series_title = us.Title(content='Series', qualifier='seriestitle')
    children = [official_title, series_title, creator]
    form_elements = us.FormGenerator(children=children,
                                     sort_order=['title', 'creator', 'hidden'])
    # Check there is a title group with both official and series elements
    # a group for the creator, and a separate hidden group was created.
    assert len(form_elements.element_groups) == 3
    title_group = form_elements.element_groups[0].group_list
    assert len(title_group) == 2
    for title in title_group:
        assert isinstance(title, us.Title)
    creator_group = form_elements.element_groups[1].group_list
    assert len(creator_group) == 1
    assert isinstance(creator_group[0], us.Creator)
    hidden_group = form_elements.element_groups[2].group_list
    assert len(hidden_group) == 1
    assert isinstance(hidden_group[0], us.Meta)


@patch('pyuntl.untl_structure.FormGenerator.get_vocabularies', return_value=VOCAB)
def test_FormGenerator_hidden_is_alone(_):
    """Test Meta with Hidden qualifier is handled.

     A Meta element with qualifier of "hidden" gets a separate group
     from other Meta elements.
    """
    system = us.Meta(content='DC', qualifier='system')
    hidden = us.Meta(content='True', qualifier='hidden')
    children = [system, hidden]
    form_elements = us.FormGenerator(children=children,
                                     sort_order=['meta', 'hidden'])
    assert len(form_elements.element_groups) == 2
    assert isinstance(form_elements.element_groups[0], FormGroup)
    assert isinstance(form_elements.element_groups[1], HiddenGroup)
    assert not form_elements.adjustable_items


@patch('pyuntl.untl_structure.FormGenerator.get_vocabularies', return_value=VOCAB)
def test_FormGenerator_adjustable_items(_):
    """FormGroup types with data for adjusting form with JS are handled."""
    access = us.Rights(content='public', qualifier='access')
    hidden = us.Meta(content='True', qualifier='hidden')
    children = [access, hidden]
    sort_order = ['rights', 'hidden']
    fg = us.FormGenerator(children=children,
                          sort_order=sort_order)
    assert 'access' in fg.adjustable_items


@patch('urllib2.urlopen')
def test_FormGenerator_get_vocabularies(mock_urlopen):
    """Tests the vocabularies are returned."""
    mock_urlopen.return_value.read.return_value = str(VOCAB)
    vocabularies = us.FormGenerator(children=[], sort_order=['hidden'])
    vocabularies == VOCAB
    mock_urlopen.assert_called_once()


@patch('urllib2.urlopen', side_effect=Exception)
def test_FormGenerator_fails_without_vocab_service(mock_urlopen):
    """If vocabularies URL can't be reached, exception is raised.

    With urlopen patched, the vocabularies can't be reached, so trying
    to generate the form elements will raise an exception.
    """
    with pytest.raises(us.UNTLStructureException):
        us.FormGenerator(children=[],
                         sort_order=[])
    mock_urlopen.assert_called_once()


def test_Metadata_create_xml_string():
    """Test our metadata xml is written as expected string."""
    metadata = us.Metadata()
    title = us.Title(content=u'Colección', qualifier=u'seriestitle')
    description = us.Description(content=u'Adaption of "Fortuna te dé Dios, hijo"',
                                 qualifier=u'content')
    metadata.children = [title, description]
    expected_text = """<?xml version="1.0" encoding="UTF-8"?>
<metadata>
  <title qualifier="seriestitle">Colecci&#243;n</title>
  <description qualifier="content">Adaption of "Fortuna te d&#233; Dios, hijo"</description>
</metadata>\n"""
    assert metadata.create_xml_string() == expected_text


def test_Metadata_create_xml():
    """Test the metadata ElementTree representation."""
    metadata = us.Metadata()
    title_text = u'Colección'
    description_text = u'Adaption of "Fortuna te dé Dios, hijo"'
    name_text = u'Oudrid, C. (Cristóbal), 1825-1877.'
    title = us.Title(content=title_text, qualifier=u'seriestitle')
    description = us.Description(content=description_text,
                                 qualifier=u'content')
    contributor = us.Contributor(qualifier=u'cmp')
    type_ = us.Type(content=u'per')
    name = us.Name(content=name_text)
    contributor.add_child(type_)
    contributor.add_child(name)
    metadata.add_child(title)
    metadata.add_child(description)
    metadata.add_child(contributor)

    root = metadata.create_xml(useNamespace=False)
    assert root.tag == 'metadata'
    # Check are children are there in sorted order.
    assert root[0].tag == u'title'
    assert root[0].text == title_text
    assert root[0].get('qualifier') == u'seriestitle'
    assert root[1].tag == u'contributor'
    assert root[1].get('qualifier') == u'cmp'
    assert root[2].tag == u'description'
    assert root[2].text == description_text
    assert root[2].get('qualifier') == u'content'
    # Check that the contributor children are there.
    assert root[1][0].tag == 'type'
    assert root[1][1].tag == 'name'
    assert root[1][1].text == name_text


def test_Metadata_create_xml_use_namespace():
    """Check tag can include the namespace."""
    metadata = us.Metadata()
    metadata.add_child(us.Institution(content='UNT'))
    root = metadata.create_xml(useNamespace=True)
    assert root.tag == '{http://digital2.library.unt.edu/untl/}metadata'
    assert root[0].tag == '{http://digital2.library.unt.edu/untl/}institution'


def test_Metadata_create_element_dict():
    """Test a UNTL Python object converts to dictionary."""
    metadata = us.Metadata()
    title_text = u'An Official Title'
    series_text = u'The Series Title'
    name_text = u'Oudrid, C. (Cristóbal), 1825-1877.'
    title = us.Title(content=title_text, qualifier=u'officialtitle')
    series_title = us.Title(content=series_text, qualifier=u'seriestitle')
    contributor = us.Contributor(qualifier=u'cmp')
    type_ = us.Type(content=u'per')
    name = us.Name(content=name_text)
    contributor.add_child(type_)
    contributor.add_child(name)
    metadata.add_child(title)
    metadata.add_child(series_title)
    metadata.add_child(contributor)

    untl_dict = metadata.create_element_dict()
    assert untl_dict == {
        'contributor': [
            {'content': {'name': name_text, 'type': u'per'}, 'qualifier': u'cmp'}
        ],
        'title': [
            {'content': title_text, 'qualifier': u'officialtitle'},
            {'content': series_text, 'qualifier': u'seriestitle'}
        ]
    }


def test_Metadata_create_xml_file(tmpdir):
    """Test the UNTL XML file is created correctly.

    Uses pytest tmdir fixture for temporary file.
    """
    metadata = us.Metadata()
    title = us.Title(content=u'Colección', qualifier=u'seriestitle')
    description = us.Description(content=u'"Fortuna te dé Dios, hijo"',
                                 qualifier=u'content')
    contributor = us.Contributor(qualifier=u'cmp')
    type_ = us.Type(content=u'per')
    name = us.Name(content=u'Oudrid, C. (Cristóbal), 1825-1877.')
    contributor.add_child(type_)
    contributor.add_child(name)
    metadata.add_child(title)
    metadata.add_child(description)
    metadata.add_child(contributor)

    xml_file = tmpdir.join('untl.xml')
    metadata.create_xml_file(xml_file.strpath)
    assert xml_file.read() == (
        u'<?xml version="1.0" encoding="UTF-8"?>\n'
        u'<metadata>\n'
        u'  <title qualifier="seriestitle">Colecci&#243;n</title>\n'
        u'  <contributor qualifier="cmp">\n'
        u'    <type>per</type>\n'
        u'    <name>Oudrid, C. (Crist&#243;bal), 1825-1877.</name>\n'
        u'  </contributor>\n'
        u'  <description qualifier="content">"Fortuna te d&#233; Dios, hijo"</description>\n'
        u'</metadata>\n'
    )


def test_Metadata_create_xml_file_ascii_hex(tmpdir):
    """Test the UNTL XML file is created correctly.

    Uses pytest tmdir fixture for temporary file.
    """
    metadata = us.Metadata()
    title = us.Title(content=u'Colecci\xf3n', qualifier=u'seriestitle')
    description = us.Description(content=u'"Fortuna te d\xe9 Dios, hijo"',
                                 qualifier=u'content')
    contributor = us.Contributor(qualifier=u'cmp')
    type_ = us.Type(content=u'per')
    name = us.Name(content=u'Oudrid, C. (Crist\xf3bal), 1825-1877.')
    contributor.add_child(type_)
    contributor.add_child(name)
    metadata.add_child(title)
    metadata.add_child(description)
    metadata.add_child(contributor)

    xml_file = tmpdir.join('untl.xml')
    metadata.create_xml_file(xml_file.strpath)
    assert xml_file.read() == (
        u'<?xml version="1.0" encoding="UTF-8"?>\n'
        u'<metadata>\n'
        u'  <title qualifier="seriestitle">Colecci&#243;n</title>\n'
        u'  <contributor qualifier="cmp">\n'
        u'    <type>per</type>\n'
        u'    <name>Oudrid, C. (Crist&#243;bal), 1825-1877.</name>\n'
        u'  </contributor>\n'
        u'  <description qualifier="content">"Fortuna te d&#233; Dios, hijo"</description>\n'
        u'</metadata>\n'
    )


def test_Metadata_create_xml_file_exception_raised():
    """Test exception when XML file can't be written."""
    metadata = us.Metadata()
    with pytest.raises(us.UNTLStructureException):
        metadata.create_xml_file('/slkfjsldfjsdf/not/real')


def test_Metadata_sort_untl():
    """Test that elements are sorted correctly."""
    metadata = us.Metadata()
    child1 = us.UNTLElement()
    child1.tag = 'ziggy'
    child2 = us.UNTLElement()
    child2.tag = 'apple'
    child3 = us.UNTLElement()
    child3.tag = 'dash'
    metadata.children = [child1, child2, child3]
    # Sort by the tags in this order.
    metadata.sort_untl(['dash', 'ziggy', 'apple'])
    assert metadata.children == [child3, child1, child2]


def test_Metadata_validate():
    """Nothing is implemented in validate().

    This is here for coverage.
    """
    metadata = us.Metadata()
    assert metadata.validate() is None


@patch('pyuntl.untl_structure.FormGenerator.get_vocabularies', return_value=VOCAB)
def test_generate_form_data(_):
    """Test this returns a FormGenerator object."""
    metadata = us.Metadata()
    assert not metadata.children
    fg = metadata.generate_form_data(sort_order=UNTL_PTH_ORDER)
    assert isinstance(fg, us.FormGenerator)
    # Check missing children were added.
    assert len(metadata.children) == len(metadata.contained_children)
