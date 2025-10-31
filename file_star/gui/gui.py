import asyncio

from loguru import logger
from nicegui import ui

from file_star.core.mods.filter_logic import FilterLogic
from file_star.core.subjects.filters_handler import FiltersHandler
from file_star.core.subjects.filters_iterator import FiltersIterator
from file_star.core.subjects.subject_creator import SubjectCreator
from file_star.gui.gui_handler import GuiHandler
from file_star.gui.widgets import FileModWidget, FolderModWidget, LocalFolderPicker, SearchWidget


class FileStar:
    """File Star"""

    def __init__(self) -> None:
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

        self.left_drawer_widget = None
        self.drag_drop_area = None

    def __call__(self) -> None:
        self.header()
        self.left_drawer()
        self.drag_drop_view()
        self.tree_view()

    @staticmethod
    def header() -> None:
        """Header"""

        with ui.header().classes('w-full no-wrap'):
            ui.label('File*').style('font-size: 30px; font-weight: bold;')
            ui.link(
                text='Regex101',
                target='https://regex101.com/',
                new_tab=True,
            ).classes(
                'ml-auto text-white text-lg'
            ).tooltip('Not necessary but useful for more advanced searches')

    def left_drawer(self) -> None:
        """Left drawer - create collapsed initially"""

        # Create drawer at top level (required by NiceGUI) but keep it collapsed initially
        self.left_drawer_widget = ui.left_drawer().classes('bg-blue-100 w-full h-full').props('width=400 mini')
        with self.left_drawer_widget:
            self.left_drawer_update()

    def expand_left_drawer(self) -> None:
        """Expand left drawer when source is selected"""

        # Expand drawer by removing mini prop while keeping width=400
        if self.left_drawer_widget:
            # Set width to 400 and remove mini prop - NiceGUI will update props
            self.left_drawer_widget.props('width=400')
            # Ensure mini is removed by updating props without it
            current_props = self.left_drawer_widget._props.copy()
            if 'mini' in current_props:
                del current_props['mini']
                self.left_drawer_widget._props = current_props
                self.left_drawer_widget.update()

    def drag_drop_view(self) -> None:
        """Drag and drop folder selection area"""

        @ui.refreshable
        def show_drag_drop():
            if self.src_path is None:
                # Create a centered container
                with ui.column().classes('w-full h-screen items-center justify-center'):
                    # Simple folder selection card
                    with ui.card().classes('items-center justify-center').style(
                        'min-width: 500px; min-height: 400px; border: 2px solid #e5e7eb; border-radius: 15px; '
                        'padding: 60px; background-color: #ffffff;'
                    ):
                        with ui.column().classes('items-center gap-4'):
                            ui.icon('folder', size='100px').classes('text-gray-400')
                            ui.label('Select a folder to begin').classes('text-2xl font-bold text-gray-600')

                            async def handle_browse():
                                """Handle browse button click"""
                                await self.pick_source()

                            ui.button('Browse for Folder', icon='folder_open', on_click=handle_browse).classes(
                                'mt-4 px-8 py-4 text-lg'
                            )

        self._drag_drop_refreshable = show_drag_drop
        # Actually call the function to render it
        show_drag_drop()

    def drag_drop_view_refresh(self):
        """Refresh the drag and drop view"""
        if hasattr(self, '_drag_drop_refreshable'):
            self._drag_drop_refreshable.refresh()

    @ui.refreshable
    def left_drawer_update(self) -> None:
        """Left drawer update"""

        # Only show sidebar content when original tree view is loaded
        if not self.gui_handler.original:
            return

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
                ui.button(text='Export', icon='output', on_click=self.export).classes('w-full')

    def tree_view(self) -> None:
        """Tree view"""

        @ui.refreshable
        def show_tree_view():
            if self.src_path is None:
                # Don't show tree view when no source is selected
                return

            # Use flex layout to fill available space
            with ui.row().classes('w-full no-wrap').style('height: calc(100vh - 64px);'):
                self.show_gui_tree('original')
                self.show_gui_tree('search')
                self.show_gui_tree('file_modifications')
                self.show_gui_tree('folder_modifications')

        self._tree_view_refreshable = show_tree_view
        show_tree_view()

    def tree_view_refresh(self):
        """Refresh the tree view"""
        if hasattr(self, '_tree_view_refreshable'):
            self._tree_view_refreshable.refresh()

    async def process_search(self) -> None:
        """Process filters"""

        # Show spinner immediately when apply is clicked - open before any processing
        dialog = ui.dialog()
        with dialog, ui.card().classes('items-center gap-4 p-8'):
            ui.spinner(size='lg')
            ui.label('Applying search filters...').classes('text-lg font-bold')

        # Open dialog immediately and yield to event loop to ensure UI updates
        dialog.open()
        await asyncio.sleep(0)  # Yield to event loop to ensure spinner appears

        try:
            # Run blocking operation in executor to not block UI
            loop = asyncio.get_event_loop()
            filters_iter, collisions, inactive = await loop.run_in_executor(
                None, self.filter_logic.apply_search, self.filters_handler
            )

            if filters_iter is None:
                dialog.close()
                ui.notify(message='The filters must first be defined before they can be applied', type='info')
                return None

            if collisions:
                dialog.close()
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
                dialog.close()
                with ui.dialog() as inactive_dialog, ui.card():
                    inactive_dialog.open()
                    ui.label('Inactive Filter:').style('font-size: 20px; font-weight: bold; color: #3874c8').classes(
                        'w-full'
                    )
                    for filter_name in inactive:
                        ui.label(filter_name).style('font-size: 15px; font-weight: bold;')
                    ui.button(text='Close', on_click=inactive_dialog.close)
                return None

            # Update filters and state - keep spinner open during tree view update
            self.filters_handler.set(state='search', filters_iter=filters_iter)
            self.update_state(self.filters_handler, state='search', path_type='file_path_rel')

            # Close spinner immediately after tree view update - no artificial delay
            dialog.close()
        except Exception as e:
            dialog.close()
            logger.error(f"Error processing search: {e}")
            ui.notify(message=f'Error applying search filters: {str(e)}', type='negative')
            return None

    async def process_file_mods(self) -> None:
        """Process file modifications"""

        # Show spinner immediately when apply is clicked
        dialog = ui.dialog()
        with dialog, ui.card().classes('items-center gap-4 p-8'):
            ui.spinner(size='lg')
            ui.label('Applying file modifications...').classes('text-lg font-bold')

        dialog.open()
        # Small delay to ensure dialog is visible
        await asyncio.sleep(0.01)

        try:
            filters_iter = self.filter_logic.apply_file_modifications(self.filters_handler)

            if filters_iter is None:
                dialog.close()
                ui.notify(message='The modifications must first be defined before they can be applied', type='info')
                return None

            # Update filters and state - keep spinner open during tree view update
            self.filters_handler.set(state='file_modifications', filters_iter=filters_iter)
            self.expand.update({'search': False})
            self.update_state(self.filters_handler, state='file_modifications', path_type='new_file_path_rel')

            # Close spinner immediately after tree view update
            dialog.close()
        except Exception as e:
            dialog.close()
            logger.error(f"Error processing file modifications: {e}")
            ui.notify(message=f'Error applying file modifications: {str(e)}', type='negative')
            return None

    async def process_folder_mods(self) -> None:
        """Process folder modifications"""

        # Show spinner immediately when apply is clicked
        dialog = ui.dialog()
        with dialog, ui.card().classes('items-center gap-4 p-8'):
            ui.spinner(size='lg')
            ui.label('Applying folder modifications...').classes('text-lg font-bold')

        dialog.open()
        # Small delay to ensure dialog is visible
        await asyncio.sleep(0.01)

        try:
            filters_iter = self.filter_logic.apply_folder_modifications(self.filters_handler)

            if filters_iter is None:
                dialog.close()
                ui.notify(message='The modifications must first be defined before they can be applied', type='info')
                return None

            # Update filters and state - keep spinner open during tree view update
            self.filters_handler.set(state='folder_modifications', filters_iter=filters_iter)
            self.expand.update({'file_modifications': False})
            self.update_state(self.filters_handler, state='folder_modifications', path_type='new_file_path_rel')

            # Close spinner immediately after tree view update
            dialog.close()
        except Exception as e:
            dialog.close()
            logger.error(f"Error processing folder modifications: {e}")
            ui.notify(message=f'Error applying folder modifications: {str(e)}', type='negative')
            return None

    async def pick_source(self) -> None:
        """Pick source folder"""

        src_path = await LocalFolderPicker('~')

        if src_path is None:
            return None

        await self.load_source_folder(str(src_path))

    async def load_source_folder(self, src_path: str) -> None:
        """Load source folder with spinner"""

        if self.src_path:
            self.reset_gui()

        # Show spinner during file reading
        with ui.dialog() as dialog, ui.card().classes('items-center gap-4 p-8'):
            dialog.open()
            ui.spinner(size='lg')
            ui.label('Reading file system...').classes('text-lg font-bold')
            progress_label = ui.label('Initializing...').classes('text-sm')

            # Update progress callback - use a list to store values for thread-safe access
            progress_data = {'current': 0, 'total': 0}

            def update_progress(current, total):
                progress_data['current'] = current
                progress_data['total'] = total
                try:
                    # Update UI from any thread
                    ui.run_job(lambda: setattr(progress_label, 'text', f'Processing {current} of {total} files...'))
                except Exception:
                    # Fallback if UI update fails
                    pass

            try:
                subject_creator = SubjectCreator(src_path, progress_callback=update_progress)
                subject_iter = await subject_creator.__call_async__()

                if subject_iter is None or len(subject_iter) == 0:
                    dialog.close()
                    ui.notify(message=f'No files found in {src_path}', type='negative')
                    return None

                filters_iter = FiltersIterator(original=subject_iter)
                self.filters_handler.set(state='original', filters_iter=filters_iter)

                self.src_path = src_path

                # Update progress label to show tree building
                progress_label.text = 'Building tree view...'

                # Update state (includes tree building which can take time) - keep spinner open
                self.update_state(self.filters_handler, state='original', path_type='file_path_rel')

                # Expand left drawer after tree view is loaded (after update_state sets gui_handler.original)
                if self.gui_handler.original:
                    self.expand_left_drawer()

                self.drag_drop_view_refresh()
                self.tree_view_refresh()

                # Close dialog immediately after tree view refresh - no artificial delay
                dialog.close()

            except Exception as e:
                dialog.close()
                ui.notify(message=f'Error loading folder: {str(e)}', type='negative')
                import traceback

                logger.error(f"Error loading folder: {traceback.format_exc()}")
                return None

    def update_state(self, subject_handler, state, path_type) -> None:
        """Update the gui state"""

        self.gui_handler.subject_handler_to_gui_handler(subject_handler, state, path_type)
        self.show_gui_tree.refresh()
        self.left_drawer_update.refresh()

    def reset_gui(self) -> None:
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

        # Collapse left drawer on reset
        if self.left_drawer_widget:
            self.left_drawer_widget.props('mini')

        self.left_drawer_update.refresh()
        self.show_gui_tree.refresh()
        self.drag_drop_view_refresh()
        self.tree_view_refresh()

    async def export(self) -> None:
        """Pick destination folder"""

        self.dst_path = await LocalFolderPicker('~')
        if self.dst_path is None:
            return None

        self.expand.update({'folder_modifications': False})

        if self.dst_path is None:
            ui.notify(message='You must first set the destination folder', type='info')
            return None

        # Show spinner immediately when export starts
        dialog = ui.dialog()
        with dialog, ui.card().classes('items-center gap-4 p-8'):
            ui.spinner(size='lg')
            ui.label('Exporting files...').classes('text-lg font-bold')
            progress_label = ui.label('Copying files...').classes('text-sm')

        dialog.open()
        # Small delay to ensure dialog is visible
        await asyncio.sleep(0.01)

        try:
            # Apply new structure (this can take time)
            self.filter_logic.apply_new_structure(self.filters_handler, self.dst_path)

            # Close spinner immediately after export completes
            dialog.close()
            ui.notify(message=f'Copied files to new structure in {self.dst_path}', type='positive')
        except Exception as e:
            dialog.close()
            logger.error(f"Error exporting: {e}")
            ui.notify(message=f'Error exporting files: {str(e)}', type='negative')
            return None

    def tree_menu(self, state) -> None:
        """Tree menu"""

        def tree_filter(e, _state):
            if e.value == '':
                getattr(self.gui_handler, state).tree_gui._props['filter'] = ''
            else:
                getattr(self.gui_handler, state).tree_gui._props['filter'] = e.value
            getattr(self.gui_handler, state).tree_gui.expand()

        async def expand_tree(_state):
            """Expand tree with spinner"""
            # Open dialog immediately before any operation
            dialog = ui.dialog()
            with dialog, ui.card().classes('items-center gap-4 p-8'):
                ui.spinner(size='lg')
                ui.label('Expanding tree...').classes('text-lg font-bold')

            # Open dialog immediately
            dialog.open()
            # Minimal delay to ensure dialog renders
            await asyncio.sleep(0.01)

            try:
                tree_gui = getattr(self.gui_handler, _state).tree_gui
                if tree_gui:
                    tree_gui.props('filter=').expand()
                # Minimal delay for tree expansion
                await asyncio.sleep(0.1)
                dialog.close()
            except Exception:
                dialog.close()

        async def collapse_tree(_state):
            """Collapse tree with spinner"""
            # Open dialog immediately before any operation
            dialog = ui.dialog()
            with dialog, ui.card().classes('items-center gap-4 p-8'):
                ui.spinner(size='lg')
                ui.label('Collapsing tree...').classes('text-lg font-bold')

            # Open dialog immediately
            dialog.open()
            # Minimal delay to ensure dialog renders
            await asyncio.sleep(0.01)

            try:
                tree_gui = getattr(self.gui_handler, _state).tree_gui
                if tree_gui:
                    tree_gui.props('filter=').collapse()
                # Minimal delay for tree collapse
                await asyncio.sleep(0.1)
                dialog.close()
            except Exception:
                dialog.close()

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
                    on_click=lambda e, _state=state: expand_tree(_state),
                )
                ui.button(
                    icon='expand_less',
                    on_click=lambda e, _state=state: collapse_tree(_state),
                )
            analysis = self.filters_handler.analyze_state(state)
            for filter_name in analysis:
                file_counts = analysis[filter_name]['files']
                top_level_folders_count = analysis[filter_name]['top_level_folders']
                with ui.row().classes('w-full no-wrap'):
                    if filter_name != 'original':
                        ui.label(f'{filter_name.upper()}:').style('font-size: 15px; font-weight: bold;')
                    ui.label(f'Top Level Folders: {top_level_folders_count}').style(
                        'font-size: 15px; font-weight: bold;'
                    )
                    ui.label(f'Files: {file_counts}').style('font-size: 15px; font-weight: bold;')

    @ui.refreshable
    def show_gui_tree(self, state) -> None:
        """Show gui tree"""

        if getattr(self.gui_handler, state):
            if self.show_tree[state]:
                classes = 'w-full h-full no-wrap'
            else:
                classes = 'h-full no-wrap'

            # Use flexbox to ensure scroll area fills remaining space after tree menu
            with ui.column().classes(classes).style(
                'height: calc(100vh - 64px); display: flex; flex-direction: column; overflow: hidden;'
            ):
                # Tree menu takes only the space it needs
                with ui.column().classes('flex-shrink-0'):
                    self.tree_menu(state)

                if self.show_tree[state]:
                    # Scroll area fills all remaining space
                    with ui.scroll_area().style('flex: 1 1 auto; min-height: 0; overflow-y: auto;'):
                        tree = ui.tree(getattr(self.gui_handler, state).tree_format, label_key='id')
                        del tree._props['selected']

                        tree.on(
                            'lazy-load',
                            js_handler='''({ node, key, done, fail }) => {
                            console.log('lazy-load', node)
                            fetch(`/tmodel/get-tree-children?object_type=${node.type}&object_id=${node.id}`)
                            .then(response => response.json())
                            .then(data => done(data))
                            .catch(fail);
                        }''',
                        )

                        tree.on(
                            'update:selected',
                            js_handler='''(event) => {
                            console.log('select event:', event)
                        }''',
                        )

                        tree.on('after-expand', lambda e: print('Expanded:', e.args))
                        tree.on('after-collapse', lambda e: print('Collapsed:', e.args))

                        getattr(self.gui_handler, state).tree_gui = tree
