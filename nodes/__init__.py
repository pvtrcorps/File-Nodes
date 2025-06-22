
import bpy, importlib
# Node modules used by the File Nodes addon. `input_nodes` now contains
# FNWorldInputNode for providing World datablocks.
from . import read_blend, create_list, get_item_by_name, set_world, group_input, group_output, input_nodes

_modules = [read_blend, create_list, get_item_by_name, set_world, group_input, group_output, input_nodes]

def register():
    for m in _modules:
        importlib.reload(m)
        if hasattr(m, 'register'):
            m.register()

def unregister():
    for m in reversed(_modules):
        if hasattr(m, 'unregister'):
            m.unregister()
