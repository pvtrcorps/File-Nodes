
import bpy
from bpy.types import Panel
from .modifiers import FILE_NODES_UL_modifiers, FileNodeModItem, get_project
from . import ADDON_NAME

class FILE_NODES_PT_global(Panel):
    bl_label = "File Nodes"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'File Nodes'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        project = get_project()
        if not project or not hasattr(project, "modifiers"):
            layout.label(text="File Nodes data not initialized")
            return
        layout.template_list("FILE_NODES_UL_modifiers", "", project, "modifiers", scene, "file_node_mod_index")
        row = layout.row(align=True)
        row.operator('file_nodes.mod_add', text="", icon='ADD')
        row.operator('file_nodes.mod_remove', text="", icon='REMOVE')
        row.operator('file_nodes.mod_move', text="", icon='TRIA_UP').direction = 'UP'
        row.operator('file_nodes.mod_move', text="", icon='TRIA_DOWN').direction = 'DOWN'

        if 0 <= scene.file_node_mod_index < len(project.modifiers):
            mod = project.modifiers[scene.file_node_mod_index]
            box = layout.box()
            for inp in mod.inputs:
                prop = inp.prop_name()
                if prop:
                    box.prop(inp, prop, text=inp.name)

        layout.operator('file_nodes.evaluate', icon='FILE_REFRESH')
        prefs = context.preferences.addons[ADDON_NAME].preferences
        layout.prop(prefs, "auto_evaluate")

def register():
    bpy.utils.register_class(FILE_NODES_PT_global)
def unregister():
    bpy.utils.unregister_class(FILE_NODES_PT_global)
