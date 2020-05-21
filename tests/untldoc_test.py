import os
from copy import deepcopy
from io import BytesIO
from unittest.mock import patch

import pytest
from lxml.etree import fromstring
from rdflib import ConjunctiveGraph

from pyuntl import untldoc, untl_structure as us, dc_structure as dc


TEST_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)))

UNTL_DICTIONARY = {'title': [{'qualifier': 'officialtitle',
                              'content': 'Tres Actos'}],
                   'creator': [{'qualifier': 'aut',
                                'content': {'name': 'Last, Furston, 1807-1865.', 'type': 'per'}}],
                   'publisher': [{'content': {'name': 'Fake Publishing'}}],
                   'collection': [{'content': 'UNT'}],
                   'date': [{'content': '1944',
                             'qualifier': 'creation'}]}

UNTL_STRING = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<metadata>\n'
               '  <title qualifier="officialtitle">Tres Actos</title>\n'
               '  <creator qualifier="aut">\n'
               '    <name>Last, Furston, 1807-1865.</name>\n'
               '    <type>per</type>\n'
               '  </creator>\n'
               '  <publisher>\n'
               '    <name>Fake Publishing</name>\n'
               '  </publisher>\n'
               '  <date qualifier="creation">1944</date>\n'
               '  <collection>UNT</collection>\n'
               '</metadata>\n')

DC_DICTIONARY = {'title': [{'content': 'Tres Actos'}],
                 'creator': [{'content': 'Enhorn, Blair'}],
                 'publisher': [{'content': 'Fake Publishing'}],
                 'date': [{'content': '1944'}]}


def test_PyuntlException():
    msg = 'Throw this'
    try:
        raise untldoc.PyuntlException(msg)
    except untldoc.PyuntlException as err:
        assert str(err) == msg


def test_untlxml2py():
    """Verify children are correctly added from the UNTL XML."""
    xml = BytesIO(b'<?xml version="1.0" encoding="UTF-8"?>\n'
                  b'<metadata>\n'
                  b'  <title qualifier="officialtitle">Tres Actos</title>\n'
                  b'  <creator qualifier="aut">\n'
                  b'    <name>Last, Furston, 1807-1865.</name>\n'
                  b'  </creator>\n'
                  b'</metadata>\n')
    root = untldoc.untlxml2py(xml)
    assert isinstance(root, us.UNTLElement)
    assert root.tag == 'metadata'
    assert len(root.children) == 2
    assert root.children[0].tag == 'title'
    assert root.children[0].content == 'Tres Actos'
    assert root.children[0].qualifier == 'officialtitle'
    assert root.children[1].tag == 'creator'
    assert root.children[1].qualifier == 'aut'
    assert root.children[1].children[0].tag == 'name'
    assert root.children[1].children[0].content == 'Last, Furston, 1807-1865.'


def test_untlxml2py_namespace():
    """Namespace is removed from element.tag when building py object.

    Including xmlns in the xml prepends "{http://purl.org/dc/elements/1.1/}"
    to element tags, but untlxml2py will ignore that.
    """
    xml = BytesIO(b'<?xml version="1.0" encoding="UTF-8"?>\n'
                  b'<metadata xmlns="http://purl.org/dc/elements/1.1/">\n'
                  b'  <title qualifier="officialtitle">Tres Actos</title>\n'
                  b'</metadata>\n')
    root = untldoc.untlxml2py(xml)
    assert isinstance(root, us.UNTLElement)
    assert root.tag == 'metadata'
    assert root.children[0].tag == 'title'


def test_untlxml2py_non_UNTL_tag_raises_exception():
    xml = BytesIO(b'<?xml version="1.0" encoding="UTF-8"?>\n'
                  b'<metadata>\n'
                  b'  <dog>Bezos</dog>\n'
                  b'</metadata>\n')
    with pytest.raises(untldoc.PyuntlException) as err:
        untldoc.untlxml2py(xml)
    assert 'Element "dog" not in UNTL dispatch.' == err.value.args[0]


def test_untlxml2pydict():
    xml = BytesIO(UNTL_STRING.encode('utf-8'))
    untl_dict = untldoc.untlxml2pydict(xml)
    assert untl_dict == UNTL_DICTIONARY


