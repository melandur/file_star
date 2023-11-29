import json
import os


class Subject:
    def __init__(self, search_path: str, file_path_abs: str) -> None:
        self._search_path = search_path

        self._file_name = None
        self._extension = None
        self._file_base_name = None
        self._file_path_abs = file_path_abs
        self._file_path_rel = None
        self._folder_path_abs = None
        self._folder_path_rel = None

        self._new_file_name = None
        self._new_extension = None
        self._new_file_path_rel = None
        self._new_folder_path_rel = None

        self.extract_info()

    @property
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self, value):
        self._file_name = value

    @property
    def extension(self):
        return self._extension

    @extension.setter
    def extension(self, value):
        self._extension = value

    @property
    def file_base_name(self):
        return self._file_base_name

    @file_base_name.setter
    def file_base_name(self, value):
        self._file_base_name = value

    @property
    def file_path_abs(self):
        return self._file_path_abs

    @file_path_abs.setter
    def file_path_abs(self, value):
        self._file_path_abs = value

    @property
    def file_path_rel(self):
        return self._file_path_rel

    @file_path_rel.setter
    def file_path_rel(self, value):
        self._file_path_rel = value

    @property
    def folder_path_abs(self):
        return self._folder_path_abs

    @folder_path_abs.setter
    def folder_path_abs(self, value):
        self._folder_path_abs = value

    @property
    def folder_path_rel(self):
        return self._folder_path_rel

    @folder_path_rel.setter
    def folder_path_rel(self, value):
        self._folder_path_rel = value

    @property
    def new_file_name(self):
        return self._new_file_name

    @new_file_name.setter
    def new_file_name(self, value):
        self._new_file_name = value

    @property
    def new_extension(self):
        return self._new_extension

    @new_extension.setter
    def new_extension(self, value):
        self._new_extension = value

    @property
    def new_file_path_rel(self):
        return self._new_file_path_rel

    @new_file_path_rel.setter
    def new_file_path_rel(self, value):
        self._new_file_path_rel = value

    @property
    def new_folder_path_rel(self):
        return self._new_folder_path_rel

    @new_folder_path_rel.setter
    def new_folder_path_rel(self, value):
        self._new_folder_path_rel = value

    def extract_info(self) -> None:
        """Extract file name, folder names and extension from a file path"""
        self._file_name = os.path.basename(self._file_path_abs)

        if '.' in self._file_name:
            self._file_base_name, self._extension = self._file_name.split('.', 1)
        else:
            self._file_base_name = self._file_name
            self._extension = ''

        self._file_path_rel = os.path.relpath(self._file_path_abs, self._search_path)
        self._folder_path_abs = os.path.dirname(self._file_path_abs)
        self._folder_path_rel = os.path.dirname(self._file_path_rel)

    def __str__(self):
        return json.dumps(
            {
                'file_name': self._file_name,
                'extension': self._extension,
                'file_base_name': self._file_base_name,
                'file_path_abs': self._file_path_abs,
                'file_path_rel': self._file_path_rel,
                'folder_path_abs': self._folder_path_abs,
                'folder_path_rel': self._folder_path_rel,
                'new_file_name': self._new_file_name,
                'new_extension': self._new_extension,
                'new_file_path_rel': self._new_file_path_rel,
                'new_folder_path_rel': self._new_folder_path_rel,
            },
            indent=4,
        )
