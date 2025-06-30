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
            box = layout.box()
            for item in getattr(iface, "items_tree", []):
                if getattr(item, "in_out", None) == 'INPUT':
                    inp = ctx.inputs.get(item.name)
                    if inp:
                        prop = inp.prop_name()
                        if prop:
                            if item.socket_type == 'FNSocketExec':
                                op = box.operator('file_nodes.trigger_exec', text=item.name, icon='PLAY')
                                op.tree_name = tree.name
                                op.socket_name = item.name
                                op.group_input = True
                            else:
                                box.prop(inp, prop, text=item.name)


def _tree_prop_update(self, context):
    tree = self.file_nodes_tree
    if tree and getattr(tree, "interface", None) and getattr(tree, "fn_inputs", None):
        try:
            tree.interface_update(context)
        except Exception as exc:
            if hasattr(self, "report"):
                self.report({'ERROR'}, f"File Nodes: {exc}")
            else:
                print(f"File Nodes: {exc}")


def register():
    bpy.utils.register_class(FILE_NODES_PT_global)
    bpy.types.Scene.file_nodes_tree = bpy.props.PointerProperty(
        type=FileNodesTree,
        update=_tree_prop_update,
    )


def unregister():
    del bpy.types.Scene.file_nodes_tree
    bpy.utils.unregister_class(FILE_NODES_PT_global)
