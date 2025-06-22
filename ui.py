
import bpy
from bpy.types import Panel, UIList, Operator
from .modifiers import FileNodeModItem
from .tree import FileNodesTree


class FILE_NODES_UL_modifiers(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.prop(item, "enabled", text="")
        if item.node_tree:
            row.prop(item.node_tree, "name", text="", emboss=False)
        else:
            row.label(text="<None>")


class FN_OT_mod_add(Operator):
    bl_idname = "file_nodes.mod_add"
    bl_label = "Add File Node Modifier"

    def execute(self, context):
        file = context.scene.File
        item = file.file_node_modifiers.add()
        item.node_tree = bpy.data.node_groups.new("File Nodes", 'FileNodesTreeType')
        item.node_tree.use_fake_user = True
        item.name = item.node_tree.name
        item.stack_index = len(file.file_node_modifiers) - 1
        file.active_index = item.stack_index
        return {'FINISHED'}


class FN_OT_mod_remove(Operator):
    bl_idname = "file_nodes.mod_remove"
    bl_label = "Remove File Node Modifier"

    def execute(self, context):
        file = context.scene.File
        idx = file.active_index
        if 0 <= idx < len(file.file_node_modifiers):
            file.file_node_modifiers.remove(idx)
            file.active_index = min(idx, len(file.file_node_modifiers) - 1)
            for i, it in enumerate(file.file_node_modifiers):
                it.stack_index = i
        return {'FINISHED'}


class FN_OT_mod_move(Operator):
    bl_idname = "file_nodes.mod_move"
    bl_label = "Move Modifier"

    direction: bpy.props.EnumProperty(items=[('UP', 'Up', ''), ('DOWN', 'Down', '')])

    def execute(self, context):
        file = context.scene.File
        idx = file.active_index
        if self.direction == 'UP' and idx > 0:
            file.file_node_modifiers.move(idx, idx - 1)
            file.active_index -= 1
        elif self.direction == 'DOWN' and idx < len(file.file_node_modifiers) - 1:
            file.file_node_modifiers.move(idx, idx + 1)
            file.active_index += 1
        for i, it in enumerate(file.file_node_modifiers):
            it.stack_index = i
        return {'FINISHED'}
class FILE_NODES_PT_global(Panel):
    bl_label = "File Nodes"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        file = context.scene.File
        row = layout.row()
        row.template_list("FILE_NODES_UL_modifiers", "", file, "file_node_modifiers", file, "active_index")
        col = row.column(align=True)
        col.operator('file_nodes.mod_add', text="", icon='ADD')
        col.operator('file_nodes.mod_remove', text="", icon='REMOVE')
        col.separator()
        col.operator('file_nodes.mod_move', text="", icon='TRIA_UP').direction = 'UP'
        col.operator('file_nodes.mod_move', text="", icon='TRIA_DOWN').direction = 'DOWN'

        layout.operator('file_nodes.evaluate', icon='FILE_REFRESH')

classes = (
    FILE_NODES_UL_modifiers,
    FN_OT_mod_add,
    FN_OT_mod_remove,
    FN_OT_mod_move,
    FILE_NODES_PT_global,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
