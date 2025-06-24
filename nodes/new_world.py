import bpy
from bpy.types import Node
from .base import FNBaseNode
from ..sockets import FNSocketWorld, FNSocketString

class FNNewWorld(Node, FNBaseNode):
    bl_idname = "FNNewWorld"
    bl_label = "New World"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        sock = self.inputs.new('FNSocketString', "Name")
        sock.value = "World"
        self.outputs.new('FNSocketWorld', "World")

    def process(self, context, inputs):
        name = inputs.get("Name") or "World"
        world = bpy.data.worlds.new(name)
        return {"World": world}


def register():
    bpy.utils.register_class(FNNewWorld)


def unregister():
    bpy.utils.unregister_class(FNNewWorld)
