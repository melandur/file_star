from abc import ABC


class Handler(ABC):
    def __init__(self):
        self._original = None
        self._search = None
        self._file_modifications = None
        self._folder_modifications = None

    @property
    def original(self):
        """Get the original"""
        return self._original

    @original.setter
    def original(self, value):
        """Set the original"""
        self._original = value

    @property
    def search(self):
        """Get the search"""
        return self._search

    @search.setter
    def search(self, value):
        """Set the search"""
        self._search = value

    @property
    def file_modifications(self):
        """Get the file modifications"""
        return self._file_modifications

    @file_modifications.setter
    def file_modifications(self, value):
        """Set the file modifications"""
        self._file_modifications = value

    @property
    def folder_modifications(self):
        """Get the folder modifications"""
        return self._folder_modifications

    @folder_modifications.setter
    def folder_modifications(self, value):
        """Set the folder modifications"""
        self._folder_modifications = value
