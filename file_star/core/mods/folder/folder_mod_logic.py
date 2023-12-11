import os
import re

from loguru import logger

from file_star.core.mods.search.search_logic import Filter, Specification
from file_star.core.mods.search.search_tokens import (
    create_filter_logic,
    tokenize_filter_string,
)


class FolderNames(Specification):
    """Search for folder name specifications"""

    def __init__(self, *args) -> None:
        self.folder_name = args

    def is_satisfied(self, folder) -> bool:
        if any(x for x in self.folder_name if x in folder):
            return True


class SearchFilter(Filter):
    """Search filter loop"""

    def filter(self, folders: list, spec: Specification) -> str:
        for folder in folders:
            if spec.is_satisfied(folder):
                yield folder


def find_folder_by_level(subject, states):
    """Find a folder by its level"""

    folders = subject.folder_path_rel.split(os.sep)
    if states['level'] < len(folders):
        subject.new_folder_path_rel = folders[states['level']]

    return subject


def find_folder_by_name(subject, states):
    """Find a folder by its name"""

    search_tokens = tokenize_filter_string(states['name'])
    if search_tokens is None:
        return subject

    search_filter = create_filter_logic(search_tokens, 'FolderNames')
    if search_filter is None:
        return subject

    sf = SearchFilter()
    folders = subject.folder_path_rel.split(os.sep)
    for folder in sf.filter(folders, eval(search_filter)):
        subject.new_folder_path_rel = folder
        return subject

    return subject


def new_folder_name(subject, states):
    """Create a new folder name"""

    subject.new_folder_path_rel = states['name']
    return subject


def split_folder_name_parts(subject, states):
    """Strip the file name parts"""

    for _, values in states.items():
        if values['split'] is None or values['start'] is None or values['end'] is None:
            continue

        if values['start'] > values['end']:
            continue

        if values['start'] < 0 or values['end'] < 0:
            continue

        if values['split'] in subject.new_folder_path_rel:
            folder_names = subject.new_folder_path_rel.split(values['split'])

            if values['end'] <= len(folder_names):
                subject.new_folder_path_rel = f'{values["split"]}'.join(
                    folder_names[values['start'] : values['end'] + 1]
                )

    return subject


def replace_folder_name_parts(subject, states):
    """Replace the old file name with the new file name"""

    for _, values in states.items():
        if values['old'] is None or values['new'] is None:
            continue

        try:
            if re.search(values['old'], subject.new_folder_path_rel):
                subject.new_folder_path_rel = re.sub(values['old'], values['new'], subject.folder_path_rel)

        except re.error as e:
            logger.warning(f"Regex error occurred for folder name replacement: {e}")

    return subject


def add_folder_prefix_suffix(subject, fixes):
    """Add a prefix/suffix to the file name"""

    if fixes['prefix'] is not None:
        subject.new_folder_path_rel = f'{fixes["prefix"]}{subject.new_folder_path_rel}'

    if fixes['suffix'] is not None:
        subject.new_folder_path_rel = f'{subject.new_folder_path_rel}{fixes["suffix"]}'

    return subject
