from pathlib import Path

from nicegui import events, ui


class LocalFolderPicker(ui.dialog):
    """Local Folder Picker"""

    def __init__(self, path) -> None:
        super().__init__()
        self.path = Path(path).expanduser()
        self.upper_limit = Path('~').expanduser()

        with self, ui.card():

            self.grid = (
                ui.aggrid(
                    {
                        'columnDefs': [{'field': 'name', 'headerName': f'{self.path}'}],
                        'rowSelection': 'single',
                    },
                    html_columns=[0],
                )
                .classes('w-96')
                .on('cellDoubleClicked', self.handle_double_click)
                .style('height: 1000px')
            )

            with ui.row().classes('w-full justify-end'):
                ui.button('Cancel', on_click=self.close).props('outline')
                ui.button('Ok', on_click=self._handle_ok)
        self.update_grid()

    def update_grid(self) -> None:
        """Update grid"""

        paths = list(self.path.glob('*'))
        paths = [p for p in paths if not p.name.startswith('.')]
        paths.sort()

        self.grid.options['columnDefs'][0]['headerName'] = str(self.path)
        self.grid.options['rowData'] = [
            {
                'name': f'📁 <strong>{p.name}</strong>' if p.is_dir() else p.name,
                'path': str(p),
            }
            for p in paths
        ]
        if self.path != self.upper_limit:
            self.grid.options['rowData'].insert(
                0,
                {
                    'name': '📁 <strong>..</strong>',
                    'path': str(self.path.parent),
                },
            )
        self.grid.update()

    def handle_double_click(self, e: events.GenericEventArguments) -> None:
        """Handle double click"""

        self.path = Path(e.args['data']['path'])
        if self.path.is_dir():
            self.update_grid()

    def _handle_ok(self):
        """Handle ok"""

        self.submit(self.path)
