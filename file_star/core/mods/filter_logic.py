# pylint: disable=W0611

import copy
import os
import shutil

from file_star.core.handler import Handler
from file_star.core.mods.file.file_mod_logic import (  # needed for file_modifications
    add_file_prefix_suffix,
    new_file_name,
    replace_file_name_parts,
    split_file_name_parts,
)
from file_star.core.mods.folder.folder_mod_logic import (  # needed for new_folder_modifications
    add_folder_prefix_suffix,
    find_folder_by_level,
    find_folder_by_name,
    create_folder_from_file_name,
    new_folder_name,
    replace_folder_name_parts,
    split_folder_name_parts,
)
from file_star.core.mods.search import (
    Extension,
    FileName,
    FolderNames,
    SearchFilter,
    check_for_inactive_search,
    check_search_collisions,
    create_search_statements,
)
from file_star.core.subjects.filters_iterator import FiltersIterator
from file_star.core.subjects.subjects_iterator import SubjectsIterator


class FilterLogic(Handler):
    """Filter logic"""

    _shared_state = {}  # Class attribute to store shared state

    def __init__(self) -> None:
        super().__init__()
        self.__dict__ = self._shared_state  # Assign the shared state to the instance's __dict__
        self.filter_names = []

    def apply_search(self, subject_handler):
        """Apply a search to a list of file paths"""

        if subject_handler.original is None:
            return None, None, None

        if len(getattr(subject_handler.original, 'original')) == 0:
            return None, None, None

        sf = SearchFilter()
        filter_statements = create_search_statements(self.search)  # self.search is from BORG

        filters_iter = FiltersIterator()
        if filter_statements:
            self.filter_names = list(filter_statements.keys())

            subjects = subject_handler.get_subjects_per_filters(
                state='original', filter_name='original', attribute=None
            )

            for filter_name in filter_statements:
                subjects_per_filter = []
                for subject in sf.filter(subjects['original'], eval(filter_statements[filter_name])):
                    subjects_per_filter.append(subject)

                filters_iter[filter_name] = SubjectsIterator(subjects_per_filter)

            inactive_search = check_for_inactive_search(filters_iter)
            collision = check_search_collisions(filters_iter)
            return filters_iter, collision, inactive_search

        return None, None, None

    def apply_file_modifications(self, subject_handler):
        """Apply file modifications to a list of file paths"""

        if subject_handler.search is None:
            return None

        if self.file_modifications is None:
            return None

        filters_iter = FiltersIterator()
        for filter_name, subjects in subject_handler.get_subjects_per_filters(state='search', attribute=None).items():
            subjects_per_filter = []
            for subject in subjects:
                tmp_subject = copy.deepcopy(subject)

                for mod_name in self.file_modifications[filter_name]:
                    if self.file_modifications[filter_name][mod_name]:
                        tmp_subject = eval(mod_name)(tmp_subject, self.file_modifications[filter_name][mod_name])

                subjects_per_filter.append(tmp_subject)
            filters_iter[filter_name] = SubjectsIterator(subjects_per_filter)

        return filters_iter

    def apply_folder_modifications(self, subject_handler):
        """Apply folder modifications to a list of file paths"""

        if subject_handler.file_modifications is None:
            return None

        if self.folder_modifications is None:
            return None

        filters_iter = FiltersIterator()
        for filter_name, subjects in subject_handler.get_subjects_per_filters(
                state='file_modifications', attribute=None
        ).items():
            subjects_per_filter = []
            for subject in subjects:
                tmp_folder_names = []
                for folder_struct in self.folder_modifications[filter_name]:
                    tmp_subject = copy.deepcopy(subject)
                    for mod_name in self.folder_modifications[filter_name][folder_struct]:
                        if self.folder_modifications[filter_name][folder_struct][mod_name]:
                            tmp_subject = eval(mod_name)(
                                tmp_subject, self.folder_modifications[filter_name][folder_struct][mod_name]
                            )

                    if tmp_subject.new_folder_path_rel:
                        tmp_folder_names.append(tmp_subject.new_folder_path_rel)

                if tmp_folder_names:  # if there are folder modifications else use the original folder path
                    new_folder_path_rel = os.path.join(*tmp_folder_names)
                else:
                    new_folder_path_rel = subject.folder_path_rel

                subject.new_folder_path_rel = new_folder_path_rel
                new_file = f'{subject.new_file_name}.{subject.new_extension}'
                subject.new_file_path_rel = os.path.join(new_folder_path_rel, new_file)

                subjects_per_filter.append(subject)

            filters_iter[filter_name] = SubjectsIterator(subjects_per_filter)

        return filters_iter

    @staticmethod
    def apply_new_structure(subject_handler, dst_path: str) -> None:
        """Apply new structure to a list of file paths"""

        if subject_handler.folder_modifications is None:
            raise AttributeError('No folder modifications provided.')

        if dst_path is None:
            raise AttributeError('No destination path provided.')

        subject_per_filters = subject_handler.get_subjects_per_filters(state='folder_modifications', attribute=None)
        for _, subjects in subject_per_filters.items():
            for subject in subjects:
                new_folder_path_abs = os.path.join(dst_path, subject.new_folder_path_rel)
                os.makedirs(new_folder_path_abs, exist_ok=True)
                tmp_new_file_name = f'{subject.new_file_name}.{subject.new_extension}'
                new_file_path_abs = os.path.join(new_folder_path_abs, tmp_new_file_name)
                shutil.copy(subject.file_path_abs, new_file_path_abs)
