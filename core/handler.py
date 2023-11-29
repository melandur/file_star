from abc import ABC


class Handler(ABC):
    def __init__(self):
        self._original = None
        self._search = None
        self._file_modifications = None
        self._folder_modifications = None

    @property
    def original(self):
        return self._original

    @original.setter
    def original(self, value):
        self._original = value

    @property
    def search(self):
        return self._search

    @search.setter
    def search(self, value):
        self._search = value

    @property
    def file_modifications(self):
        return self._file_modifications

    @file_modifications.setter
    def file_modifications(self, value):
        self._file_modifications = value

    @property
    def folder_modifications(self):
        return self._folder_modifications

    @folder_modifications.setter
    def folder_modifications(self, value):
        self._folder_modifications = value