def test_untlpy2dict():
    title = us.Title(qualifier='serialtitle', content='The Bronco')
    elements = us.Metadata()
    elements.add_child(title)
    untl_dict = untldoc.untlpy2dict(elements)
    assert untl_dict == {'title': [{'qualifier': 'serialtitle',
                                    'content': 'The Bronco'}]}


@pytest.mark.parametrize('input_indent, json_output',
                         [
                             (4, ('{\n'
                                  '    "title": [\n'
                                  '        {\n'
                                  '            "content": "The Bronco",\n'
                                  '            "qualifier": "serialtitle"\n'
                                  '        }\n'
                                  '    ]\n'
                                  '}')),
                             (None,
                              '{"title": [{"content": "The Bronco", "qualifier": "serialtitle"}]}')
                         ])
def test_generate_untl_json(input_indent, json_output):
    title = us.Title(qualifier='serialtitle', content='The Bronco')
    elements = us.Metadata()
    elements.add_child(title)
    untl_json = untldoc.generate_untl_json(elements, input_indent)
    assert untl_json == json_output


def test_untljson2py():
    untl_py = untldoc.untljson2py(
        '{"title": [{"content": "The Bronco", "qualifier": "serialtitle"}]}')
    assert untl_py.children[0].tag == 'title'
    assert untl_py.children[0].content == 'The Bronco'
    assert untl_py.children[0].qualifier == 'serialtitle'
    assert untl_py.tag == 'metadata'


def test_untlpydict2xml(tmpdir):
    xml_file = os.path.join(tmpdir, 'untl.xml')
    returned_value = untldoc.untlpydict2xml(xml_file, UNTL_DICTIONARY)
    # untlpydict2xml writes an XML file and returns None.
    assert returned_value is None
    with open(xml_file) as xml_f:
        assert xml_f.read() == UNTL_STRING


def test_untlpydict2xmlstring():
    xml_string = untldoc.untlpydict2xmlstring(UNTL_DICTIONARY)
    assert xml_string == UNTL_STRING.encode('utf-8')


def test_untldict2py():
    root = untldoc.untldict2py(UNTL_DICTIONARY)
    assert isinstance(root, us.UNTLElement)
    assert len(root.children) == 5
    assert root.tag == 'metadata'
    assert root.children[0].tag == 'title'
    assert root.children[0].content == 'Tres Actos'
    assert root.children[0].qualifier == 'officialtitle'
    assert root.children[1].tag == 'creator'
    assert root.children[1].qualifier == 'aut'
    assert root.children[1].children[0].tag == 'name'
    assert root.children[1].children[0].content == 'Last, Furston, 1807-1865.'
    assert root.children[2].tag == 'publisher'
    assert root.children[2].children[0].tag == 'name'
    assert root.children[2].children[0].content == 'Fake Publishing'
    assert root.children[3].tag == 'collection'
    assert root.children[3].content == 'UNT'
    assert root.children[4].tag == 'date'
    assert root.children[4].content == '1944'


def test_untldict2py_dict_includes_qualifier_only_element():
    # Not sure if there are ever elements with no content and no children
    # in practice, but the code handles that scenario.
    untl_dict = deepcopy(UNTL_DICTIONARY)
    untl_dict['date'] = [{'qualifier': 'creation'}]
    root = untldoc.untldict2py(untl_dict)
    assert isinstance(root, us.UNTLElement)
    assert root.children[4].tag == 'date'
    assert root.children[4].qualifier == 'creation'


