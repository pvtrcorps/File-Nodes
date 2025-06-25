
import bpy
from bpy.types import Panel
from . import ADDON_NAME

class FILE_NODES_PT_global(Panel):
    bl_label = "File Nodes"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.operator('file_nodes.evaluate', icon='FILE_REFRESH')
        prefs = context.preferences.addons[ADDON_NAME].preferences
        layout.prop(prefs, "auto_evaluate")

def register():
    bpy.utils.register_class(FILE_NODES_PT_global)
def unregister():
    bpy.utils.unregister_class(FILE_NODES_PT_global)
