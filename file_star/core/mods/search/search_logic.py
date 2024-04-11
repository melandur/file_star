import os
import re
from abc import ABC, abstractmethod

from loguru import logger


class Specification(ABC):
    """Abstract class for specifications"""

    @abstractmethod
    def is_satisfied(self, item: list) -> bool:
        """Abstract method for checking if a specification is satisfied"""

    def __and__(self, other):
        """Overload the & operator to check if all specifications are satisfied"""
        return AndSpecification(self, other)

    def __or__(self, other):
        """Overload the | operator to check if any specification is satisfied"""
        return OrSpecification(self, other)

    def __invert__(self):
        """Overload the ~ operator to check if any specification is satisfied"""
        return NotSpecification(self)


class AndSpecification(Specification):
    """Class for and specifications"""

    def __init__(self, *args) -> None:
        self.args = args

    def is_satisfied(self, item: dict) -> bool:
        return all(spec.is_satisfied(item) for spec in self.args)


class OrSpecification(Specification):
    """Class for or specifications"""

    def __init__(self, *args) -> None:
        self.args = args

    def is_satisfied(self, item: dict) -> bool:
        return any(spec.is_satisfied(item) for spec in self.args)


class NotSpecification(Specification):
    """Class for not specifications"""

    def __init__(self, spec) -> None:
        self.spec = spec

    def is_satisfied(self, item: dict) -> bool:
        return not self.spec.is_satisfied(item)


class Filter(ABC):
    """Abstract class for filters"""

    @abstractmethod
    def filter(self, item: dict, spec: Specification) -> object:
        """Abstract method for filtering"""


class FileName(Specification):
    """Search for file name specifications with regex"""

    def __init__(self, *args) -> None:
        self.file_names = args

    def is_satisfied(self, subject) -> bool:
        """Check if a file name is satisfied by a specification"""
        for file_name in self.file_names:
            try:
                if (
                    bool(re.search(file_name, subject.file_base_name))
                    and re.search(file_name, subject.file_base_name).group() != ''
                ):
                    return True
            except re.error as e:
                logger.warning(f"Regex error occurred for file names: {e}")
        return False


class FolderNames(Specification):
    """Search for folder name specifications with regex"""

    def __init__(self, *args) -> None:
        self.folder_name = args

    def is_satisfied(self, subject) -> bool:
        """Check if a folder name is satisfied by a specification"""
        folders = subject.folder_path_rel.split(os.sep)
        for folder_name in self.folder_name:
            for folder in folders:
                try:
                    if bool(re.search(folder_name, folder)) and re.search(folder_name, folder).group() != '':
                        return True
                except re.error as e:
                    logger.warning(f"Regex error occurred for folder names: {e}")
        return False


class Extension(Specification):
    """Search for extension specifications with regex"""

    def __init__(self, *args) -> None:
        self.extension = args

    def is_satisfied(self, subject) -> bool:
        """Check if an extension is satisfied by a specification"""
        for extension in self.extension:
            try:
                if (
                    bool(re.search(extension, subject.extension))
                    and re.search(extension, subject.extension).group() != ''
                ):
                    return True
            except re.error as e:
                logger.warning(f"Regex error occurred for extension: {e}")
        return False


class SearchFilter(Filter):
    """Search filter loop"""

    def filter(self, subject_iter: list, spec: Specification) -> dict:
        """Filter a list of subjects by a specification"""
        for subject in subject_iter:
            if spec.is_satisfied(subject):
                yield subject
