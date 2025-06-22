
import bpy
from bpy.types import Panel
from .modifiers import FILE_NODES_UL_modifiers
from . import ADDON_NAME

class FILE_NODES_PT_global(Panel):
    bl_label = "File Nodes"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.template_list("FILE_NODES_UL_modifiers", "", scene, "file_node_modifiers", scene, "file_node_mod_index")
        row = layout.row(align=True)
        row.operator('file_nodes.mod_add', text="", icon='ADD')
        row.operator('file_nodes.mod_remove', text="", icon='REMOVE')
        row.operator('file_nodes.mod_move', text="", icon='TRIA_UP').direction = 'UP'
        row.operator('file_nodes.mod_move', text="", icon='TRIA_DOWN').direction = 'DOWN'
        layout.operator('file_nodes.evaluate', icon='FILE_REFRESH')
        prefs = context.preferences.addons[ADDON_NAME].preferences
        layout.prop(prefs, "auto_evaluate")

def register():
    bpy.utils.register_class(FILE_NODES_PT_global)
def unregister():
    bpy.utils.unregister_class(FILE_NODES_PT_global)
