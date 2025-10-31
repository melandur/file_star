import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool, cpu_count
from typing import Callable, Optional

from loguru import logger

from file_star.core.subjects.subject import Subject
from file_star.core.subjects.subjects_iterator import SubjectsIterator


def create_subject(args) -> Subject:
    """Helper function for multiprocessing"""
    base_path, file_path_abs = args
    return Subject(base_path, file_path_abs)


def _create_subjects_batch(args_list: list) -> list:
    """Create subjects using multiprocessing pool (runs in executor)"""
    pool_size = min(cpu_count(), len(args_list))
    with Pool(pool_size) as pool:
        return pool.map(create_subject, args_list)


class SubjectCreator:
    """Creates subjects from recursive file paths"""

    def __init__(self, path: str, progress_callback: Optional[Callable[[int, int], None]] = None) -> None:
        super().__init__()
        self.path = path
        self.progress_callback = progress_callback

    def __call__(self) -> SubjectsIterator or None:
        """Extract all file paths from a directory (synchronous)"""

        if not os.path.exists(self.path):
            logger.error(f'Path does not exist: {self.path}')
            return None

        file_paths_abs = []
        for root, _, files in os.walk(self.path):
            for file in files:
                file_paths_abs.append(os.path.join(root, file))

        if len(file_paths_abs) == 0:
            return None

        file_paths_abs.sort()

        args_list = [(self.path, fp) for fp in file_paths_abs]

        # Optimize pool size - use min of cpu_count and file count
        pool_size = min(cpu_count(), len(args_list))

        with Pool(pool_size) as pool:
            subjects = pool.map(create_subject, args_list)

        return SubjectsIterator(subjects)

    async def __call_async__(self) -> SubjectsIterator or None:
        """Extract all file paths from a directory (asynchronous)"""

        if not os.path.exists(self.path):
            logger.error(f'Path does not exist: {self.path}')
            return None

        # Run file discovery in executor to avoid blocking
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        with ThreadPoolExecutor() as executor:
            file_paths_abs = await loop.run_in_executor(executor, self._discover_files)

        if len(file_paths_abs) == 0:
            return None

        file_paths_abs.sort()

        args_list = [(self.path, fp) for fp in file_paths_abs]

        # Update progress callback
        if self.progress_callback:
            try:
                self.progress_callback(0, len(args_list))
            except Exception as e:
                logger.warning(f"Error in progress callback: {e}")

        # Run subject creation in executor (multiprocessing Pool wrapped in thread executor)
        with ThreadPoolExecutor() as executor:
            subjects = await loop.run_in_executor(executor, _create_subjects_batch, args_list)
            if self.progress_callback:
                try:
                    self.progress_callback(len(subjects), len(args_list))
                except Exception as e:
                    logger.warning(f"Error in progress callback: {e}")

        return SubjectsIterator(subjects)

    def _discover_files(self) -> list:
        """Discover all files in directory (runs in executor)"""
        file_paths_abs = []
        for root, _, files in os.walk(self.path):
            for file in files:
                file_paths_abs.append(os.path.join(root, file))
        return file_paths_abs
