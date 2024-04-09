import copy

from nicegui import ui

from file_star.core.mods.filter_logic import FilterLogic


class CurrentTab:
    active: str

    def __init__(self):
        self.active = ''


class CurrentExpansion:
    """Current expansions states"""

    def __init__(self, data_dict):
        for filter_name, value in data_dict.items():  # Iterate through the dictionary and set class attributes
            for folder_struct, _ in value.items():
                setattr(CurrentExpansion, f'{filter_name}_{folder_struct}', False)


class FolderModWidget(FilterLogic):
    """Modifications widget"""

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self._shared_state.update(kwargs)

        self.folder_modifications = {}
        self.current_tab = CurrentTab()
        self.current_expansion = None

    def get_widget(self):
        """Return ui"""

        return self.tab_view()

    def init_mods(self):
        """Init mods"""

        sub_template = {
            'find_folder_by_level': False,
            'find_folder_by_name': False,
            'new_folder_name': False,
            'split_folder_name_parts': None,
            'replace_folder_name_parts': None,
            'add_folder_prefix_suffix': None,
        }

        template = {
            'top_folder': copy.deepcopy(sub_template),
            'folder': copy.deepcopy(sub_template),
            'sub_folder': copy.deepcopy(sub_template),
        }

        if self.filter_names:
            for filter_name in self.filter_names:
                if filter_name not in self.folder_modifications:
                    self.folder_modifications[filter_name] = copy.deepcopy(template)
                    self.current_expansion = CurrentExpansion(self.folder_modifications)

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

    def update_mod_store(self, e):
        """Update mod store"""

        filter_name, folder_struct, mod_name = e
        if self.folder_modifications[filter_name][folder_struct][mod_name]:
            self.folder_modifications[filter_name][folder_struct][mod_name] = False
        else:
            self.folder_modifications[filter_name][folder_struct][mod_name] = True
        self.update_available_mods(filter_name, folder_struct, mod_name)

    def update_available_mods(self, filter_name, folder_struct, mod_name):
        """Update available mods"""

        if mod_name == 'find_folder_by_level':
            if self.folder_modifications[filter_name][folder_struct][mod_name]:
                for mod_name in ['find_folder_by_name', 'new_folder_name']:
                    self.folder_modifications[filter_name][folder_struct][mod_name] = None

                for mod_name in ['split_folder_name_parts', 'replace_folder_name_parts', 'add_folder_prefix_suffix']:
                    if mod_name in self.folder_modifications[filter_name][folder_struct]:
                        self.folder_modifications[filter_name][folder_struct][mod_name] = False
            else:
                for mod_name in ['find_folder_by_name', 'new_folder_name']:
                    self.folder_modifications[filter_name][folder_struct][mod_name] = False

                for mod_name in ['split_folder_name_parts', 'replace_folder_name_parts', 'add_folder_prefix_suffix']:
                    if mod_name in self.folder_modifications[filter_name][folder_struct]:
                        self.folder_modifications[filter_name][folder_struct][mod_name] = None

        elif mod_name == 'find_folder_by_name':
            if self.folder_modifications[filter_name][folder_struct][mod_name]:
                for mod_name in ['find_folder_by_level', 'new_folder_name']:
                    if mod_name in self.folder_modifications[filter_name][folder_struct]:
                        self.folder_modifications[filter_name][folder_struct][mod_name] = None

                for mod_name in ['split_folder_name_parts', 'replace_folder_name_parts', 'add_folder_prefix_suffix']:
                    if mod_name in self.folder_modifications[filter_name][folder_struct]:
                        self.folder_modifications[filter_name][folder_struct][mod_name] = False
            else:
                for mod_name in ['find_folder_by_level', 'new_folder_name']:
                    if mod_name in self.folder_modifications[filter_name][folder_struct]:
                        self.folder_modifications[filter_name][folder_struct][mod_name] = False

                for mod_name in ['split_folder_name_parts', 'replace_folder_name_parts', 'add_folder_prefix_suffix']:
                    if mod_name in self.folder_modifications[filter_name][folder_struct]:
                        self.folder_modifications[filter_name][folder_struct][mod_name] = None

        elif mod_name == 'new_folder_name':
            if self.folder_modifications[filter_name][folder_struct][mod_name]:
                for mod_name in [
                    'find_folder_by_level',
                    'find_folder_by_name',
                    'split_folder_name_parts',
                    'replace_folder_name_parts',
                    'add_folder_prefix_suffix',
                ]:
                    if mod_name in self.folder_modifications[filter_name][folder_struct]:
                        self.folder_modifications[filter_name][folder_struct][mod_name] = None

            else:
                for mod_name in ['find_folder_by_level', 'find_folder_by_name']:
                    self.folder_modifications[filter_name][folder_struct][mod_name] = False

        self.tab_view.refresh()

    def copy_mods(self, _filter_name):
        """Copy mods from one filter to all other filters"""

        template_mods = self.folder_modifications[_filter_name]
        for filter_name in self.filter_names:
            if filter_name != _filter_name:
                self.folder_modifications[filter_name] = copy.deepcopy(template_mods)
        self.tab_view.refresh()

    def mod_mask(self, filter_name):
        """Filter mask"""

        mod_description = {
            'find_folder_by_level': 'Find folder by level',
            'find_folder_by_name': 'Find folder by name',
            'new_folder_name': 'Replace current folder name with new folder name',
            'split_folder_name_parts': 'Split certain parts of folder name',
            'replace_folder_name_parts': 'Replace certain parts of folder name with new parts',
            'add_folder_prefix_suffix': 'Add prefix and/or suffix to folder name',
        }

        with ui.row().classes('w-full'):
            ui.label('Folder Modifications'.format(filter_name)).style(
                'font-size: 20px; font-weight: bold; color: #3874c8;'
            )
            ui.button(
                'Template',
                on_click=lambda e, x=filter_name: self.copy_mods(x),
            ).classes(
                'ml-auto'
            ).tooltip('Copy mods from this filter to all other filters')

        for folder_struct in self.folder_modifications[filter_name]:
            show_folder_name = folder_struct.replace('_', ' ').capitalize()
            with ui.expansion(show_folder_name).classes('w-full') as exp:
                exp.bind_value(self.current_expansion, f'{filter_name}_{folder_struct}')
                for mod_name in self.folder_modifications[filter_name][folder_struct]:
                    mod_name_to_show = mod_name.replace('_', ' ').capitalize()
                    if self.folder_modifications[filter_name][folder_struct][mod_name] is not None:
                        ui.checkbox(
                            text=mod_name_to_show,
                            value=self.folder_modifications[filter_name][folder_struct][mod_name],
                            on_change=lambda x, e=(filter_name, folder_struct, mod_name): self.update_mod_store(e),
                        ).tooltip(mod_description[mod_name]).props('enable')
                        self.get_adequate_mask(filter_name, folder_struct, mod_name)
                    else:
                        ui.checkbox(text=mod_name_to_show, value=False).tooltip(mod_description[mod_name]).props(
                            'disable'
                        )

    def get_adequate_mask(self, filter_name, folder_struct, mod_name):
        """Get adequate mask"""

        if self.folder_modifications[filter_name][folder_struct][mod_name]:
            if mod_name == 'find_folder_by_level':
                return self.get_find_folder_by_level_mask(filter_name, folder_struct, mod_name)

            if mod_name == 'find_folder_by_name':
                return self.find_folder_by_name_mask(filter_name, folder_struct, mod_name)

            if mod_name == 'new_folder_name':
                return self.new_folder_name_mask(filter_name, folder_struct, mod_name)

            if mod_name == 'split_folder_name_parts':
                return self.get_split_mask(filter_name, folder_struct, mod_name)

            if mod_name == 'replace_folder_name_parts':
                return self.get_replace_mask(filter_name, folder_struct, mod_name)

            if mod_name == 'add_folder_prefix_suffix':
                return self.get_prefix_suffix_mask(filter_name, folder_struct, mod_name)

    def get_find_folder_by_level_mask(self, filter_name, folder_struct, mod_name):
        """Get find folder by level mask"""

        store = {'level': None}

        if isinstance(self.folder_modifications[filter_name][folder_struct][mod_name], bool):
            self.folder_modifications[filter_name][folder_struct][mod_name] = store

        def helper(filter_name, folder_struct, mod_name, key, value):
            self.folder_modifications[filter_name][folder_struct][mod_name][key] = value

        with ui.card() as card:
            ui.number(
                label='Level',
                value=self.folder_modifications[filter_name][folder_struct][mod_name]['level']
                if self.folder_modifications[filter_name][folder_struct][mod_name] is not True
                else None,
                format='%d',
                min=0,
                on_change=lambda x, e=(filter_name, folder_struct, mod_name, 'level'): helper(*e, int(x.value)),
            ).classes('w-full no-wrap')

        return card

    def find_folder_by_name_mask(self, filter_name, folder_struct, mod_name):
        """Find folder by name mask"""

        store = {'name': None}

        if isinstance(self.folder_modifications[filter_name][folder_struct][mod_name], bool):
            self.folder_modifications[filter_name][folder_struct][mod_name] = store

        def helper(filter_name, folder_struct, mod_name, key, value):
            self.folder_modifications[filter_name][folder_struct][mod_name][key] = value

        with ui.card() as card:
            ui.input(
                label='Folder name by search tags',
                placeholder='tag_1 & (tag_2 | tag_3) & ~tag_4',
                value=self.folder_modifications[filter_name][folder_struct][mod_name]['name']
                if self.folder_modifications[filter_name][folder_struct][mod_name] is not True
                else None,
                on_change=lambda x, e=(filter_name, folder_struct, mod_name, 'name'): helper(*e, x.value),
            ).tooltip(
                'use logic operators & for and, | for or, ~ for not, '
                'group logic operators with (), no need for string or char quotes'
            ).classes(
                'w-full no-wrap'
            )

        return card

    def new_folder_name_mask(self, filter_name, folder_struct, mod_name):
        """New folder name mask"""

        store = {'name': None}

        if isinstance(self.folder_modifications[filter_name][folder_struct][mod_name], bool):
            self.folder_modifications[filter_name][folder_struct][mod_name] = store

        def helper(filter_name, folder_struct, mod_name, key, value):
            self.folder_modifications[filter_name][folder_struct][mod_name][key] = value

        with ui.card() as card:
            ui.input(
                label='Create new folder name',
                placeholder='tag_1 & (tag_2 | tag_3) & ~tag_4',
                value=self.folder_modifications[filter_name][folder_struct][mod_name]['name']
                if self.folder_modifications[filter_name][folder_struct][mod_name] is not True
                else None,
                on_change=lambda x, e=(filter_name, folder_struct, mod_name, 'name'): helper(*e, x.value),
            ).classes('w-full no-wrap')
        return card

    def get_split_mask(self, filter_name, folder_struct, mod_name):
        """Get split mask"""

        store = {
            'first': {'split': None, 'start': None, 'end': None},
            'second': {'split': None, 'start': None, 'end': None},
            'third': {'split': None, 'start': None, 'end': None},
        }

        if isinstance(self.folder_modifications[filter_name][folder_struct][mod_name], bool):
            self.folder_modifications[filter_name][folder_struct][mod_name] = store

        def helper_int(filter_name, folder_struct, mod_name, step, key, value):
            self.folder_modifications[filter_name][folder_struct][mod_name][step][key] = value

        def helper_str(filter_name, folder_struct, mod_name, step, key, value):
            self.folder_modifications[filter_name][folder_struct][mod_name][step][key] = value

        with ui.card() as card:
            ui.label('Name will split by split char, keeps splitted names in range start to end index')
            ui.label('The selected name parts will be joined with the split char afterwards')
            for step in store:
                ui.label(f'{step.capitalize()} stage')
                with ui.row().classes('w-full no-wrap'):
                    ui.input(
                        'Split char',
                        value=self.folder_modifications[filter_name][folder_struct][mod_name][step]['split'],
                        on_change=lambda x, e=(filter_name, folder_struct, mod_name, step, 'split'): helper_str(
                            *e, x.value
                        ),
                    )
                    ui.number(
                        label='Start index',
                        value=self.folder_modifications[filter_name][folder_struct][mod_name][step]['start'],
                        format='%d',
                        min=0,
                        on_change=lambda x, e=(filter_name, folder_struct, mod_name, step, 'start'): helper_int(
                            *e, int(x.value)
                        ),
                    )
                    ui.number(
                        label='End index',
                        value=self.folder_modifications[filter_name][folder_struct][mod_name][step]['end'],
                        format='%d',
                        min=0,
                        on_change=lambda x, e=(filter_name, folder_struct, mod_name, step, 'end'): helper_int(
                            *e, int(x.value)
                        ),
                    )
        return card

    def get_replace_mask(self, filter_name, folder_struct, mod_name):
        """Get replace mask"""

        store = {
            'first': {'old': None, 'new': ''},
            'second': {'old': None, 'new': ''},
            'third': {'old': None, 'new': ''},
        }
        if isinstance(self.folder_modifications[filter_name][folder_struct][mod_name], bool):
            self.folder_modifications[filter_name][folder_struct][mod_name] = store

        def helper(filter_name, folder_struct, mod_name, step, key, value):
            self.folder_modifications[filter_name][folder_struct][mod_name][step][key] = value

        with ui.card() as card:
            ui.label('The current name part will be replaced with the new name part if present. Regex is supported')
            ui.label('Order of replacement stages: First, Second, Third')
            for step in store:
                ui.label(f'{step.capitalize()} stage')
                with ui.row().classes('w-full no-wrap'):
                    ui.input(
                        'Old',
                        value=self.folder_modifications[filter_name][folder_struct][mod_name][step]['old'],
                        on_change=lambda x, e=(filter_name, folder_struct, mod_name, step, 'old'): helper(*e, x.value),
                    )
                    ui.input(
                        'New',
                        value=self.folder_modifications[filter_name][folder_struct][mod_name][step]['new'],
                        on_change=lambda x, e=(filter_name, folder_struct, mod_name, step, 'new'): helper(*e, x.value),
                    )
        return card

    def get_prefix_suffix_mask(self, filter_name, folder_struct, mod_name):
        """Get prefix suffix mask"""

        store = {'prefix': None, 'suffix': None}

        if isinstance(self.folder_modifications[filter_name][folder_struct][mod_name], bool):
            self.folder_modifications[filter_name][folder_struct][mod_name] = store

        def helper(filter_name, folder_struct, mod_name, key, value):
            self.folder_modifications[filter_name][folder_struct][mod_name][key] = value

        with ui.card() as card:
            with ui.row().classes('w-full no-wrap'):
                ui.input(
                    'Prefix',
                    value=self.folder_modifications[filter_name][folder_struct][mod_name]['prefix'],
                    on_change=lambda x, e=(filter_name, folder_struct, mod_name, 'prefix'): helper(*e, x.value),
                )
                ui.input(
                    'Suffix',
                    value=self.folder_modifications[filter_name][folder_struct][mod_name]['suffix'],
                    on_change=lambda x, e=(filter_name, folder_struct, mod_name, 'suffix'): helper(*e, x.value),
                )
        return card
