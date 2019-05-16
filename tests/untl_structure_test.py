# -*- coding: utf-8 -*-
import pytest
from pyuntl import untl_structure


def test_UNTLElement_init():
    """Check initialized UNTLElement."""
    element = untl_structure.UNTLElement(content='test_content',
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
    element = untl_structure.UNTLElement()
    element.set_qualifier('  test_qualifier ')
    assert element.qualifier == 'test_qualifier'


def test_UNTLElement_set_qualifier_exception():
    """Test a qualifier must be allowed to set one."""
    element = untl_structure.UNTLElement()
    element.allows_qualifier = False
    with pytest.raises(untl_structure.UNTLStructureException):
        element.set_qualifier('test_qualifier')


def test_UNTLElement_add_child():
    """Test children in contained_children are allowed for adding."""
    child_element = untl_structure.UNTLElement()
    child_tag = 'child1'
    child_element.tag = child_tag
    element = untl_structure.UNTLElement()
    element.contained_children.append(child_tag)
    element.add_child(child_element)
    assert child_element in element.children


def test_UNTLElement_add_child_exception():
    """Test random children are not allowed."""
    child_element = untl_structure.UNTLElement()
    child_element.tag = 'child1'
    element = untl_structure.UNTLElement()
    with pytest.raises(untl_structure.UNTLStructureException):
        element.add_child(child_element)


def test_UNTLElement_set_content():
    """Test setting and stripping of content value."""
    element = untl_structure.UNTLElement()
    element.set_content('  содержани ')
    assert element.content == 'содержани'


def test_UNTLElement_set_content_exception():
    """Test content must be allowed to set it."""
    element = untl_structure.UNTLElement()
    element.allows_content = False
    with pytest.raises(untl_structure.UNTLStructureException):
        element.set_content('test_content')


def test_UNTLElement_add_form_qualifier_and_content():
    """Test form is created with qualifier and content passed."""
    element = untl_structure.UNTLElement()
    element.tag = 'title'
    qualifiers = ['test']
    element.add_form(vocabularies={'title-qualifiers': qualifiers},
                     qualifier='test_qualifier',
                     content='test_content')
    assert element.form.untl_object == element
    assert element.form.qualifier_dd == qualifiers


def test_UNTLElement_add_form_qualifier_only():
    """Test form is created with qualifier but not content passed."""
    element = untl_structure.UNTLElement()
    element.tag = 'creator'
    element.add_form(qualifier='test_qualifier')
    assert element.form.untl_object == element


def test_UNTLElement_add_form_content_only_no_parent_tag():
    """Test form is created with content but no qualifier nor parent tag."""
    element = untl_structure.UNTLElement()
    element.tag = 'primarySource'
    element.add_form(content='test_content')
    assert element.form.untl_object == element


def test_UNTLElement_add_form_content_and_parent_tag():
    """Test form is created with content and parent tag passed."""
    element = untl_structure.UNTLElement()
    element.tag = 'type'
    qualifiers = ['test']
    element.add_form(vocabularies={'agent-type': qualifiers},
                     content='test_content',
                     parent_tag='test_parent')
    assert element.form.untl_object == element
    assert element.form.qualifier_dd == qualifiers
    assert 'designate if a test_parent' in element.form.help_text


def test_UNTLElement_add_form_no_qualifier_no_content_no_parent_tag():
    """Test form is created with no parent tag, no content, no qualifier."""
    element = untl_structure.UNTLElement()
    element.tag = 'publisher'
    element.add_form()
    assert element.form.untl_object == element


def test_UNTLElement_add_form_no_qualifier_no_content_parent_tag():
    """Test form is created with parent tag, no content nor qualifier."""
    element = untl_structure.UNTLElement()
    element.tag = 'type'
    qualifiers = ['test']
    element.add_form(vocabularies={'agent-type': qualifiers},
                     parent_tag='test_parent')
    assert element.form.untl_object == element
    assert element.form.qualifier_dd == qualifiers


def test_UNTLElement_completeness():
    """Test there is a completeness score."""
    element = untl_structure.UNTLElement()
    assert isinstance(element.completeness, float)


def test_UNTLElement_record_length():
    """Check the record_length with meta field included."""
    # Create an element with collection and meta fields.
    root = untl_structure.UNTLElement()
    root.tag = 'metadata'
    root.contained_children = ['collection', 'meta']
    collection = untl_structure.UNTLElement(content='Colección')
    collection.tag = 'collection'
    root.add_child(collection)
    meta = untl_structure.UNTLElement(content='fake',
                                      qualifier='ark')
    meta.tag = 'meta'
    root.add_child(meta)
    # NOTE: in utf-8 length is 94:
    # "{'meta': [{'qualifier': 'ark', 'content': 'fake'}], 'collection': [{'content': 'Colección'}]}"  # noqa 
    # We are getting that it is length 100 for:
    # "{'meta': [{'qualifier': 'ark', 'content': 'fake'}], 'collection': [{'content': 'Colecci\xc3\xb3n'}]}"  # noqa
    assert root.record_length == 100


def test_UNTLElement_record_content_length():
    """Check the record_length with meta field excluded."""
    # Create an element with collection and meta fields.
    root = untl_structure.UNTLElement()
    root.tag = 'metadata'
    root.contained_children = ['collection', 'meta']
    collection = untl_structure.UNTLElement(content='Colección')
    collection.tag = 'collection'
    root.add_child(collection)
    meta = untl_structure.UNTLElement(content='fake',
                                      qualifier='ark')
    meta.tag = 'meta'
    root.add_child(meta)
    # NOTE: in utf-8 length is 43:
    # "{'collection': [{'content': 'Colección'}]}"
    # We are getting that it is length 49 for:
    # "{'collection': [{'content': 'Colecci\xc3\xb3n'}]}"
    assert root.record_content_length == 49
