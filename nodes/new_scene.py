import bpy
from bpy.types import Node
from .base import FNBaseNode
from ..sockets import FNSocketScene, FNSocketString

class FNNewScene(Node, FNBaseNode):
    bl_idname = "FNNewScene"
    bl_label = "New Scene"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        sock = self.inputs.new('FNSocketString', "Name")
        sock.value = "Scene"
        self.outputs.new('FNSocketScene', "Scene")

    def process(self, context, inputs):
        name = inputs.get("Name") or "Scene"
        scene = bpy.data.scenes.new(name)
        return {"Scene": scene}


def register():
    bpy.utils.register_class(FNNewScene)


def unregister():
    bpy.utils.unregister_class(FNNewScene)
