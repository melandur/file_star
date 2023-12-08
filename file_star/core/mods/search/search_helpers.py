from itertools import combinations


def check_search_collisions(filters_iter):
    """Check if a filter is already in the filter store"""

    filter_file_paths_rel = filters_iter.get_per_filter(attribute='file_path_rel')
    filter_names = list(filter_file_paths_rel.keys())
    filter_combinations = [combo for combo in combinations(filter_names, 2) if combo[0] != combo[1]]

    collisions = {}
    for combo in filter_combinations:
        if set(filter_file_paths_rel[combo[0]]) & set(filter_file_paths_rel[combo[1]]):
            colliding_paths = list(set(filter_file_paths_rel[combo[0]]) & set(filter_file_paths_rel[combo[1]]))
            collisions[f'{combo[0]}_&_{combo[1]}'] = colliding_paths

    for key in collisions:
        if len(collisions[key]) > 5:  # limit example collisions to 5
            collisions[key] = collisions[key][:5]

    return collisions


def check_for_inactive_search(filters_iter):
    """Check if a filter has no results"""

    inactive_search = []
    for filter_name, subjects_iter in filters_iter.get_per_filter(attribute=None).items():
        if len(subjects_iter) == 0:
            inactive_search.append(filter_name)
    return inactive_search


def analyze_search(filters_iter):
    """Analyze a search"""

    analysis = {}
    for filter_name, subjects_iter in filters_iter.get_per_filter(attribute=None).items():
        analysis[filter_name] = len(subjects_iter)
    return analysis
