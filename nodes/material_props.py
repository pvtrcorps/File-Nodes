import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketMaterial
from ..operators import get_active_mod_item, auto_evaluate_if_enabled


class FNMaterialProps(Node, FNBaseNode):
    bl_idname = "FNMaterialProps"
    bl_label = "Material Properties"

    use_nodes: bpy.props.BoolProperty(
        name="Use Nodes",
        default=True,
        update=auto_evaluate_if_enabled,
    )

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketMaterial', "Material")
        self.outputs.new('FNSocketMaterial', "Material")

    def draw_buttons(self, context, layout):
        layout.prop(self, "use_nodes", text="Use Nodes")

    def process(self, context, inputs):
        mat = inputs.get("Material")
        if mat:
            mod = get_active_mod_item()
            if mod:
                mod.store_original(mat, "use_nodes")
            try:
                mat.use_nodes = self.use_nodes
            except Exception:
                pass
        return {"Material": mat}


def register():
    bpy.utils.register_class(FNMaterialProps)

def unregister():
    bpy.utils.unregister_class(FNMaterialProps)
