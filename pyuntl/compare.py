def compare_elements(hash_dict1, hash_dict2):
    """Check if any elements have been added, removed or modified."""
    changed = {}
    for key in hash_dict1:
        elem = hash_dict2.get(key, '')
        if elem == '':
            changed[key] = 'deleted'
        elif elem != hash_dict1[key]:
            changed[key] = 'changed'

    for key in hash_dict2:
        elem = hash_dict1.get(key, '')
        if elem == '':
            changed[key] = 'added'

    return changed
