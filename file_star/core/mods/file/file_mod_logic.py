import os
import re

from loguru import logger


def new_file_name(subject, states):
    """Create a new file name"""

    subject = _propagate(subject, states['name'])
    return subject


def split_file_name_parts(subject, states):
    """Strip the file name parts"""

    for _, values in states.items():
        if values['split'] is None or values['start'] is None or values['end'] is None:
            continue

        if values['start'] > values['end']:
            continue

        if values['start'] < 0 or values['end'] < 0:
            continue

        if values['split'] in subject.new_file_name:
            file_base_name = subject.new_file_name.split(values['split'])
            if values['end'] <= len(file_base_name):
                new_file_name = f'{values["split"]}'.join(file_base_name[values['start'] : values['end'] + 1])
                subject = _propagate(subject, new_file_name)

    return subject


def replace_file_name_parts(subject, states):
    """Replace the old file name with the new file name"""

    for _, values in states.items():
        if values['old'] is None or values['new'] is None:
            continue

        try:
            if re.search(values['old'], subject.new_file_name):
                new_file_name = re.sub(values['old'], values['new'], subject.new_file_name)
                subject = _propagate(subject, new_file_name)
        except re.error as e:
            logger.warning(f"Regex error occurred for file name replacement: {e}")

    return subject


def add_file_prefix_suffix(subject, fixes):
    """Add a prefix/suffix to the file name"""

    if fixes['prefix'] is not None:
        new_file_name = f'{fixes["prefix"]}{subject.new_file_name}'
        subject = _propagate(subject, new_file_name)

    if fixes['suffix'] is not None:
        new_file_name = f'{subject.new_file_name}{fixes["suffix"]}'
        subject = _propagate(subject, new_file_name)

    return subject


def _propagate(subject, new_file_name):
    """Apply the changes to different file tags"""

    subject.new_file_name = f'{new_file_name}'
    new_file_name = f'{new_file_name}.{subject.new_extension}'
    subject.new_file_path_rel = os.path.join(subject.folder_path_rel, new_file_name)
    return subject
