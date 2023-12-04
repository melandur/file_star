import os
from nicegui import ui

file_paths = []

for root, dirs, files in os.walk('/home/melandur/Data/diff_perf_mike'):
    for file in files:
        rel = os.path.relpath(root, '/home/melandur/Data/diff_perf_mike')
        file_paths.append(os.path.join(rel, file))

# print(file_paths)

# file_paths = [
#     'WAS_084_1953-20130327-0 (4th copy)/104-MPRkmcor/WAS_084_1953_MPRkmcor_104_12.dcm',
#     'WAS_084_1953-20130327-0 (4th copy)/104-MPRkmcor/WAS_084_1953_MPRkmcor_104_67.dcm',
#
#     'AEH_001_1945-20121025-0 (3rd copy)/1-localizer/uria/AEH_001_1945_localizer_1_1.dcm',
#
#     'AFB__1951-20130215-0/604-MIPaxial/AFB__1951_MIPaxial_604_93.dcm',
#     'AFB__1951-20130215-0/604-MIPaxial/AFB__1951_MIPaxial_604_60.dcm',
#     'AFB__1951-20130215-0/604-MIPaxial/test/AFB__1951_MIPaxial_604_220.dcm',
#     'AFB__1951-20130215-0/604-MIPaxial/test/AFB__1951_MIPaxial_604_40.dcm',
# ]


class Test:

    def __init__(self, _file_paths):
        self._file_paths = _file_paths
        self.store = []
        self.tree = None
        self.convert_to_structure(_file_paths, None)
        self.get_tree()

    @ui.refreshable
    def get_tree(self):
        tree = ui.tree(
            self.tree,
            label_key='id',
            on_expand=lambda e: self.convert_to_structure(self._file_paths, e.value),

        )
        del tree._props['selected']

        for expand in self.store:
            if os.sep in expand:
                expand = expand.split(os.sep)
            else:
                expand = [expand]
            tree.expand(expand)

    @staticmethod
    def extract(_file_paths):
        tree = {}
        _file_paths.sort()
        for file_path_rel in _file_paths:
            parts = file_path_rel.split(os.sep)
            current_node = tree

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

        if tree:
            return tree['children']

    def remove_substrings(self, _list):
        _list.sort(key=len)
        for i in range(len(_list)):
            for j in range(i + 1, len(_list)):
                if _list[i] in _list[j]:
                    _list[j] = _list[j].replace(_list[i], '')
        return _list

    def convert_to_structure(self, _file_paths, path_to_resolve=None):
        # print('res', path_to_resolve)
        _file_paths = [file_path.lstrip(os.sep) for file_path in _file_paths]

        if path_to_resolve is None:
            _file_paths = list(set([f'{os.sep}'.join(file_path.split(os.sep)[0:2]) for file_path in _file_paths]))
            self.tree = self.extract(_file_paths)
            self.get_tree.refresh()

        else:
            path_to_resolve = path_to_resolve[-1]
            print(path_to_resolve)
            active = [file_path for file_path in _file_paths if path_to_resolve in file_path]

            tmp = []
            for file_path in active:
                folders = file_path.split(os.sep)
                try:
                    index = folders.index(path_to_resolve)
                    folders = folders[0:index + 1]
                    tmp.append(os.sep.join(folders))
                except ValueError:
                    pass
            path_to_resolve = tmp[0]

            if self.store:
                if [x for x in self.store if x in path_to_resolve]:
                    for x in self.store:
                        if x in path_to_resolve:
                            self.store.remove(x)
                            self.store.append(path_to_resolve)
                else:
                    self.store.append(path_to_resolve)
            else:
                self.store.append(path_to_resolve)

            print(self.store)
            if self.store:
                count = 1
                if os.sep in path_to_resolve:
                    count = len(path_to_resolve.split(os.sep))

                _file_paths = list(
                    set([f'{os.sep}'.join(file_path.split(os.sep)[0:count + 2]) for file_path in _file_paths]))
                x = self.extract(_file_paths)

                if x:
                    self.tree = x

                self.get_tree.refresh()


a = Test(file_paths)

ui.run()