def test_post2pydict():
    post_dict = {'creator-name': ['Eathing, Sai N.'],
                 'relation-content': [''],
                 'subject-qualifier': ['AAT', 'AAT'],
                 'publisher-name': ['UNT Art'],
                 'creator-role': ['art'],
                 'title-content': ['Untitled 2000.'],
                 'description-qualifier': ['physical', 'content'],
                 'relation-qualifier': [''],
                 'description-content': ['oil on canvas ; 12 x 6 in.',
                                         'Painting of cookies.'],
                 'publish': ['Publish'],
                 'creator-info': ['UNT'],
                 'collection-content': ['UNTCVA', 'UNTSW'],
                 'subject-content': ['paintings (visual works)',
                                     'works of art'],
                 'creator-type': ['per'],
                 'meta-qualifier': ['meta-id', 'system'],
                 'csrfmiddlewaretoken': ['blahblahblahblah'],
                 'meta-content': ['metatest1', 'DC'],
                 'title-qualifier': ['officialtitle']}
    ignore_list = ['publish', 'csrfmiddlewaretoken']
    element_dict = untldoc.post2pydict(post_dict, ignore_list)
    # publish and csrfmiddlewaretoken are not in the resulting dict.
    assert element_dict == {'creator': [{'qualifier': 'art',
                                         'content': {'name': 'Eathing, Sai N.',
                                                     'info': 'UNT',
                                                     'type': 'per'}}],
                            'subject': [{'qualifier': 'AAT',
                                         'content': 'paintings (visual works)'},
                                        {'qualifier': 'AAT',
                                         'content': 'works of art'}],
                            'publisher': [{'content': {'name': 'UNT Art'}}],
                            'title': [{'qualifier': 'officialtitle',
                                       'content': 'Untitled 2000.'}],
                            'description': [{'qualifier': 'physical',
                                             'content': 'oil on canvas ; 12 x 6 in.'},
                                            {'qualifier': 'content',
                                             'content': 'Painting of cookies.'}],
                            'collection': [{'content': 'UNTCVA'},
                                           {'content': 'UNTSW'}],
                            'meta': [{'qualifier': 'meta-id',
                                      'content': 'metatest1'},
                                     {'qualifier': 'system',
                                      'content': 'DC'}]}


def test_post2pydict_PyuntlException():
    post_dict = {'subject-qualifier': ['AAT', 'AAT'],
                 'subject-content': ['paintings (visual works)']}
    with pytest.raises(untldoc.PyuntlException) as err:
        untldoc.post2pydict(post_dict, [])
    assert 'Field values did not match up numerically for subject' == err.value.args[0]


def test_untlpy2dcpy():
    untl_dict = {'coverage': [{'content': '1943', 'qualifier': 'sDate'},
                              {'content': '1944', 'qualifier': 'eDate'},
                              {'content': 'United States - Texas', 'qualifier': 'placeName'}],
                 'publisher': [{'content': {'name': 'UNT Press', 'location': 'Denton, Texas'}}],
                 'creator': [{'content': {'type': 'org', 'name': 'UNT'}, 'qualifier': 'aut'}],
                 'title': [{'content': 'UNT Book', 'qualifier': 'officialtitle'}],
                 'collection': [{'content': 'UNT'}]}
    untl_elements = untldoc.untldict2py(untl_dict)
    root = untldoc.untlpy2dcpy(untl_elements)
    assert isinstance(root, dc.DCElement)
    assert len(root.children) == 5
    assert root.tag == 'dc'
    assert root.children[0].tag == 'coverage'
    assert root.children[0].content == 'United States - Texas'
    assert root.children[1].tag == 'publisher'
    assert root.children[1].content == 'UNT Press'
    assert root.children[2].tag == 'creator'
    assert root.children[2].content == 'UNT'
    assert root.children[3].tag == 'title'
    assert root.children[3].content == 'UNT Book'
    # Coverage sDate/eDate are combined and added at the end.
    assert root.children[4].tag == 'coverage'
    assert root.children[4].content == '1943-1944'


def test_untlpy2dcpy_resolve_values_verbose_vocabularies():
    verbose_vocab = {'languages': [{'url': 'http://example.com/languages/#spa',
                                    'name': 'spa',
                                    'label': 'Spanish'}]}
    untl_dict = {'language': [{'content': 'spa'}]}
    untl_elements = untldoc.untldict2py(untl_dict)
    root = untldoc.untlpy2dcpy(untl_elements,
                               resolve_values=True,
                               verbose_vocabularies=verbose_vocab)
    assert root.children[0].tag == 'language'
    assert root.children[0].content == 'Spanish'


