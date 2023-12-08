from nicegui import ui

from file_star.core.mods.filter_logic import FilterLogic
from file_star.core.subjects.filters_handler import FiltersHandler
from file_star.core.subjects.filters_iterator import FiltersIterator
from file_star.core.subjects.subject_creator import SubjectCreator
from file_star.gui.gui_handler import GuiHandler
from file_star.gui.widgets import (
    FileModWidget,
    FolderModWidget,
    LocalFolderPicker,
    SearchWidget,
)


class FileStar:
    def __init__(self):
        self.src_path = None
        self.dst_path = None

        self.expand = {'search': True, 'file_modifications': True, 'folder_modifications': True}
        self.show_tree = {'original': True, 'search': True, 'file_modifications': True, 'folder_modifications': True}

        self.gui_handler = GuiHandler()
        self.filter_logic = FilterLogic()
        self.filters_handler = FiltersHandler()

        self.search_widget = SearchWidget()
        self.file_mod_widget = FileModWidget()
        self.folder_mod_widget = FolderModWidget()

    def __call__(self):
        self.header()
        self.left_drawer()
        self.tree_view()

    def header(self):
        with ui.header():
            ui.label('File*').style('font-size: 30px; font-weight: bold;')

    def left_drawer(self):
        with ui.left_drawer().classes('bg-blue-100 w-full h-full').props('width=400'):
            ui.button(text='Set Source', icon='input', on_click=self.pick_source).classes('w-full')
            self.left_drawer_update()

    @ui.refreshable
    def left_drawer_update(self):
        if self.gui_handler.original:
            with ui.expansion(
                text='Search',
                icon='search',
                value=self.expand['search'],
                on_value_change=lambda e: self.expand.update({'search': e.value}),
            ).classes('w-full').props('header-class="bg-primary text-white font-bold text-lg"'):
                self.search_widget.get_widget(self.process_search)

        if self.gui_handler.search:
            with ui.expansion(
                text='File Modifications',
                icon='description',
                value=self.expand['file_modifications'],
                on_value_change=lambda e: self.expand.update({'file_modifications': e.value}),
            ).classes('w-full').props('header-class="bg-primary text-white font-bold text-lg"'):
                self.file_mod_widget.get_widget()
                ui.button(text='Apply', on_click=self.process_file_mods)

        if self.gui_handler.file_modifications:
            with ui.expansion(
                text='Folder Modifications',
                value=self.expand['folder_modifications'],
                icon='folder',
                on_value_change=lambda e: self.expand.update({'folder_modifications': e.value}),
            ).classes('w-full').props('header-class="bg-primary text-white font-bold text-lg"'):
                self.folder_mod_widget.get_widget()
                ui.button(text='Apply', on_click=self.process_folder_mods)

        if self.gui_handler.folder_modifications:
            with ui.expansion(
                text='Final',
                icon='file_download',
                value=True,
                on_value_change=None,
            ).classes(
                'w-full'
            ).props('header-class="bg-primary text-white font-bold text-lg"'):
                ui.button(text='Set Destination', icon='output', on_click=self.pick_destination).classes('w-full')

                if self.dst_path:
                    ui.button(text='Export', icon='play_arrow', on_click=self.execute).classes('w-full')
                else:
                    ui.button(text='Export', icon='play_arrow', on_click=self.execute).classes('w-full').props('hidden')

    def tree_view(self):
        """Tree view"""
        with ui.row().classes('w-full h-full no-wrap'):
            self.show_gui_tree('original')
            self.show_gui_tree('search')
            self.show_gui_tree('file_modifications')
            self.show_gui_tree('folder_modifications')

    def process_search(self):
        """Process filters"""
        filters_iter, collisions, inactive = self.filter_logic.apply_search(self.filters_handler)

        if filters_iter is None:
            ui.notify(message='The filters must first be defined before they can be applied', type='info')
            return None

        if collisions:
            with ui.dialog().classes('no-wrap') as collision_dialog, ui.card():
                collision_dialog.open()
                ui.label('Filter collisions:').style('font-size: 20px; font-weight: bold; color: #3874c8')
                with ui.scroll_area().style('height: 500px; width: 500px;'):
                    for filter_names in collisions:
                        ui.label(f'{filter_names}, here a subset of collisions:').style(
                            'font-size: 20px; font-weight: bold;'
                        )
                        for collision in collisions[filter_names]:
                            ui.label(collision).style('font-size: 15px; font-weight: bold;')
                ui.button(text='Close', on_click=collision_dialog.close)
            return None

        if inactive:
            with ui.dialog() as inactive_dialog, ui.card():
                inactive_dialog.open()
                ui.label('Inactive Filter:').style('font-size: 20px; font-weight: bold; color: #3874c8').classes(
                    'w-full'
                )
                for filter_name in inactive:
                    ui.label(filter_name).style('font-size: 15px; font-weight: bold;')
                ui.button(text='Close', on_click=inactive_dialog.close)
            return None

        self.filters_handler.set(state='search', filters_iter=filters_iter)
        self.update_state(self.filters_handler, state='search', path_type='file_path_rel')

    def process_file_mods(self):
        """Process file modifications"""
        filters_iter = self.filter_logic.apply_file_modifications(self.filters_handler)

        if filters_iter is None:
            ui.notify(message='The modifications must first be defined before they can be applied', type='info')
            return None

        self.filters_handler.set(state='file_modifications', filters_iter=filters_iter)
        self.expand.update({'search': False})
        self.update_state(self.filters_handler, state='file_modifications', path_type='new_file_path_rel')

    def process_folder_mods(self):
        filters_iter = self.filter_logic.apply_folder_modifications(self.filters_handler)

        if filters_iter is None:
            ui.notify(message='The modifications must first be defined before they can be applied', type='info')
            return None

        self.filters_handler.set(state='folder_modifications', filters_iter=filters_iter)
        self.expand.update({'file_modifications': False})
        self.update_state(self.filters_handler, state='folder_modifications', path_type='new_file_path_rel')

    async def pick_source(self) -> None:
        """Pick source folder"""

        src_path = await LocalFolderPicker('~')

        if src_path is None:
            return None

        if self.src_path:
            self.reset_gui()

        subject_creator = SubjectCreator(src_path)
        subject_iter = subject_creator()
        filters_iter = FiltersIterator(original=subject_iter)
        self.filters_handler.set(state='original', filters_iter=filters_iter)

        if len(subject_iter) == 0:
            ui.notify(message=f'No files found in {src_path}', type='negative')
            return None

        if len(subject_iter) >= 5000:
            ui.notify(
                message="To many files to show, only the first 5'000 are presented here."
                f"However, all of the files in {src_path} will be processed.",
                multi_line=True,
                type='info',
            )
            self.show_tree['original'] = False

        self.src_path = src_path
        self.update_state(self.filters_handler, state='original', path_type='file_path_rel')

    def update_state(self, subject_handler, state, path_type):
        self.gui_handler.subject_handler_to_gui_handler(subject_handler, state, path_type)
        self.show_gui_tree.refresh()
        self.left_drawer_update.refresh()

    def reset_gui(self):
        """Reset the gui"""
        self.src_path = None
        self.dst_path = None

        self.expand = {'search': True, 'file_modifications': True, 'folder_modifications': True}
        self.show_tree = {'original': True, 'search': True, 'file_modifications': True, 'folder_modifications': True}

        self.gui_handler = GuiHandler()
        self.filter_logic = FilterLogic()
        self.filters_handler = FiltersHandler()

        self.search_widget = SearchWidget()
        self.file_mod_widget = FileModWidget()
        self.folder_mod_widget = FolderModWidget()

        self.left_drawer_update.refresh()
        self.show_gui_tree.refresh()

    async def pick_destination(self) -> None:
        """Pick destination folder"""

        self.dst_path = await LocalFolderPicker('~')
        if self.dst_path is None:
            return None

        ui.notify(f'Your output will be in {self.dst_path}')
        self.left_drawer_update.refresh()

    def execute(self):
        """Execute the file modifications"""
        if self.dst_path is None:
            ui.notify(message='You must first set the destination folder', type='info')
            return None

        self.filter_logic.apply_new_structure(self.filters_handler, self.dst_path)
        ui.notify(message=f'Copied files to new structure in {self.dst_path}', type='positive')

    def tree_menu(self, state):
        """Tree menu"""

        def tree_filter(e, _state):
            if e.value == '':
                getattr(self.gui_handler, state).tree_gui._props['filter'] = ''
            else:
                getattr(self.gui_handler, state).tree_gui._props['filter'] = e.value
            getattr(self.gui_handler, state).tree_gui.expand()

        def switch(e, _state):
            self.show_tree[_state] = e.value
            self.show_gui_tree.refresh()

        tree_name = state.replace('_', ' ').capitalize()
        with ui.row().classes('w-full no-wrap'):
            ui.label(tree_name).style('font-size: 20px; font-weight: bold; color: #3874c8')
            ui.switch(text='', value=self.show_tree[state], on_change=lambda e, _state=state: switch(e, _state))

        if self.show_tree[state]:
            with ui.row().classes('w-full no-wrap'):
                ui.input(label='Search', on_change=lambda e, _state=state: tree_filter(e, _state))
                ui.button(
                    icon='expand_more',
                    on_click=lambda e: getattr(self.gui_handler, state).tree_gui.props('filter=').expand(),
                )
                ui.button(
                    icon='expand_less',
                    on_click=lambda e: getattr(self.gui_handler, state).tree_gui.props('filter=').collapse(),
                )
            file_counts, top_level_folders_count = self.filters_handler.counts(state)

            with ui.row().classes('w-full no-wrap'):
                ui.label(f'Top Level Folders Count: {top_level_folders_count}').style(
                    'font-size: 15px; font-weight: bold;'
                )
                ui.label(f'Files Count: {file_counts}').style('font-size: 15px; font-weight: bold;')

    @ui.refreshable
    def show_gui_tree(self, state) -> None:
        """Show gui tree"""
        if getattr(self.gui_handler, state):
            if self.show_tree[state]:
                classes = 'w-full h-full no-wrap'
            else:
                classes = 'h-full no-wrap'

            with ui.column().classes(classes):
                self.tree_menu(state)
                if self.show_tree[state]:
                    with ui.scroll_area().style('height: 1000px;'):
                        tree = ui.tree(getattr(self.gui_handler, state).tree_format, label_key='id').expand()
                        del tree._props['selected']
                        getattr(self.gui_handler, state).tree_gui = tree
