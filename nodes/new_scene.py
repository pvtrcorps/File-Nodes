import bpy
from bpy.types import Node
from .base import FNBaseNode
from ..sockets import FNSocketScene
from ..operators import auto_evaluate_if_enabled

class FNNewScene(Node, FNBaseNode):
    bl_idname = "FNNewScene"
    bl_label = "New Scene"

    name: bpy.props.StringProperty(name="Name", default="Scene", update=auto_evaluate_if_enabled)

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.outputs.new('FNSocketScene', "Scene")

    def draw_buttons(self, context, layout):
        layout.prop(self, "name", text="Name")

    def process(self, context, inputs):
        scene = bpy.data.scenes.new(self.name)
        return {"Scene": scene}


def register():
    bpy.utils.register_class(FNNewScene)


def unregister():
    bpy.utils.unregister_class(FNNewScene)