@patch('pyuntl.untldoc.retrieve_vocab')
def test_untlpy2dcpy_resolve_values_retrieve_vocab(mock_vocab):
    mock_vocab.return_value = {'languages': [{'url': 'http://example.com/languages/#spa',
                                              'name': 'spa',
                                              'label': 'Spanish'}]}
    untl_dict = {'language': [{'content': 'spa'}]}
    untl_elements = untldoc.untldict2py(untl_dict)
    root = untldoc.untlpy2dcpy(untl_elements,
                               resolve_values=True)
    assert root.children[0].tag == 'language'
    assert root.children[0].content == 'Spanish'


def test_untlpy2dcpy_resolve_urls():
    verbose_vocab = {'languages': [{'url': 'http://example.com/languages/#spa',
                                    'name': 'spa',
                                    'label': 'Spanish'}]}
    untl_dict = {'language': [{'content': 'spa'}]}
    untl_elements = untldoc.untldict2py(untl_dict)
    root = untldoc.untlpy2dcpy(untl_elements,
                               resolve_urls=True,
                               verbose_vocabularies=verbose_vocab)
    assert root.children[0].tag == 'language'
    assert root.children[0].content == 'http://example.com/languages/#spa'


def test_untlpy2dcpy_add_permalink_and_ark():
    untl_dict = {'title': [{'content': 'UNT Book', 'qualifier': 'officialtitle'}]}
    untl_elements = untldoc.untldict2py(untl_dict)
    root = untldoc.untlpy2dcpy(untl_elements,
                               ark='ark:/67531/metatest1',
                               domain_name='example.com',
                               scheme='https')
    assert root.children[0].tag == 'title'
    assert root.children[1].tag == 'identifier'
    assert root.children[1].content == 'https://example.com/ark:/67531/metatest1/'
    assert root.children[2].tag == 'identifier'
    assert root.children[2].content == 'ark: ark:/67531/metatest1'


def test_untlpy2dcpy_only_sDate():
    untl_dict = {'coverage': [{'content': '1943', 'qualifier': 'sDate'}]}
    untl_elements = untldoc.untldict2py(untl_dict)
    root = untldoc.untlpy2dcpy(untl_elements)
    assert root.children[0].tag == 'coverage'
    assert root.children[0].content == '1943'


def test_untlpy2dcpy_only_eDate():
    untl_dict = {'coverage': [{'content': '1955', 'qualifier': 'eDate'}]}
    untl_elements = untldoc.untldict2py(untl_dict)
    root = untldoc.untlpy2dcpy(untl_elements)
    assert root.children[0].tag == 'coverage'
    assert root.children[0].content == '1955'


def test_untlpy2highwirepy():
    untl_elements = untldoc.untldict2py(UNTL_DICTIONARY)
    highwire_list = untldoc.untlpy2highwirepy(untl_elements)
    assert len(highwire_list) == 4
    for element in highwire_list:
        assert element.tag == 'meta'
    assert highwire_list[0].qualifier == 'aut'
    assert highwire_list[0].name == 'citation_author'
    assert highwire_list[0].content == 'Last, Furston, 1807-1865.'
    assert highwire_list[1].qualifier is None
    assert highwire_list[1].name == 'citation_publisher'
    assert highwire_list[1].content == 'Fake Publishing'
    assert highwire_list[2].qualifier == 'creation'
    assert highwire_list[2].name == 'citation_publication_date'
    assert highwire_list[2].content == '1944'
    assert highwire_list[3].qualifier == 'officialtitle'
    assert highwire_list[3].name == 'citation_title'
    assert highwire_list[3].content == 'Tres Actos'


def test_untlpy2highwirepy_not_official_title():
    untl_dict = {'title': [{'qualifier': 'alternatetitle',
                            'content': 'Tres Actos'}]}
    untl_elements = untldoc.untldict2py(untl_dict)
    highwire_list = untldoc.untlpy2highwirepy(untl_elements)
    assert len(highwire_list) == 1
    assert highwire_list[0].qualifier == 'alternatetitle'
    assert highwire_list[0].name == 'citation_title'
    assert highwire_list[0].content == 'Tres Actos'


