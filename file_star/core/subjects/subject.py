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

    def __call__(self, *args, **kwargs):
        return self

    @property
    def file_name(self) -> str:
        """Get the file name"""
        return self._file_name

    @file_name.setter
    def file_name(self, value: str) -> None:
        """Set the file name"""
        self._file_name = value

    @property
    def extension(self) -> str:
        """Get the extension"""
        return self._extension

    @extension.setter
    def extension(self, value: str) -> None:
        """Set the extension"""
        self._extension = value

    @property
    def file_base_name(self) -> str:
        """Get the file base name"""
        return self._file_base_name

    @file_base_name.setter
    def file_base_name(self, value: str) -> None:
        """Set the file base name"""
        self._file_base_name = value

    @property
    def file_path_abs(self) -> str:
        """Get the file path absolute"""
        return self._file_path_abs

    @file_path_abs.setter
    def file_path_abs(self, value: str) -> None:
        """Set the file path absolute"""
        self._file_path_abs = value

    @property
    def file_path_rel(self) -> str:
        """Get the file path relative"""
        return self._file_path_rel

    @file_path_rel.setter
    def file_path_rel(self, value: str) -> None:
        """Set the file path relative"""
        self._file_path_rel = value

    @property
    def folder_path_abs(self) -> str:
        """Get the folder path absolute"""
        return self._folder_path_abs

    @folder_path_abs.setter
    def folder_path_abs(self, value: str) -> None:
        """Set the folder path absolute"""
        self._folder_path_abs = value

    @property
    def folder_path_rel(self) -> str:
        """Get the folder path relative"""
        return self._folder_path_rel

    @folder_path_rel.setter
    def folder_path_rel(self, value: str) -> None:
        """Set the folder path relative"""
        self._folder_path_rel = value

    @property
    def new_file_name(self) -> str:
        """Get the new file name"""
        return self._new_file_name

    @new_file_name.setter
    def new_file_name(self, value: str) -> None:
        """Set the new file name"""
        self._new_file_name = value

    @property
    def new_extension(self) -> str:
        """Get the new extension"""
        return self._new_extension

    @new_extension.setter
    def new_extension(self, value: str) -> None:
        """Set the new extension"""
        self._new_extension = value

    @property
    def new_file_path_rel(self) -> str:
        """Get the new file path relative"""
        return self._new_file_path_rel

    @new_file_path_rel.setter
    def new_file_path_rel(self, value: str) -> None:
        """Set the new file path relative"""
        self._new_file_path_rel = value

    @property
    def new_folder_path_rel(self) -> str:
        """Get the new folder path relative"""
        return self._new_folder_path_rel

    @new_folder_path_rel.setter
    def new_folder_path_rel(self, value: str) -> None:
        """Set the new folder path relative"""
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

    def __str__(self) -> str:
        """Return the subject as a string"""
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
