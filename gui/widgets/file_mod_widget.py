import copy

from nicegui import ui

from core.mods.filter_logic import FilterLogic


class CurrentTab:
    active: str

    def __init__(self):
        self.active = ''


class FileModWidget(FilterLogic):
    """Modifications widget"""

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self._shared_state.update(kwargs)

        self.file_modifications = {}
        self.current_tab = CurrentTab()

    def get_widget(self):
        """Return ui"""
        return self.tab_view()

    def init_mods(self):
        template = {
            'new_file_name': False,
            'split_file_name_parts': False,
            'replace_file_name_parts': False,
            'add_file_prefix_suffix': False,
        }

        if self.filter_names:
            for filter_name in self.filter_names:
                if filter_name not in self.file_modifications:
                    self.file_modifications[filter_name] = copy.deepcopy(template)

    @ui.refreshable
    def tab_view(self):
        """Tab view for all filters"""

        self.init_mods()

        if self.filter_names:
            with ui.card().tight().classes('w-full'):
                with ui.tabs().classes('w-full').bind_value(self.current_tab, 'active') as tabs:
                    for filter_name in self.filter_names:
                        ui.tab(filter_name)

                self.current_tab.active = self.current_tab.active if self.current_tab.active else filter_name

                with ui.tab_panels(tabs, animated=False, value=self.current_tab.active).classes('w-full'):
                    for filter_name in self.filter_names:
                        with ui.tab_panel(filter_name).classes('w-full'):
                            self.mod_mask(filter_name)

    def update_mod(self, e):
        filter_name, mod_name = e
        if self.file_modifications[filter_name][mod_name]:
            self.file_modifications[filter_name][mod_name] = False
        else:
            self.file_modifications[filter_name][mod_name] = True
        self.update_available_mods(filter_name, mod_name)

    def update_available_mods(self, filter_name, changed_mod_name):
        if changed_mod_name == 'new_file_name':
            for mod_name in ['add_file_prefix_suffix', 'split_file_name_parts', 'replace_file_name_parts']:
                self.file_modifications[filter_name][mod_name] = (
                    None if self.file_modifications[filter_name][changed_mod_name] else False
                )

        else:
            self.file_modifications[filter_name]['new_file_name'] = (
                None if self.file_modifications[filter_name][changed_mod_name] else False
            )

        self.tab_view.refresh()

    def mod_mask(self, filter_name):
        """Filter mask"""

        mod_description = {
            'new_file_name': 'Replace current file name with new file name',
            'split_file_name_parts': 'Strip certain parts of file name',
            'replace_file_name_parts': 'Replace certain parts of file name with new parts',
            'add_file_prefix_suffix': 'Add prefix and/or suffix to file name',
        }

        ui.label('File Modifications'.format(filter_name)).style('font-size: 20px; font-weight: bold; color: #3874c8;')

        for mod_name in self.file_modifications[filter_name]:
            mod_name_to_show = mod_name.replace('_', ' ').capitalize()
            if self.file_modifications[filter_name][mod_name] is not None:
                ui.checkbox(
                    text=mod_name_to_show,
                    value=self.file_modifications[filter_name][mod_name],
                    on_change=lambda x, e=(filter_name, mod_name): self.update_mod(e),
                ).tooltip(mod_description[mod_name]).props('enable')

                self.get_adequate_mask(filter_name, mod_name)
            else:
                ui.checkbox(text=mod_name_to_show, value=False).tooltip(mod_description[mod_name]).props('disable')

    def get_adequate_mask(self, filter_name, mod_name):
        if self.file_modifications[filter_name][mod_name]:
            if mod_name == 'split_file_name_parts':
                return self.get_split_mask(filter_name, mod_name)

            if mod_name == 'replace_file_name_parts':
                return self.get_replace_mask(filter_name, mod_name)

            if mod_name == 'new_file_name':
                return self.get_new_file_name_mask(filter_name, mod_name)

            if mod_name == 'add_file_prefix_suffix':
                return self.get_prefix_suffix_mask(filter_name, mod_name)

    def get_new_file_name_mask(self, filter_name, mod_name):
        store = {'name': None}

        if isinstance(self.file_modifications[filter_name][mod_name], bool):
            self.file_modifications[filter_name][mod_name] = store

        def helper(filter_name, mod_name, key, value):
            self.file_modifications[filter_name][mod_name][key] = value

        with ui.card() as card:
            ui.input(
                value=self.file_modifications[filter_name][mod_name]['name']
                if self.file_modifications[filter_name][mod_name] is not True
                else None,
                on_change=lambda x, e=(filter_name, mod_name, 'name'): helper(*e, x.value),
            ).classes('w-full')
        return card

    def get_replace_mask(self, filter_name, mod_name):
        store = {
            'first': {'old': None, 'new': None},
            'second': {'old': None, 'new': None},
            'third': {'old': None, 'new': None},
        }

        if isinstance(self.file_modifications[filter_name][mod_name], bool):
            self.file_modifications[filter_name][mod_name] = store

        def helper(filter_name, mod_name, step, key, value):
            self.file_modifications[filter_name][mod_name][step][key] = value

        with ui.card() as card:
            ui.label('The current name part will be replaced with the new name part if present.')
            ui.label('Order of replacement stages: First, Second, Third')
            for step in store:
                ui.label(f'{step.capitalize()} stage')
                with ui.row().classes('w-full no-wrap'):
                    ui.input(
                        'Old',
                        value=self.file_modifications[filter_name][mod_name][step]['old'],
                        on_change=lambda x, e=(filter_name, mod_name, step, 'old'): helper(*e, x.value),
                    )
                    ui.input(
                        'New',
                        value=self.file_modifications[filter_name][mod_name][step]['new'],
                        on_change=lambda x, e=(filter_name, mod_name, step, 'new'): helper(*e, x.value),
                    )
        return card

    def get_split_mask(self, filter_name, mod_name):
        store = {
            'first': {'split': None, 'start': None, 'end': None},
            'second': {'split': None, 'start': None, 'end': None},
            'third': {'split': None, 'start': None, 'end': None},
        }

        if isinstance(self.file_modifications[filter_name][mod_name], bool):
            self.file_modifications[filter_name][mod_name] = store

        def helper_int(filter_name, mod_name, step, key, value):
            if value < 0:
                value = 0
            self.file_modifications[filter_name][mod_name][step][key] = value

        def helper_str(filter_name, mod_name, step, key, value):
            self.file_modifications[filter_name][mod_name][step][key] = value

        with ui.card() as card:
            ui.label('Name will split by split char, keeps splitted names in range start to end index')
            ui.label('The selected name parts will be joined with the split char afterwards')
            for step in store:
                ui.label(f'{step.capitalize()} stage')
                with ui.row().classes('w-full no-wrap'):
                    ui.input(
                        'Split char',
                        value=self.file_modifications[filter_name][mod_name][step]['split'],
                        on_change=lambda x, e=(filter_name, mod_name, step, 'split'): helper_str(*e, x.value),
                    )

                    ui.number(
                        label='Start index',
                        value=self.file_modifications[filter_name][mod_name][step]['start'],
                        format='%d',
                        on_change=lambda x, e=(filter_name, mod_name, step, 'start'): helper_int(*e, int(x.value)),
                    )
                    ui.number(
                        label='End index',
                        value=self.file_modifications[filter_name][mod_name][step]['end'],
                        format='%d',
                        on_change=lambda x, e=(filter_name, mod_name, step, 'end'): helper_int(*e, int(x.value)),
                    )
        return card

    def get_prefix_suffix_mask(self, filter_name, mod_name):
        store = {'prefix': None, 'suffix': None}

        if isinstance(self.file_modifications[filter_name][mod_name], bool):
            self.file_modifications[filter_name][mod_name] = store

        def helper(filter_name, mod_name, key, value):
            self.file_modifications[filter_name][mod_name][key] = value

        with ui.card() as card:
            with ui.row().classes('w-full no-wrap'):
                ui.input(
                    'Prefix',
                    value=self.file_modifications[filter_name][mod_name]['prefix'],
                    on_change=lambda x, e=(filter_name, mod_name, 'prefix'): helper(*e, x.value),
                )
                ui.input(
                    'Suffix',
                    value=self.file_modifications[filter_name][mod_name]['suffix'],
                    on_change=lambda x, e=(filter_name, mod_name, 'suffix'): helper(*e, x.value),
                )
        return card
