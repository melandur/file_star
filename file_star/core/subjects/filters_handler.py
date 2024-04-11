import copy
import os

from file_star.core.handler import Handler


class FiltersHandler(Handler):
    def get_subjects_per_filters(self, state: str, filter_name: str = None, attribute: str = None) -> dict:
        """Get a list of attributes from a filter of subjects"""

        if state is None:
            raise AttributeError('No state provided')

        if hasattr(self, state):
            state_attr = getattr(self, state)

            if filter_name is None:
                filters = {}
                for tmp_filter_name in vars(state_attr):
                    filters[tmp_filter_name] = getattr(state_attr, tmp_filter_name).get(attribute)
                return copy.deepcopy(filters)

            if hasattr(state_attr, filter_name):
                filter_iter = getattr(state_attr, filter_name)
                return copy.deepcopy({filter_name: filter_iter.get(attribute)})

            raise AttributeError(
                f'Filter {filter_name} does not exist.'
                f'Valid names are: original, search, file_modifications, folder_modifications'
            )

        raise AttributeError(
            f'State {state} does not exist.'
            f'Valid names are: original, search, file_modifications, folder_modifications'
        )

    def get_subjects_per_state(self, state: str, attribute: str = None) -> list:
        """Get a list of attributes from a filter of subjects"""

        if state is None:
            raise AttributeError('No state provided')

        if hasattr(self, state):
            state_attr = getattr(self, state)
            subjects = []
            for filter_name in vars(state_attr):
                subjects.extend(getattr(state_attr, filter_name).get(attribute))
            return copy.deepcopy(subjects)

        raise AttributeError(
            f'State {state} does not exist.'
            f'Valid names are: original, search, file_modifications, folder_modifications'
        )

    def set(self, state: str, filters_iter) -> None:
        """Add subjects_iterator to a filter group"""

        if filters_iter is None:
            raise AttributeError('No subjects_iterator provided.')

        if hasattr(self, state):
            setattr(self, state, filters_iter)
        else:
            raise AttributeError(
                f'State {state} does not exist.'
                f'Valid names are: original, search, file_modifications, folder_modifications'
            )

    def analyze_state(self, state: str) -> dict:
        """Analyze a search"""

        if state is None:
            raise AttributeError('No state provided')

        if not hasattr(self, state):
            raise AttributeError('Invalid state provided.')

        filters_iter = getattr(self, state)
        analysis = {}
        for filter_name, subjects_iter in filters_iter.get_per_filter(attribute=None).items():
            analysis[filter_name] = {}
            analysis[filter_name]['files'] = len(subjects_iter)
            top_level_folders = len({subject.folder_path_rel.split(os.sep)[0] for subject in subjects_iter})
            analysis[filter_name]['top_level_folders'] = top_level_folders

        return analysis
