from pyuntl import compare


def test_compare_elements():
    hash_dict1 = {'title': '67ede133ab43b9d1cdbba5f33f48664a',
                  'creator': '1513f10cb05d869823951dcc50ae2e45',
                  'publisher': '1e48e8e67c2da306cd9b5495ac513681',
                  'collection': '8ca05b391a1b1cf502366f6dea811115',
                  'date': '8221c0e5dcc2e441a532f36d9afb296e'}

    hash_dict2 = {'title': 'e543bd10a308522b9b73ed7fc18106c7',
                  'creator': '1513f10cb05d869823951dcc50ae2e45',
                  'publisher': '5eb7bb172012ebb7347f40d7b4f28482',
                  'collection': '8ca05b391a1b1cf502366f6dea811115',
                  'meta': '8ca05b391a1b1c3951dcc50ae2e45'}
    changes = compare.compare_elements(hash_dict1, hash_dict2)
    assert changes == {'title': 'changed', 'publisher': 'changed',
                       'meta': 'added', 'date': 'deleted'}
