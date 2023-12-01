import os

from nicegui import ui

from generic_file_cleaner.core.handler import Handler
from generic_file_cleaner.core.subjects.filters_handler import FiltersHandler


class GuiHandler(Handler):
    def __init__(self) -> None:
        super().__init__()

    def subject_handler_to_gui_handler(
        self,
        subjects_handler: FiltersHandler = None,
        state: str = None,
        path_type: str = None,
    ) -> None:
        """Convert subject_handler to gui_handler"""

        if hasattr(self, state):
            setattr(self, state, GuiHelper(subjects_handler, state, path_type))


class GuiHelper:
    def __init__(self, filters_handler: FiltersHandler = None, state: str = None, path_type: str = None) -> None:
        self.state = state
        self.filters_handler = filters_handler

        self._tree_format = {}
        self._tree_gui = ui.tree(nodes=[{'id': ''}], label_key='id')

        self._get_tree_format(path_type, limit=10000)

    @property
    def tree_format(self):
        return self._tree_format

    @tree_format.setter
    def tree_format(self, value):
        self._tree_format = value

    @property
    def tree_gui(self):
        return self._tree_gui

    @tree_gui.setter
    def tree_gui(self, value):
        self._tree_gui = value

    def _get_tree_format(self, path_type, limit=10000) -> dict or None:
        """Convert a list of file paths into a tree structure"""

        if getattr(self.filters_handler, self.state) is None:
            return None

        tree_format = {}

        subjects = self.filters_handler.get_subjects_per_state(self.state)

        file_paths = []
        for subject in subjects:
            if getattr(subject, path_type):
                file_paths.append(getattr(subject, path_type))
            else:
                file_paths.append(subject.file_path_rel)

        file_paths.sort()
        file_paths = file_paths[:limit]

        for file_path_rel in file_paths:
            parts = file_path_rel.split(os.sep)
            current_node = tree_format

            for part in parts:
                if 'children' not in current_node:
                    current_node['children'] = []

                child_id = {'id': part}
                existing_child = next((child for child in current_node['children'] if child['id'] == part), None)

                if existing_child:
                    current_node = existing_child
                else:
                    current_node['children'].append(child_id)
                    current_node = child_id

        self._tree_format = self.count_children(tree_format.get('children', []))

    @staticmethod
    def count_children(data):
        """Count the number of children and grandchildren in a tree structure"""

        def count_descendants(item):
            if 'children' in item and len(item['children']) > 0:
                for child in item['children']:
                    grandchildren_count = len(child.get('children', []))
                    if grandchildren_count > 0:
                        child['id'] = f"{child['id']} [ {grandchildren_count} ]"
                        count_descendants(child)

        for item in data:
            children_count = len(item.get('children', []))
            if children_count > 0:
                item['id'] = f"{item['id']} [ {len(item.get('children', []))} ]"
            count_descendants(item)

        return data
