import bpy
from bpy.types import PropertyGroup
from bpy.props import PointerProperty, CollectionProperty, BoolProperty, IntProperty, StringProperty
from .tree import FileNodesTree

class FileNodeModItem(PropertyGroup):
    name: StringProperty(name="Name")
    node_tree: PointerProperty(type=FileNodesTree)
    enabled: BoolProperty(name="Enabled", default=True)
    stack_index: IntProperty(name="Index", default=0)

class FileRoot(PropertyGroup):
    file_node_modifiers: CollectionProperty(type=FileNodeModItem)
    active_index: IntProperty(name="Active Modifier", default=-1)

def _get_file(self):
    scn = self.scene
    return getattr(scn, 'File', None)

def register():
    bpy.utils.register_class(FileNodeModItem)
    bpy.utils.register_class(FileRoot)
    bpy.types.Scene.File = PointerProperty(type=FileRoot)
    bpy.types.Context.File = property(_get_file)

def unregister():
    del bpy.types.Context.File
    del bpy.types.Scene.File
    bpy.utils.unregister_class(FileRoot)
    bpy.utils.unregister_class(FileNodeModItem)
