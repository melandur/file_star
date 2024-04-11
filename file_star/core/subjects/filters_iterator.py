class FiltersIterator:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __setitem__(self, filter_name, subject_iter):
        self.__dict__[filter_name] = subject_iter

    def __getitem__(self, filter_name):
        return self.__dict__.get(filter_name)

    def __str__(self):
        return str(self.__dict__)

    def get_keys(self):
        """Get a list of keys from a filter of subjects"""
        return list(self.__dict__.keys())

    def get_per_filter(self, attribute: str = None) -> dict:
        """Get a list of attributes from a filter of subjects"""
        filters = {}
        for _filter_name in self.get_keys():
            filters[_filter_name] = getattr(self, _filter_name).get(attribute)
        return filters

    def get(self, filter_name: str = None, attribute: str = None) -> list:
        """Get a list of attributes from a filter of subjects"""
        if filter_name is None:
            raise AttributeError('No filter name provided')

        if hasattr(self, filter_name):
            subject_iter = getattr(self, filter_name)
            return subject_iter.get(attribute)

        raise AttributeError(
            f'Filter {filter_name} does not exist.'
            f'Valid names are: original, search, file_modifications, folder_modifications'
        )