def test_untlpydict2dcformatteddict():
    dc_dict = untldoc.untlpydict2dcformatteddict(UNTL_DICTIONARY,
                                                 resolve_values=True,
                                                 ark='ark:/67531/metatest1',
                                                 domain_name='example.com',
                                                 scheme='https')
    assert dc_dict == {'title': ['Tres Actos'],
                       'creator': ['Last, Furston, 1807-1865.'],
                       'publisher': ['Fake Publishing'],
                       'date': ['1944'],
                       'identifier': ['https://example.com/ark:/67531/metatest1/',
                                      'ark: ark:/67531/metatest1']}


def test_dcpy2formatteddcdict():
    root = dc.DC()
    name = us.Name(content='Case, Justin')
    creator = dc.DCCreator(children=[name])
    root.add_child(creator)
    dc_dict = untldoc.dcpy2formatteddcdict(root)
    assert dc_dict == {'creator': ['Case, Justin']}


def test_dcpy2dict():
    root = dc.DC()
    name = us.Name(content='Case, Justin')
    creator = dc.DCCreator(children=[name])
    root.add_child(creator)
    dc_dict = untldoc.dcpy2dict(root)
    assert dc_dict == {'creator': [{'content': 'Case, Justin'}]}


def test_formatted_dc_dict():
    unformatted_dict = {'creator': [{'content': 'Case, Justin'}]}
    dc_dict = untldoc.formatted_dc_dict(unformatted_dict)
    assert dc_dict == {'creator': ['Case, Justin']}


def test_generate_dc_xml():
    xml = untldoc.generate_dc_xml(DC_DICTIONARY)
    expected_xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                    '<oai_dc:dc xmlns:dc="http://purl.org/dc/elements/1.1/"'
                    ' xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"'
                    ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
                    ' xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/'
                    ' http://www.openarchives.org/OAI/2.0/oai_dc.xsd">\n'
                    '  <dc:title>Tres Actos</dc:title>\n'
                    '  <dc:creator>Enhorn, Blair</dc:creator>\n'
                    '  <dc:publisher>Fake Publishing</dc:publisher>\n'
                    '  <dc:date>1944</dc:date>\n'
                    '</oai_dc:dc>\n')
    xml_lines = xml.decode().split('\n')
    expected_xml_lines = expected_xml.split('\n')
    # All but the second XML line should be in a specific order, so sort the
    # text of the second line to check equality.
    xml_lines[1] = sorted(xml_lines[1].split())
    expected_xml_lines[1] = sorted(expected_xml_lines[1].split())
    assert xml_lines == expected_xml_lines


def test_generate_dc_json():
    dc_json = untldoc.generate_dc_json(DC_DICTIONARY)
    assert dc_json == ('{\n'
                       '    "creator": [\n'
                       '        "Enhorn, Blair"\n'
                       '    ],\n'
                       '    "date": [\n'
                       '        "1944"\n'
                       '    ],\n'
                       '    "publisher": [\n'
                       '        "Fake Publishing"\n'
                       '    ],\n'
                       '    "title": [\n'
                       '        "Tres Actos"\n'
                       '    ]\n'
                       '}')


def test_generate_dc_txt():
    dc_txt = untldoc.generate_dc_txt(DC_DICTIONARY)
    assert dc_txt == ('title: Tres Actos\n'
                      'creator: Enhorn, Blair\n'
                      'publisher: Fake Publishing\n'
                      'date: 1944')


def test_highwirepy2dict():
    untl_elements = untldoc.untldict2py(UNTL_DICTIONARY)
    highwire_list = untldoc.untlpy2highwirepy(untl_elements)
    highwire_dict = untldoc.highwirepy2dict(highwire_list)
    assert highwire_dict == {'citation_author': [{'content': 'Last, Furston, 1807-1865.'}],
                             'citation_publisher': [{'content': 'Fake Publishing'}],
                             'citation_publication_date': [{'content': '1944'}],
                             'citation_title': [{'content': 'Tres Actos'}]}


