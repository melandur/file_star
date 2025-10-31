import os
import re
from abc import ABC, abstractmethod
from functools import lru_cache

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


@lru_cache(maxsize=128)
def _compile_regex(pattern: str):
    """Cache compiled regex patterns"""
    try:
        return re.compile(pattern)
    except re.error:
        return None


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
        # Pre-compile regex patterns for better performance
        self._compiled_patterns = []
        for pattern in self.file_names:
            compiled = _compile_regex(pattern)
            if compiled is not None:
                self._compiled_patterns.append(compiled)
            else:
                logger.warning(f"Invalid regex pattern for file names: {pattern}")

    def is_satisfied(self, subject) -> bool:
        """Check if a file name is satisfied by a specification"""
        for pattern in self._compiled_patterns:
            try:
                match = pattern.search(subject.file_base_name)
                if match and match.group() != '':
                    return True
            except Exception as e:
                logger.warning(f"Error matching file name pattern: {e}")
        return False


class FolderNames(Specification):
    """Search for folder name specifications with regex"""

    def __init__(self, *args) -> None:
        self.folder_name = args
        # Pre-compile regex patterns for better performance
        self._compiled_patterns = []
        for pattern in self.folder_name:
            compiled = _compile_regex(pattern)
            if compiled is not None:
                self._compiled_patterns.append(compiled)
            else:
                logger.warning(f"Invalid regex pattern for folder names: {pattern}")

    def is_satisfied(self, subject) -> bool:
        """Check if a folder name is satisfied by a specification"""
        folders = subject.folder_path_rel.split(os.sep)
        for pattern in self._compiled_patterns:
            for folder in folders:
                try:
                    match = pattern.search(folder)
                    if match and match.group() != '':
                        return True
                except Exception as e:
                    logger.warning(f"Error matching folder name pattern: {e}")
        return False


class Extension(Specification):
    """Search for extension specifications with regex"""

    def __init__(self, *args) -> None:
        self.extension = args
        # Pre-compile regex patterns for better performance
        self._compiled_patterns = []
        for pattern in self.extension:
            compiled = _compile_regex(pattern)
            if compiled is not None:
                self._compiled_patterns.append(compiled)
            else:
                logger.warning(f"Invalid regex pattern for extensions: {pattern}")

    def is_satisfied(self, subject) -> bool:
        """Check if an extension is satisfied by a specification"""
        for pattern in self._compiled_patterns:
            try:
                match = pattern.search(subject.extension)
                if match and match.group() != '':
                    return True
            except Exception as e:
                logger.warning(f"Error matching extension pattern: {e}")
        return False


class SearchFilter(Filter):
    """Search filter loop"""

    def filter(self, subject_iter: list, spec: Specification) -> dict:
        """Filter a list of subjects by a specification"""
        for subject in subject_iter:
            if spec.is_satisfied(subject):
                yield subject
