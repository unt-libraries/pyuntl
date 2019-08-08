import os
from unittest.mock import patch

import pytest
from lxml.etree import Element, tostring, fromstring

from pyuntl import (metadata_generator as mg, untl_structure as us,
                    etd_ms_structure as es, highwire_structure as hs)


def test_MetadataGeneratorException():
    msg = 'Throw this'
    try:
        raise mg.MetadataGeneratorException(msg)
    except mg.MetadataGeneratorException as err:
        assert str(err) == msg


def test_py2dict():
    """Test UNTL Elements are converted to a dictionary."""
    title = us.Title(qualifier='serialtitle', content='The Bronco')
    name = us.Name(content='Case, J.')
    creator = us.Creator(qualifier='aut')
    creator.add_child(name)
    elements = us.Metadata()
    elements.add_child(title)
    elements.add_child(creator)
    metadata_dict = mg.py2dict(elements)
    assert metadata_dict == {'title': [{'qualifier': 'serialtitle',
                                        'content': 'The Bronco'}],
                             'creator': [{'qualifier': 'aut',
                                          'content': {'name': 'Case, J.'}}]}


def test_etd_ms_py2dict():
    """Test ETD MS elements are converted to a dictionary."""
    title = es.ETD_MSTitle(qualifier='officialtitle',
                           content='A Good Dissertation')
    grantor = es.ETD_MSDegreeGrantor(content='UNT')
    degree = es.ETD_MSDegree()
    degree.add_child(grantor)
    name = es.ETD_MSDegreeName(content='Case, J.')
    contributor = es.ETD_MSContributor(role='chair', children=[name])
    subject = es.ETD_MSSubject(content='dog', scheme='LC')
    elements = es.ETD_MS()
    elements.add_child(title)
    elements.add_child(degree)
    elements.add_child(contributor)
    elements.add_child(subject)
    metadata_dict = mg.etd_ms_py2dict(elements)
    assert metadata_dict == {'title': [{'qualifier': 'officialtitle',
                                        'content': 'A Good Dissertation'}],
                             'degree': [{'content': {'grantor': 'UNT'}}],
                             'contributor': [{'role': 'chair', 'content': 'Case, J.'}],
                             'subject': [{'scheme': 'LC',
                                          'content': 'dog'}]}


def test_pydict2xml(tmpdir):
    """Test the metadata file is written."""
    metadata_dict = {'title': [{'qualifier': 'serialtitle',
                                'content': 'A Title'}],
                     'creator': [{'qualifier': 'aut',
                                  'content': {'name': 'Noway, José'}}]}
    xml_file = os.path.join(tmpdir, 'meta.xml')
    mg.pydict2xml(xml_file, metadata_dict)
    with open(xml_file) as xml_f:
        text = xml_f.read()
    assert text == ('<?xml version="1.0" encoding="UTF-8"?>\n'
                    '<metadata>\n'
                    '  <title qualifier="serialtitle">A Title</title>\n'
                    '  <creator qualifier="aut">\n'
                    '    <name>Noway, José</name>\n'
                    '  </creator>\n'
                    '</metadata>\n')


@patch('builtins.open', side_effect=OSError)
def test_pydict2xml_raises_MetadataGeneratorException(mock_open):
    """Test MetadataGeneratorException is raised on other exception."""
    path = '/some/path/meta.xml'
    with pytest.raises(mg.MetadataGeneratorException) as err:
        mg.pydict2xml(path, {'not': [{'gonna': 'use'}]})
    msg = 'Failed to create an XML file. Filename: {}'.format(path)
    assert err.value.args[0] == msg
    mock_open.assert_called_once_with(path, 'wb')


def test_pydict2xmlstring_no_root_namespace_no_nsmap():
    metadata_dict = {'title': [{'qualifier': 'serialtitle',
                                'content': 'A Title'}],
                     'creator': [{'qualifier': 'aut',
                                  'content': {'name': 'Noway, José'}}]}
    xml = mg.pydict2xmlstring(metadata_dict)
    assert xml.decode('utf-8') == ('<?xml version="1.0" encoding="UTF-8"?>\n'
                                   '<metadata>\n'
                                   '  <title qualifier="serialtitle">A Title</title>\n'
                                   '  <creator qualifier="aut">\n'
                                   '    <name>Noway, José</name>\n'
                                   '  </creator>\n'
                                   '</metadata>\n')


