import copy

from nicegui import ui
from nicegui.events import KeyEventArguments

from file_star.core.mods.filter_logic import FilterLogic


class SearchWidget(FilterLogic):
    """Search widget"""

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self._shared_state.update(kwargs)

        self.search = {}  # from Borg
        self.search_name = None
        self.remove_checkbox = {}

    def get_widget(self, callback):
        """Return ui"""
        return self.tab_view(callback)

    def search_mask(self, name):
        """Search mask"""
        self.search[name]['search_name'] = name
        for key in self.search[name]:
            if key == 'search_name':
                continue
            with ui.row().classes('w-full'):
                key_to_show = key.replace('_', ' ').title()
                ui.input(
                    label=key_to_show,
                    placeholder='tag_1 & (tag_2 | tag_3) & ~tag_4',
                    value=self.search[name][key] if self.search[name][key] else None,
                    on_change=lambda x, e=key: self.search[name].update({e: str(x.value)}),
                ).tooltip(
                    'use logic operators & for and, | for or, ~ for not, '
                    'group logic operators with [], no need for string or char quotes, regex is supported'
                ).classes(
                    'w-full'
                )

    @ui.refreshable
    def tab_view(self, callback):
        """Tab view for all searches"""
        with ui.row().classes('w-full no-wrap'):
            ui.button('Add Filter').on('click', self.add_dialog)

            if self.search:
                ui.button('Remove Filter').on('click', self.remove_dialog)
            else:
                ui.button('Remove Filter').on('click', self.remove_dialog).props('hidden')

        with ui.card().tight().classes('w-full'):
            last_tab = None
            with ui.tabs().classes('w-full') as tabs:
                for search_name in self.search:
                    last_tab = ui.tab(search_name)

            with ui.tab_panels(tabs, animated=False, value=last_tab).classes('w-full'):
                for search_name in self.search:
                    with ui.tab_panel(search_name).classes('w-full'):
                        self.search_mask(search_name)

        if self.search:
            ui.button('Apply', on_click=callback)
        else:
            ui.button('Apply', on_click=None).props('hidden')

    def remove_dialog(self):
        """Remove filter dialog"""

        def remove():
            for name in self.remove_checkbox:
                if self.remove_checkbox[name]:
                    self.search.pop(name)

            self.dialog.close()
            self.tab_view.refresh()
            self.remove_checkbox = {}

        with ui.dialog() as self.dialog, ui.card():
            self.dialog.open()

            for search_name in [*self.search]:
                ui.checkbox(search_name, on_change=lambda x, e=search_name: self.remove_checkbox.update({e: x.value}))

            with ui.row():
                ui.button('Remove', on_click=remove)
                ui.button('Close', on_click=self.dialog.close)

    def add_dialog(self):
        """Add filter dialog"""

        template = {'search_name': None, 'file_name': None, 'extension_name': None, 'folder_name': None}

        def add():
            if self.search_name.value:
                if self.search_name.value in self.search:
                    ui.notify('Search name already exists', type='negative')
                    return None
                self.search[self.search_name.value] = copy.deepcopy(template)
                self.search_name = None
                self.dialog.close()
                self.tab_view.refresh()
            else:
                ui.notify('Please provide a search name', type='info')

        def handle_key(e: KeyEventArguments):
            if e.action.keydown and not e.action.repeat:
                if e.key == 'Enter':
                    add()

        ui.keyboard(on_key=handle_key, ignore=[])

        with ui.dialog() as self.dialog, ui.card():
            self.dialog.open()
            self.search_name = ui.input('Filter Name').props('autofocus')
            with ui.row():
                ui.button('Save', on_click=add)
                ui.button('Close', on_click=self.dialog.close)
