import os

from file_star.core.handler import Handler
from file_star.core.subjects.filters_handler import FiltersHandler


class GuiHandler(Handler):
    """Gui handler"""

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
    """Gui helper"""

    def __init__(self, filters_handler: FiltersHandler = None, state: str = None, path_type: str = None) -> None:
        self.state = state
        self.filters_handler = filters_handler

        self._tree_format = {}
        self._tree_gui = None

        self._get_tree_format(path_type)

    @property
    def tree_format(self):
        """Get the tree format"""
        return self._tree_format

    @tree_format.setter
    def tree_format(self, value):
        """Set the tree format"""
        self._tree_format = value

    @property
    def tree_gui(self):
        """Get the tree gui"""
        return self._tree_gui

    @tree_gui.setter
    def tree_gui(self, value):
        """Set the tree gui"""
        self._tree_gui = value

    def _get_tree_format(self, path_type) -> dict | None:
        """Convert a list of file paths into a tree structure (optimized)"""

        if getattr(self.filters_handler, self.state) is None:
            return None

        subjects = self.filters_handler.get_subjects_per_state(self.state)

        # Extract file paths more efficiently
        file_paths = []
        for subject in subjects:
            path = getattr(subject, path_type, None) or subject.file_path_rel
            file_paths.append(path)

        if not file_paths:
            self._tree_format = []
            return None

        file_paths.sort()

        # Optimized tree building using nested dictionaries
        tree_dict = {}

        for file_path_rel in file_paths:
            parts = file_path_rel.split(os.sep)
            current = tree_dict

            for part in parts:
                if part not in current:
                    current[part] = {}
                current = current[part]

        # Convert nested dict to tree format
        def dict_to_tree(d, path_so_far=None):
            """Convert nested dictionary to tree format"""
            result = []
            for key, value in sorted(d.items()):
                node = {'id': key}
                if value:  # Has children
                    node['children'] = dict_to_tree(value, f"{path_so_far}/{key}" if path_so_far else key)
                result.append(node)
            return result

        tree_format = dict_to_tree(tree_dict)
        self._tree_format = self.count_children(tree_format)

    @staticmethod
    def count_children(data):
        """Count the number of children and grandchildren in a tree structure (optimized)"""

        def count_descendants(item):
            """Count the number of children and grandchildren in a tree structure"""
            if 'children' in item and item['children']:
                children_count = len(item['children'])
                if children_count > 0:
                    item['id'] = f"{item['id']} [ {children_count} ]"
                    for child in item['children']:
                        count_descendants(child)

        for item in data:
            if 'children' in item and item['children']:
                children_count = len(item['children'])
                if children_count > 0:
                    item['id'] = f"{item['id']} [ {children_count} ]"
                count_descendants(item)

        return data
