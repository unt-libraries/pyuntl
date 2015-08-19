DUBLIN_CORE_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:dc="http://purl.org/dc/elements/1.1/" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd">
  <dc:title qualifier="officialtitle">The Bronco, Yearbook of Hardin-Simmons University, 1944</dc:title>
  <dc:title qualifier="serialtitle">The Bronco</dc:title>
  <dc:title qualifier="addedtitle">The Bronco 1944</dc:title>
  <dc:creator qualifier="aut">
    <type>org</type>
    <name>Hardin-Simmons University</name>
  </dc:creator>
  <dc:creator qualifier="edt">
    <type>per</type>
    <name>Mahoney, Doris</name>
  </dc:creator>
  <dc:publisher>
    <name>Hardin-Simmons University</name>
    <location>Abilene, Texas</location>
  </dc:publisher>
  <dc:date qualifier="creation">1944</dc:date>
  <dc:date qualifier="digitized">2008</dc:date>
  <dc:language>eng</dc:language>
  <dc:description qualifier="content">Yearbook for Hardin-Simmons University in Abilene, Texas includes photos of and information about the school, student body, professors, and organizations.  Includes a student directory at the end of the book.</dc:description>
  <dc:description qualifier="physical">Not paginated : ill ; 31 cm.</dc:description>
  <dc:subject qualifier="LCSH">Simmons College (Abilene, Tex.) -- Students -- Yearbooks.</dc:subject>
  <dc:subject qualifier="LCSH">Simmons University (Abilene, Tex.) -- Students -- Yearbooks.</dc:subject>
  <dc:subject qualifier="LCSH">Hardin-Simmons University -- Students -- Yearbooks.</dc:subject>
  <dc:subject qualifier="LCSH">World War, 1939-1945 -- Texas.</dc:subject>
  <dc:subject qualifier="UNTL-BS">Education - Colleges and Universities</dc:subject>
  <dc:subject qualifier="UNTL-BS">Education - Yearbooks</dc:subject>
  <dc:subject qualifier="UNTL-BS">People</dc:subject>
  <dc:subject qualifier="UNTL-BS">Social Life and Customs - Clubs and Organizations</dc:subject>
  <dc:subject qualifier="UNTL-BS">Sports and Recreation</dc:subject>
  <dc:subject qualifier="UNTL-BS">Arts and Crafts</dc:subject>
  <dc:subject qualifier="KWD">louie</dc:subject>
  <dc:subject qualifier="KWD">sarge</dc:subject>
  <dc:coverage qualifier="placeName">United States - Texas</dc:coverage>
  <dc:coverage qualifier="timePeriod">mod-tim</dc:coverage>
  <dc:coverage qualifier="sDate">1943</dc:coverage>
  <dc:coverage qualifier="eDate">1944</dc:coverage>
  <dc:format>text</dc:format>
  <dc:identifier qualifier="OCLC">14281668</dc:identifier>
