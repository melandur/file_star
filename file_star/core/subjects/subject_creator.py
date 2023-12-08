import os

from loguru import logger

from file_star.core.subjects.subject import Subject
from file_star.core.subjects.subjects_iterator import SubjectsIterator


class SubjectCreator:
    """Creates subjects from recursive file paths"""

    def __init__(self, path: str) -> None:
        super().__init__()
        self.path = path

    def __call__(self) -> SubjectsIterator or None:
        """Extract all file paths from a directory"""

        if not os.path.exists(self.path):
            logger.error(f'Path does not exist: {self.path}')
            return None

        file_paths_abs = []
        for root, dirs, files in os.walk(self.path):
            for file in files:
                file_paths_abs.append(os.path.join(root, file))

        file_paths_abs.sort()

        subjects = []
        for file_path_abs in file_paths_abs:
            subjects.append(Subject(self.path, file_path_abs))
        return SubjectsIterator(subjects)
