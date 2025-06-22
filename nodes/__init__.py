
import bpy, importlib
from . import read_blend, create_list, get_item_by_name, set_world, group_input, group_output

_modules = [read_blend, create_list, get_item_by_name, set_world, group_input, group_output]

def register():
    for m in _modules:
        importlib.reload(m)
        if hasattr(m, 'register'):
            m.register()

def unregister():
    for m in reversed(_modules):
        if hasattr(m, 'unregister'):
            m.unregister()
