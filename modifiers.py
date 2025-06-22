import bpy
from bpy.types import PropertyGroup, UIList, Operator
from .tree import FileNodesTree
from .operators import auto_evaluate_if_enabled

class FileNodeModItem(PropertyGroup):
    node_tree: bpy.props.PointerProperty(
        type=FileNodesTree,
        update=auto_evaluate_if_enabled,
    )
    enabled: bpy.props.BoolProperty(
        name="Enabled",
        default=True,
        update=auto_evaluate_if_enabled,
    )
    name: bpy.props.StringProperty(name="Name", default="")
    stack_index: bpy.props.IntProperty(name="Stack Index", default=0, min=0)

class FILE_NODES_UL_modifiers(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, "enabled", text="")
            row.prop(item, "node_tree", text="", icon='NODETREE')
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.prop(item, "enabled", text="")

class FN_OT_mod_add(Operator):
    bl_idname = "file_nodes.mod_add"
    bl_label = "Add File Node Modifier"

    def execute(self, context):
        mods = context.scene.file_node_modifiers
        item = mods.add()
        tree = bpy.data.node_groups.new("File Nodes", 'FileNodesTreeType')
        tree.use_fake_user = True
        iface = tree.interface
        iface.new_socket(name="Scene", in_out='INPUT', socket_type='FNSocketScene')
        iface.new_socket(name="Scene", in_out='OUTPUT', socket_type='FNSocketScene')
        item.node_tree = tree
        item.name = tree.name
        item.stack_index = len(mods) - 1
        context.scene.file_node_mod_index = len(mods) - 1
        return {'FINISHED'}

class FN_OT_mod_remove(Operator):
    bl_idname = "file_nodes.mod_remove"
    bl_label = "Remove File Node Modifier"

    def execute(self, context):
        mods = context.scene.file_node_modifiers
        idx = context.scene.file_node_mod_index
        if 0 <= idx < len(mods):
            mods.remove(idx)
            context.scene.file_node_mod_index = max(0, idx-1)
            for i, m in enumerate(mods):
                m.stack_index = i
        return {'FINISHED'}

class FN_OT_mod_move(Operator):
    bl_idname = "file_nodes.mod_move"
    bl_label = "Move File Node Modifier"

    direction: bpy.props.EnumProperty(items=[('UP','Up',''),('DOWN','Down','')])

    def execute(self, context):
        mods = context.scene.file_node_modifiers
        idx = context.scene.file_node_mod_index
        if self.direction == 'UP' and idx > 0:
            mods.move(idx, idx-1)
            context.scene.file_node_mod_index = idx-1
        elif self.direction == 'DOWN' and idx < len(mods)-1:
            mods.move(idx, idx+1)
            context.scene.file_node_mod_index = idx+1
        for i, m in enumerate(mods):
            m.stack_index = i
        return {'FINISHED'}

classes = (FileNodeModItem, FILE_NODES_UL_modifiers, FN_OT_mod_add, FN_OT_mod_remove, FN_OT_mod_move)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.file_node_modifiers = bpy.props.CollectionProperty(type=FileNodeModItem)
    bpy.types.Scene.file_node_mod_index = bpy.props.IntProperty(default=0)

def unregister():
    del bpy.types.Scene.file_node_modifiers
    del bpy.types.Scene.file_node_mod_index
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
