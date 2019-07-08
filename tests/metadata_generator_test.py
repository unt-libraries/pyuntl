import os
from unittest.mock import patch

import pytest
from lxml.etree import Element, tostring

from pyuntl import (metadata_generator as mg, untl_structure as us,
                    etd_ms_structure as es)


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
    mock_open.assert_called_once_with(path, 'w', encoding='utf-8')


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
