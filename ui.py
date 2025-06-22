
import bpy
from bpy.types import Panel
from .tree import FileNodesTree

class FILE_NODES_PT_global(Panel):
    bl_label = "File Nodes"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        trees = [nt for nt in bpy.data.node_groups if isinstance(nt, FileNodesTree)]
        trees.sort(key=lambda t: t.fn_stack_index)
        for t in trees:
            row = col.row(align=True)
            row.prop(t, 'fn_enabled', text='')
            row.label(text=t.name)
            row.prop(t, 'fn_stack_index', text='')
        layout.operator('file_nodes.evaluate', icon='FILE_REFRESH')

def register():
    bpy.utils.register_class(FILE_NODES_PT_global)
def unregister():
    bpy.utils.unregister_class(FILE_NODES_PT_global)