def test_pydict2xmlstring_root_namespace_attributes_nsmap():
    metadata_dict = {'title': [{'qualifier': 'officialtitle',
                                'content': 'A Dissertation'}],
                     'degree': [{'content': {'grantor': 'UNT'}}],
                     'contributor': [{'role': 'chair', 'content': 'Case, J.'}],
                     'subject': [{'scheme': 'LC',
                                  'content': 'dog'}]}
    xml = mg.pydict2xmlstring(metadata_dict,
                              root_attributes={'schemaLocation': 'http://example.org/schema'},
                              root_namespace='{http://purl.org/dc/elements/1.1/}',
                              namespace_map={'dc': 'http://purl.org/dc/elements/1.1/'})
    assert xml.decode('utf-8') == ('<?xml version="1.0" encoding="UTF-8"?>\n'
                                   '<dc:metadata xmlns:dc="http://purl.org/dc/elements/1.1/"'
                                   ' schemaLocation="http://example.org/schema">\n'
                                   '  <title qualifier="officialtitle">A Dissertation</title>\n'
                                   '  <contributor role="chair">Case, J.</contributor>\n'
                                   '  <subject scheme="LC">dog</subject>\n'
                                   '  <degree>\n'
                                   '    <grantor>UNT</grantor>\n'
                                   '  </degree>\n'
                                   '</dc:metadata>\n')


def test_pydict2xmlstring_no_root_namespace_nsmap():
    metadata_dict = {'title': [{'qualifier': 'serialtitle',
                                'content': 'A Title'}],
                     'creator': [{'qualifier': 'aut',
                                  'content': {'name': 'Noway, José'}}]}
    xml = mg.pydict2xmlstring(metadata_dict,
                              namespace_map={'dc': 'http://purl.org/dc/elements/1.1/'})
    assert xml.decode('utf-8') == ('<?xml version="1.0" encoding="UTF-8"?>\n'
                                   '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
                                   '  <title qualifier="serialtitle">A Title</title>\n'
                                   '  <creator qualifier="aut">\n'
                                   '    <name>Noway, José</name>\n'
                                   '  </creator>\n'
                                   '</metadata>\n')


def test_create_dict_subelement():
    root = Element('root', nsmap={'animal': 'http://example.com/animal'})
    mg.create_dict_subelement(root,
                              'dog',
                              'Harold',
                              attribs={'role': 'pet'},
                              namespace='{http://example.com/animal}')
    xml = tostring(root, pretty_print=True)
    assert xml.decode('utf-8') == ('<root xmlns:animal="http://example.com/animal">\n'
                                   '  <animal:dog role="pet">Harold</animal:dog>\n'
                                   '</root>\n')


def test_create_dict_subelement_no_attribs():
    root = Element('root', nsmap={'animal': 'http://example.com/animal'})
    mg.create_dict_subelement(root,
                              'dog',
                              'Harold',
                              namespace='{http://example.com/animal}')
    xml = tostring(root, pretty_print=True)
    assert xml.decode('utf-8') == ('<root xmlns:animal="http://example.com/animal">\n'
                                   '  <animal:dog>Harold</animal:dog>\n'
                                   '</root>\n')


def test_create_dict_subelement_no_namespace():
    root = Element('root')
    mg.create_dict_subelement(root, 'dog', 'Harold', attribs={'role': 'pet'})
    xml = tostring(root, pretty_print=True)
    assert xml.decode('utf-8') == ('<root>\n'
                                   '  <dog role="pet">Harold</dog>\n'
                                   '</root>\n')


