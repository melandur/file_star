import copy

from generic_file_cleaner.core.handler import Handler


class FiltersHandler(Handler):
    def __init__(self) -> None:
        super().__init__()

    def get_subjects_per_filters(self, state: str, filter_name: str = None, attribute: str = None) -> dict:
        """Get a list of attributes from a filter of subjects"""

        if state is None:
            raise AttributeError(f'No state provided')

        if hasattr(self, state):
            state_attr = getattr(self, state)

            if filter_name is None:
                filters = {}
                for filter_name in vars(state_attr):
                    filters[filter_name] = getattr(state_attr, filter_name).get(attribute)
                return copy.deepcopy(filters)

            elif hasattr(state_attr, filter_name):
                filter_iter = getattr(state_attr, filter_name)
                return copy.deepcopy({filter_name: filter_iter.get(attribute)})
            else:
                raise AttributeError(
                    f'Filter {filter_name} does not exist.'
                    f'Valid names are: original, search, file_modifications, folder_modifications'
                )
        else:
            raise AttributeError(
                f'State {state} does not exist.'
                f'Valid names are: original, search, file_modifications, folder_modifications'
            )

    def get_subjects_per_state(self, state: str, attribute: str = None) -> list:
        """Get a list of attributes from a filter of subjects"""

        if state is None:
            raise AttributeError(f'No state provided')

        if hasattr(self, state):
            state_attr = getattr(self, state)
            subjects = []
            for filter_name in vars(state_attr):
                subjects.extend(getattr(state_attr, filter_name).get(attribute))
            return copy.deepcopy(subjects)

        else:
            raise AttributeError(
                f'State {state} does not exist.'
                f'Valid names are: original, search, file_modifications, folder_modifications'
            )

    def set(self, state: str, filters_iter) -> None:
        """Add subjects_iterator to a filter group"""

        if filters_iter is None:
            raise AttributeError(f'No subjects_iterator provided.')

        if hasattr(self, state):
            setattr(self, state, filters_iter)
        else:
            raise AttributeError(
                f'State {state} does not exist.'
                f'Valid names are: original, search, file_modifications, folder_modifications'
            )