</oai_dc:dc>
'''

UNTL_DICT = {
    'publisher': [
        {'content': {'name': 'Hardin-Simmons University', 'location': 'Abilene, Texas'}}],
    'description': [
        {'content': 'Yearbook for Hardin-Simmons University in Abilene, Texas includes photos of and information about the school, student body, professors, and organizations.  Includes a student directory at the end of the book.', 'qualifier': 'content'},
        {'content': 'Not paginated : ill ; 31 cm.', 'qualifier': 'physical'}],
    'language': [
        {'content': 'eng'}],
    'creator': [
        {'content': {'type': 'org', 'name': 'Hardin-Simmons University'}, 'qualifier': 'aut'},
        {'content': {'type': 'per', 'name': 'Mahoney, Doris'}, 'qualifier': 'edt'}],
    'resourceType': [
        {'content': 'text_book'}],
    'format': [
        {'content': 'text'}],
    'title': [
        {'content': 'The Bronco, Yearbook of Hardin-Simmons University, 1944', 'qualifier': 'officialtitle'},
        {'content': 'The Bronco', 'qualifier': 'serialtitle'},
        {'content': 'The Bronco 1944', 'qualifier': 'addedtitle'}],
    'collection': [
        {'content': 'HSUY'}],
    'note': [
        {'content': '"Published Annually by Hardin-Simmons University, Abilene, Texas, 37th Edition."', 'qualifier': 'display'},
        {'content': 'comment: Descriptive metadata by htarver 2008-06-27.', 'qualifier': 'nonDisplay'},
        {'content': 'creationAppName: Adobe Photoshop\ncreationAppVersion: 7', 'qualifier': 'digitalPreservation'}],
    'meta': [
        {'content': 'ark:/67531/metapth38622', 'qualifier': 'ark'},
        {'content': 'meta-pth-38622', 'qualifier': 'meta-id'},
        {'content': 'meta-pcc-ae70cfc0-4572-11dd-8cf9-001676db018a', 'qualifier': 'meta-id'},
        {'content': '3203213158', 'qualifier': 'objectMasterSize'},
        {'content': '2008-06-29, 00:31:14', 'qualifier': 'metadataCreationDate'},
        {'content': 'mphillips', 'qualifier': 'metadataCreator'},
        {'content': 'PTH', 'qualifier': 'system'},
        {'content': '/data/ALC/HSUL/HSUY', 'qualifier': 'TKLPath'}],
    'coverage': [
        {'content': 'United States - Texas', 'qualifier': 'placeName'},
        {'content': 'mod-tim', 'qualifier': 'timePeriod'},
        {'content': '1943', 'qualifier': 'sDate'},
        {'content': '1944', 'qualifier': 'eDate'}],
    'date': [
        {'content': '1944', 'qualifier': 'creation'},
        {'content': '2008', 'qualifier': 'digitized'}],
    'identifier': [
        {'content': '14281668', 'qualifier': 'OCLC'}],
    'primarySource': [
        {'content': '1'}],
    'institution': [
        {'content': 'HSUL'}],
    'subject': [
        {'content': 'Simmons College (Abilene, Tex.) -- Students -- Yearbooks.', 'qualifier': 'LCSH'},
        {'content': 'Simmons University (Abilene, Tex.) -- Students -- Yearbooks.', 'qualifier': 'LCSH'},
        {'content': 'Hardin-Simmons University -- Students -- Yearbooks.', 'qualifier': 'LCSH'},
        {'content': 'World War, 1939-1945 -- Texas.', 'qualifier': 'LCSH'},
        {'content': 'Education - Colleges and Universities', 'qualifier': 'UNTL-BS'},
        {'content': 'Education - Yearbooks', 'qualifier': 'UNTL-BS'},
        {'content': 'People', 'qualifier': 'UNTL-BS'},
        {'content': 'Social Life and Customs - Clubs and Organizations', 'qualifier': 'UNTL-BS'},
        {'content': 'Sports and Recreation', 'qualifier': 'UNTL-BS'},
        {'content': 'Arts and Crafts', 'qualifier': 'UNTL-BS'},
        {'content': 'louie', 'qualifier': 'KWD'},
        {'content': 'sarge', 'qualifier': 'KWD'}, ]
    }

BAD_UNTL_DICT = {
    'publisher': [
        {'content': {'name': 'Hardin-Simmons University', 'location': 'Abilene, Texas'}}],
    'description': [
        {'content': 'Yearbook for Hardin-Simmons University in Abilene, Texas includes photos of and information about the school, student body, professors, and organizations.  Includes a student directory at the end of the book.', 'qualifier': 'content'},
        {'content': 'Not paginated : ill ; 31 cm.'}]
}

# Example of UNTL dict that needs normalization
UNNORMALIZED_DICT = {
    'subject': [
        {'content': 'Simmons College (Abilene, Tex.)--Students--Yearbooks', 'qualifier': 'LCSH'},
        {'content': 'Simmons University (Abilene, Tex.) -- Students -- Yearbooks', 'qualifier': 'LCSH'},
        {'content': 'Hardin-Simmons University -- Students --Yearbooks.', 'qualifier': 'LCSH'},
        {'content': 'World War, 1939-1945 -- Texas.', 'qualifier': 'LCSH'},
        {'content': 'World War, 1939-1945 -- Food supply -- United States.', 'qualifier': 'LCSH'},
        {'content': 'Business, Economics and Finance  - Journalism', 'qualifier': 'UNTL-BS'},
        {'content': 'Business, Economics and Finance  -  Journalism', 'qualifier': 'UNTL-BS'},
        ]
    }

# UNTL dict with proper normalization
NORMALIZED_DICT = {
    'subject': [
        {'content': 'Simmons College (Abilene, Tex.) -- Students -- Yearbooks.', 'qualifier': 'LCSH'},
        {'content': 'Simmons University (Abilene, Tex.) -- Students -- Yearbooks.', 'qualifier': 'LCSH'},
        {'content': 'Hardin-Simmons University -- Students -- Yearbooks.', 'qualifier': 'LCSH'},
        {'content': 'World War, 1939-1945 -- Texas.', 'qualifier': 'LCSH'},
        {'content': 'World War, 1939-1945 -- Food supply -- United States.', 'qualifier': 'LCSH'},
        {'content': 'Business, Economics and Finance - Journalism', 'qualifier': 'UNTL-BS'},
        {'content': 'Business, Economics and Finance - Journalism', 'qualifier': 'UNTL-BS'},
        ]
    }

# An unnormalized untl-bs string
UNNORMALIZED_UNTLBS = 'Business, Economics and Finance  - Journalism'

# An unnormalized lcsh string
UNNORMALIZED_LCSH = 'Guitar music--History and criticism'

# A normalized untl-bs string
NORMALIZED_UNTLBS = 'Business, Economics and Finance - Journalism'

# A normalized lcsh string
NORMALIZED_LCSH = 'Guitar music -- History and criticism.'

# Defined for testing post2pydict
IGNORE_POST_LIST = [
    'publish',
    'save',
    'csrfmiddlewaretoken',
    ]

# Defined for testing post2pydict
EXPECTED_POST_TO_PYDICT = {
    'collection': [{'content': u'UNTCVA'}, {'content': u'UNTSW'}],
    'coverage': [{'content': u'2000', 'qualifier': u'date'}],
    'creator': [{'content': {'info': u'University of North Texas',
                             'name': u'Falsetta, Vincent',
                             'type': u'per'},
                 'qualifier': u'art'}],
    'date': [{'content': u'2000', 'qualifier': u'creation'}],
    'degree': [{'content': u'Studio Arts', 'qualifier': u'department'}],
    'description': [{'content': u'1 art original : oil paint on canvas ;' +
                     ' 72 x 84 in.',
                     'qualifier': u'physical'},
                    {'content': u'This abstract painting is mostly black ' +
                     'with some white vertical scrapes.',
                     'qualifier': u'content'}],
    'format': [{'content': u'image'}],
    'identifier': [{'content': u'2010063245', 'qualifier': u'LOCAL-CONT-NO'}],
    'institution': [{'content': u'UNTCVA'}],
    'language': [{'content': u'nol'}],
    'meta': [{'content': u'metadc27160', 'qualifier': u'meta-id'},
             {'content': u'DC', 'qualifier': u'system'},
             {'content': u'ark:/67531/metadc27160', 'qualifier': u'ark'},
             {'content': u'2010-08-25, 21:10:41',
              'qualifier': u'metadataCreationDate'},
             {'content': u'acpmaker', 'qualifier': u'metadataCreator'},
             {'content': u'jliechty', 'qualifier': u'metadataModifier'},
             {'content': u'2013-10-31, 13:09:12',
              'qualifier': u'metadataModificationDate'},
             {'content': u'False', 'qualifier': u'hidden'}],
    'note': [{'content': u'comment: Descriptive metadata template created ' +
              'by htarver 2010-07-05.',
              'qualifier': u'nonDisplay'}],
    'primarySource': [{'content': u'1'}],
    'resourceType': [{'content': u'image_artwork'}],
    'rights': [{'content': u'public', 'qualifier': u'access'},
               {'content': u'Vincent Falsetta, Denton, TX',
                'qualifier': u'holder'},
               {'content': u'copyright', 'qualifier': u'license'},
               {'content': u'Copyright 2010, Vincent Falsetta, All Rights' +
                ' Reserved',
                'qualifier': u'statement'}],
    'subject': [{'content': u'paintings (visual works)', 'qualifier': u'AAT'},
                {'content': u'works of art', 'qualifier': u'AAT'},
                {'content': u'oil paint (paint)', 'qualifier': u'AAT'}],
    'title': [{'content': u'AL 00-3.', 'qualifier': u'officialtitle'}]
    }