def test_create_dict_subelement_no_extra_data():
    root = Element('root')
    mg.create_dict_subelement(root, 'dog', 'Harold')
    xml = tostring(root, pretty_print=True)
    assert xml.decode('utf-8') == ('<root>\n'
                                   '  <dog>Harold</dog>\n'
                                   '</root>\n')


def test_create_dict_subelement_degree_order_handling():
    # Order should be name, level, discipline, grantor.
    root = Element('root')
    mg.create_dict_subelement(root,
                              'degree',
                              content={'discipline': 'Chemistry',
                                       'level': 'Masters',
                                       'grantor': 'UNT',
                                       'name': 'foo'})
    xml = tostring(root, pretty_print=True)
    assert xml.decode('utf-8') == ('<root>\n'
                                   '  <degree>\n'
                                   '    <name>foo</name>\n'
                                   '    <level>Masters</level>\n'
                                   '    <discipline>Chemistry</discipline>\n'
                                   '    <grantor>UNT</grantor>\n'
                                   '  </degree>\n'
                                   '</root>\n')


def test_create_dict_subelement_content_dict_not_degree():
    root = Element('root')
    content = {'foo': 'one', 'bar': 'two'}
    mg.create_dict_subelement(root, 'stuff', content=content)
    # Check the content keys are children of the stuff element.
    assert root[0].tag == 'stuff'
    assert len(list(root[0])) == 2
    for key, value in content.items():
        assert root[0].find(key).text == value


def test_highwiredict2xmlstring():
    issue = hs.CitationIssue(content='1')
    title = hs.CitationTitle(content='Important paper')
    elements = [issue, title]
    xml = mg.highwiredict2xmlstring(elements, ordering=['citation_title',
                                                        'citation_issue'])
    expected_xml = (b'<?xml version="1.0" encoding="UTF-8"?>\n'
                    b'<metadata>\n'
                    b'  <meta content="Important paper" name="citation_title"/>\n'
                    b'  <meta content="1" name="citation_issue"/>\n'
                    b'</metadata>\n')

    # Get a sorted list of attributes for child elements in the generated and expected XML.
    generated_tree = fromstring(xml)
    generated_attribs = [child.attrib for child in generated_tree]
    generated_attribs = sorted(generated_attribs, key=lambda i: (i['content'], i['name']))
    expected_attribs = [child.attrib for child in fromstring(expected_xml)]
    expected_attribs = sorted(expected_attribs, key=lambda i: (i['content'], i['name']))
    assert expected_attribs == generated_attribs

    # Our generated XML has a `metadata` element with all `meta` element children.
    assert generated_tree.tag == 'metadata'
    for child in generated_tree:
        assert child.tag == 'meta'


def test_breakString_shorter_than_width_with_offset():
    line = mg.breakString('Hello world', width=79, firstLineOffset=0)
    assert line == 'Hello world'


def test_breakString_longer_than_width_with_offset():
    # String is shorter than width but longer than width - firstLineOffset.
    line = mg.breakString('Hello world', width=12, firstLineOffset=4)
    # Line has been split to prevent surpassing width - firstLineOffset length.
    assert line == 'Hello\n world'


def test_breakString_longer_than_width_with_offset_no_space():
    line = mg.breakString('antidisestablishmentarianism',
                          width=10,
                          firstLineOffset=4)
    # No space to split on, so line is returned over the specified width.
    assert line == 'antidisestablishmentarianism'


@pytest.mark.xfail(reason='We may want to split on consecutive space chars')
def test_breakString_multiple_consecutive_space_chars():
    line = mg.breakString('Hello  world', width=12, firstLineOffset=4)
    # Currently breakString doesn't split if there are consecutive space chars.
    # Is this to not double split if one space char is an endline?
    # Should we eliminate consecutive spaces before processing the string?
    assert line == 'Hello\n  world'


def test_writeANVLString():
    elements = {'issue': [{'content': '1'}],
                'title': [{'content': 'Important Paper'},
                          {'content': 'Another Paper'}]}
    anvl = mg.writeANVLString(elements, ordering=['title', 'issue'])
    assert anvl == ('title: Important Paper\n'
                    'title: Another Paper\n'
                    'issue: 1')
