def compare_elements(prev_hash_dict, current_hash_dict):
    """Compare elements that have changed between prev_hash_dict and current_hash_dict.

    Check if any elements have been added, removed or modified.
    """

    changed = {}
    for key in prev_hash_dict:
        elem = current_hash_dict.get(key, '')
        if elem == '':
            changed[key] = 'deleted'
        elif elem != prev_hash_dict[key]:
            changed[key] = 'changed'

    for key in current_hash_dict:
        elem = prev_hash_dict.get(key, '')
        if elem == '':
            changed[key] = 'added'

    return changed
