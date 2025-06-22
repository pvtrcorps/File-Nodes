
bl_info = {
    "name": "File Nodes MVP",
    "author": "ChatGPT (MVP generator)",
    "version": (0, 1, 0),
    "blender": (4, 4, 0),
    "location": "Node Editor > File Nodes",
    "description": "Prototype node-based file/scene management",
    "category": "Object",
}

import importlib
from . import tree, sockets, nodes, operators, ui, menu, modifiers

modules = [tree, sockets, nodes, operators, ui, menu, modifiers]

def register():
    for m in modules:
        importlib.reload(m)
        if hasattr(m, "register"):
            m.register()

def unregister():
    for m in reversed(modules):
        if hasattr(m, "unregister"):
            m.unregister()
