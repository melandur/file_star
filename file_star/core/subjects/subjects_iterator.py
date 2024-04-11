from file_star.core.subjects.subject import Subject


class SubjectsIterator:
    def __init__(self, subjects: list[Subject]) -> None:
        self._subjects = subjects
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self) -> Subject:
        if self._index < len(self._subjects):
            subject = self._subjects[self._index]
            self._index += 1
            return subject
        raise StopIteration

    def __len__(self) -> int:
        return len(self._subjects)

    def get(self, attribute: str = None) -> list:
        """Get a list of attributes from a filter of subjects"""
        if attribute is None:
            return self._subjects
        return [getattr(subject, attribute) for subject in self._subjects if hasattr(subject, attribute)]

    def reset_index(self) -> None:
        """Reset the index to 0"""
        self._index = 0
