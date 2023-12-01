from abc import ABC, abstractmethod


class Specification(ABC):
    """Abstract class for specifications"""

    @abstractmethod
    def is_satisfied(self, item: list) -> bool:
        pass

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
        pass


class FileName(Specification):
    """Search for file name specifications"""

    def __init__(self, *args) -> None:
        self.file_names = args

    def is_satisfied(self, subject) -> bool:
        for file_name in self.file_names:
            if file_name in subject.file_name:
                return True


class FolderNames(Specification):
    """Search for folder name specifications"""

    def __init__(self, *args) -> None:
        self.folder_name = args

    def is_satisfied(self, subject) -> bool:
        if any(x in y for x in self.folder_name for y in subject.folder_path_rel):
            return True


class Extension(Specification):
    """Search for extension specifications"""

    def __init__(self, *args) -> None:
        self.extension = args

    def is_satisfied(self, subject) -> bool:
        for extension in self.extension:
            if extension in subject.extension:
                return True


class SearchFilter(Filter):
    """Search filter loop"""

    def filter(self, subject_iter: list, spec: Specification) -> dict:
        for subject in subject_iter:
            if spec.is_satisfied(subject):
                yield subject
