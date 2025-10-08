import os
from multiprocessing import Pool, cpu_count

from loguru import logger

from file_star.core.subjects.subject import Subject
from file_star.core.subjects.subjects_iterator import SubjectsIterator


def create_subject(args) -> Subject:
    """Helper function for multiprocessing"""
    base_path, file_path_abs = args
    return Subject(base_path, file_path_abs)


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
        for root, _, files in os.walk(self.path):
            for file in files:
                file_paths_abs.append(os.path.join(root, file))

        file_paths_abs.sort()

        args_list = [(self.path, fp) for fp in file_paths_abs]

        with Pool(cpu_count()) as pool:
            subjects = pool.map(create_subject, args_list)
        
        return SubjectsIterator(subjects)
