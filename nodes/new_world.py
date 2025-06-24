import bpy
from bpy.types import Node
from .base import FNBaseNode
from ..sockets import FNSocketWorld
from ..operators import auto_evaluate_if_enabled

class FNNewWorld(Node, FNBaseNode):
    bl_idname = "FNNewWorld"
    bl_label = "New World"

    name: bpy.props.StringProperty(name="Name", default="World", update=auto_evaluate_if_enabled)

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.outputs.new('FNSocketWorld', "World")

    def draw_buttons(self, context, layout):
        layout.prop(self, "name", text="Name")

    def process(self, context, inputs):
        world = bpy.data.worlds.new(self.name)
        return {"World": world}


def register():
    bpy.utils.register_class(FNNewWorld)


def unregister():
    bpy.utils.unregister_class(FNNewWorld)
