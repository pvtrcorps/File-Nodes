import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketWorld
from ..operators import get_active_mod_item, auto_evaluate_if_enabled


class FNWorldProps(Node, FNBaseNode):
    bl_idname = "FNWorldProps"
    bl_label = "World Properties"

    use_nodes: bpy.props.BoolProperty(
        name="Use Nodes",
        default=True,
        update=auto_evaluate_if_enabled,
    )

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketWorld', "World")
        self.outputs.new('FNSocketWorld', "World")

    def draw_buttons(self, context, layout):
        layout.prop(self, "use_nodes", text="Use Nodes")

    def process(self, context, inputs):
        world = inputs.get("World")
        if world:
            mod = get_active_mod_item()
            if mod:
                mod.store_original(world, "use_nodes")
            try:
                world.use_nodes = self.use_nodes
            except Exception:
                pass
        return {"World": world}


def register():
    bpy.utils.register_class(FNWorldProps)

def unregister():
    bpy.utils.unregister_class(FNWorldProps)
