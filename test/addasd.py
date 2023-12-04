from nicegui import ui
#
# t = ui.tree([
#     {'id': 'A', 'children': [{'id': 'A1', 'children': [{'id': 'Test'}]}, {'id': 'A2'}]},
#     {'id': 'B', 'children': [{'id': 'B1'}, {'id': 'B2'}]},
# ], label_key='id').collapse()
#
# t.expand(['A', 'A1'])

with ui.expansion().props('header-class=bg-secondary'):
    ui.label('Hello')

ui.run()