def test_generate_highwire_xml():
    untl_elements = untldoc.untldict2py(UNTL_DICTIONARY)
    highwire_list = untldoc.untlpy2highwirepy(untl_elements)
    xml = untldoc.generate_highwire_xml(highwire_list)
    expected_xml = (b'<?xml version="1.0" encoding="UTF-8"?>\n'
                    b'<metadata>\n'
                    b'  <meta content="Tres Actos" name="citation_title"/>\n'
                    b'  <meta content="Last, Furston, 1807-1865." name="citation_author"/>\n'
                    b'  <meta content="Fake Publishing" name="citation_publisher"/>\n'
                    b'  <meta content="1944" name="citation_publication_date"/>\n'
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


def test_generate_highwire_json():
    untl_elements = untldoc.untldict2py(UNTL_DICTIONARY)
    highwire_list = untldoc.untlpy2highwirepy(untl_elements)
    highwire_json = untldoc.generate_highwire_json(highwire_list)
    assert highwire_json == ('{\n'
                             '    "citation_author": [\n'
                             '        {\n'
                             '            "content": "Last, Furston, 1807-1865."\n'
                             '        }\n'
                             '    ],\n'
                             '    "citation_publication_date": [\n'
                             '        {\n'
                             '            "content": "1944"\n'
                             '        }\n'
                             '    ],\n'
                             '    "citation_publisher": [\n'
                             '        {\n'
                             '            "content": "Fake Publishing"\n'
                             '        }\n'
                             '    ],\n'
                             '    "citation_title": [\n'
                             '        {\n'
                             '            "content": "Tres Actos"\n'
                             '        }\n'
                             '    ]\n'
                             '}')


def test_generate_highwire_text():
    untl_elements = untldoc.untldict2py(UNTL_DICTIONARY)
    highwire_list = untldoc.untlpy2highwirepy(untl_elements)
    text = untldoc.generate_highwire_text(highwire_list)
    assert text == ('citation_title: Tres Actos\n'
                    'citation_author: Last, Furston, 1807-1865.\n'
                    'citation_publisher: Fake Publishing\n'
                    'citation_publication_date: 1944')


def test_dcdict2rdfpy():
    dc_dict = {'title': [{'content': 'The Alwaysending Story'}],
               'creator': [{'content': 'Ding, Bill'}],
               'publisher': [{'content': 'Mock Publishing'}],
               'date': [{'content': '2019'}],
               'identifier': [{'content': 'ark: ark:/67531/metatest2'},
                              {'content': 'http://example.com/ark:/67531/metatest1/'}]}
    rdf_py = untldoc.dcdict2rdfpy(dc_dict)
    assert isinstance(rdf_py, ConjunctiveGraph)
    # Check the length of the graph matches the number of 'content' keys.
    assert len(rdf_py) == 6


def test_generate_rdf_xml():
    dc_dict = {'title': [{'content': 'عنوان'}],
               'creator': [{'content': 'الاخير, أول'}],
               'publisher': [{'content': 'الناشر'}],
               'date': [{'content': '2019'}],
               'identifier': [{'content': 'ark: ark:/67531/metatest2'},
                              {'content': 'http://example.com/ark:/67531/metatest1/'}]}
    rdf_xml = untldoc.generate_rdf_xml(dc_dict)
    # sort lines because rdf_xml is not always generated in the same order.
    rdf_lines = sorted(rdf_xml.decode('utf-8').split())
    assert rdf_lines == sorted(('<?xml version="1.0" encoding="utf-8"?>\n'
                                '<rdf:RDF\n'
                                '  xmlns:dc="http://purl.org/dc/elements/1.1/"\n'
                                '  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n'
                                '>\n'
                                '  <rdf:Description rdf:about="info:ark/67531/metatest2">\n'
                                '    <dc:date>2019</dc:date>\n'
                                '    <dc:creator>الاخير, أول</dc:creator>\n'
                                '    <dc:identifier'
                                ' rdf:resource="http://example.com/ark:/67531/metatest1/"/>\n'
                                '    <dc:publisher>الناشر</dc:publisher>\n'
                                '    <dc:title>عنوان</dc:title>\n'
                                '    <dc:identifier>ark: ark:/67531/metatest2</dc:identifier>\n'
                                '  </rdf:Description>\n'
                                '</rdf:RDF>\n').split())


@patch('urllib.request.urlopen')
def test_retrieve_vocab(mock_urlopen):
    mock_urlopen.return_value.read.return_value = '{"some": "data"}'
    vocab = untldoc.retrieve_vocab()
    assert vocab == {'some': 'data'}


@patch('urllib.request.urlopen', side_effect=Exception)
def test_retrieve_vocab_getting_data_errors(mock_urlopen):
    vocab = untldoc.retrieve_vocab()
    assert vocab is None


def test_add_empty_fields():
    """Check empty fields are added if not supplied in the dictionary."""
    untl_dict = deepcopy(UNTL_DICTIONARY)
    untl_dict = untldoc.add_empty_fields(untl_dict)
    assert untl_dict == {'title': [{'qualifier': 'officialtitle', 'content': 'Tres Actos'}],
                         'creator': [{'qualifier': 'aut',
                                      'content': {'name': 'Last, Furston, 1807-1865.',
                                                  'type': 'per'}}],
                         'publisher': [{'content': {'name': 'Fake Publishing'}}],
                         'collection': [{'content': 'UNT'}],
                         'date': [{'content': '1944', 'qualifier': 'creation'}],
                         'contributor': [{'content': {'info': '', 'type': '', 'name': ''}}],
                         'language': [{'content': ''}],
                         'description': [{'content': '', 'qualifier': ''}],
                         'subject': [{'content': '', 'qualifier': ''}],
                         'primarySource': [{'content': ''}],
                         'coverage': [{'content': '', 'qualifier': ''}],
                         'source': [{'content': '', 'qualifier': ''}],
                         'citation': [{'content': '', 'qualifier': ''}],
                         'relation': [{'content': '', 'qualifier': ''}],
                         'institution': [{'content': ''}],
                         'rights': [{'content': '', 'qualifier': ''}],
                         'resourceType': [{'content': ''}],
                         'format': [{'content': ''}],
                         'identifier': [{'content': '', 'qualifier': ''}],
                         'degree': [{'content': '', 'qualifier': ''}],
                         'note': [{'content': '', 'qualifier': ''}],
                         'meta': [{'content': '', 'qualifier': ''}]}


@patch('pyuntl.untl_structure.Title', side_effect=Exception)
def test_add_empty_fields_raise_PyuntlException(mock_title):
    with pytest.raises(untldoc.PyuntlException) as err:
        untldoc.add_empty_fields({})
    assert 'Could not add empty element field.' == err.value.args[0]


@patch('pyuntl.untl_structure.getattr')
def test_add_empty_fields_allows_content_no_qualifier_has_children(mock_getattr):
    # In practice we don't have a case where the element has a content
    # value and children (though the code allows it), as the children
    # are represented in the dict as the content value and would
    # overwrite an initial content value.
    # Pretend Collection element contains a child to trigger the targeted code.

    def side_effect(*args, **kwargs):
        if args[0].tag == 'collection' and args[1] == 'contained_children':
            return ['fake child']
        else:
            return getattr(*args, **kwargs)

    mock_getattr.side_effect = side_effect
    untl_dict = untldoc.add_empty_fields({})
    assert untl_dict['collection'] == [{'content': {'fake child': ''}}]


@patch('pyuntl.untl_structure.getattr')
def test_add_empty_fields_allows_content_and_qualifier_has_children(mock_getattr):
    untl_dict = untldoc.add_empty_fields({})
    # In practice we don't have a case where the element has a content
    # value, qualifier, and children (though the code allows it), as the
    # children are represented in the dict as the content value and would
    # overwrite an initial content value.
    # Pretend Subject element contains a child to trigger the targeted code.

    def side_effect(*args, **kwargs):
        if args[0].tag == 'subject' and args[1] == 'contained_children':
            return ['fake child']
        else:
            return getattr(*args, **kwargs)

    mock_getattr.side_effect = side_effect
    untl_dict = untldoc.add_empty_fields({})
    assert untl_dict['subject'] == [{'content': {'fake child': ''}, 'qualifier': ''}]


def test_find_untl_errors():
    untl_dict = {'title': [{'content': 'Tres Actos'},
                           {'content': 'Three Acts',
                            'qualifier': 'alternatetitle'}],
                 'creator': [{'content': {'name': 'Barney, Dino', 'type': 'per'}}],
                 'date': [{'content': '1944',
                           'qualifier': 'creation'}]}
    error_dict = untldoc.find_untl_errors(untl_dict)
    assert error_dict == {'untl_dict': {'title': [{'content': 'Tres Actos'},
                                                  {'content': 'Three Acts',
                                                   'qualifier': 'alternatetitle'}],
                                        'creator': [{'content': {'name': 'Barney, Dino',
                                                     'type': 'per'}}],
                                        'date': [{'content': '1944',
                                                  'qualifier': 'creation'}]},
                          'error_dict': {'title': 'no_qualifier'}}


def test_find_untl_errors_fix_errors():
    untl_dict = {'title': [{'content': 'Tres Actos'},
                           {'content': 'Three Acts',
                            'qualifier': 'alternatetitle'}],
                 'creator': [{'content': {'name': 'Barney, Dino', 'type': 'per'}}],
                 'date': [{'content': '1944',
                           'qualifier': 'creation'}]}
    error_dict = untldoc.find_untl_errors(untl_dict, fix_errors=True)
    assert error_dict == {'untl_dict': {'title': [{'content': 'Tres Actos',
                                                   'qualifier': ''},
                                                  {'content': 'Three Acts',
                                                   'qualifier': 'alternatetitle'}],
                                        'creator': [{'content': {'name': 'Barney, Dino',
                                                     'type': 'per'}}],
                                        'date': [{'content': '1944',
                                                  'qualifier': 'creation'}]},
                          'error_dict': {'title': 'no_qualifier'}}


def test_find_untl_errors_fix_errors_no_errors():
    untl_dict = {'title': [{'content': 'Tres Actos',
                            'qualifier': 'officialtitle'},
                           {'content': 'Three Acts',
                            'qualifier': 'alternatetitle'}],
                 'creator': [{'content': {'name': 'Barney, Dino', 'type': 'per'}}],
                 'date': [{'content': '1944',
                           'qualifier': 'creation'}]}
    error_dict = untldoc.find_untl_errors(untl_dict, fix_errors=True)
    assert error_dict == {'untl_dict': {'title': [{'content': 'Tres Actos',
                                                   'qualifier': 'officialtitle'},
                                                  {'content': 'Three Acts',
                                                   'qualifier': 'alternatetitle'}],
                                        'creator': [{'content': {'name': 'Barney, Dino',
                                                     'type': 'per'}}],
                                        'date': [{'content': '1944',
                                                  'qualifier': 'creation'}]},
                          'error_dict': {}}


def test_untl_to_hash_dict():
    title = us.Title(qualifier='serialtitle', content='The Bronco')
    meta_modifier = us.Meta(qualifier='metadataModifier', content='Daniel')
    meta_modification = us.Meta(qualifier='metadataModificationDate',
                                content='2007-09-20, 13:46:15')
    meta_object = us.Meta(qualifier='objectType', content='simple')
    elements = us.Metadata()
    elements.add_child(title)
    elements.add_child(meta_modification)
    elements.add_child(meta_modifier)
    elements.add_child(meta_object)
    hash_dict = untldoc.untl_to_hash_dict(elements)
    assert hash_dict == {'title': '9eff715f7ee7da9d5c2efdf075d07225',
                         'meta': 'f66a40a765dbfa230bd1b250a465ff6d'}


def test_untl_dict_to_tuple():
    untl_dict = deepcopy(UNTL_DICTIONARY)
    untl_tuple = untldoc.untl_dict_to_tuple(untl_dict)
    assert untl_tuple == {'title': [[('qualifier', 'officialtitle'),
                                     ('content', 'Tres Actos')]],
                          'creator': [[('qualifier', 'aut'),
                                       ('content', [('name', 'Last, Furston, 1807-1865.'),
                                                    ('type', 'per')])]],
                          'publisher': [[('content', [('name', 'Fake Publishing')])]],
                          'collection': [[('content', 'UNT')]],
                          'date': [[('content', '1944'), ('qualifier', 'creation')]]}


def test_generate_hash():
    test_input = [[('qualifier', 'serialtitle'), ('content', 'The Bronco')]]
    hash_val = untldoc.generate_hash(test_input)
    assert hash_val == '9eff715f7ee7da9d5c2efdf075d07225'
