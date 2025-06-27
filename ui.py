import bpy
from bpy.types import Panel
from . import ADDON_NAME
from .tree import FileNodesTree


class FILE_NODES_PT_global(Panel):
    bl_label = "File Nodes"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        layout.operator("file_nodes.evaluate", icon="FILE_REFRESH")
        prefs = context.preferences.addons[ADDON_NAME].preferences
        layout.prop(prefs, "auto_evaluate")

        scene = context.scene
        layout.template_ID(
            scene,
            "file_nodes_tree",
            new="file_nodes.new_tree",
            unlink="file_nodes.remove_tree",
        )

        tree = scene.file_nodes_tree
        iface = getattr(tree, "interface", None)
        ctx = getattr(tree, "fn_inputs", None)
        if tree and iface and ctx:
            ctx.sync_inputs(tree)
            box = layout.box()
            if hasattr(box, "template_node_view"):
                box.template_node_view(tree, None, None)
            for item in iface.items_tree:
                if getattr(item, "in_out", None) == 'INPUT':
                    inp = ctx.inputs.get(item.name)
                    if inp:
                        prop = inp.prop_name()
                        if prop:
                            box.prop(inp, prop, text=item.name)


def _tree_prop_update(self, context):
    tree = self.file_nodes_tree
    if tree:
        tree.interface_update(context)


def register():
    bpy.utils.register_class(FILE_NODES_PT_global)
    bpy.types.Scene.file_nodes_tree = bpy.props.PointerProperty(
        type=FileNodesTree,
        update=_tree_prop_update,
    )


def unregister():
    del bpy.types.Scene.file_nodes_tree
    bpy.utils.unregister_class(FILE_NODES_PT_global)
