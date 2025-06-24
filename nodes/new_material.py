import bpy
from bpy.types import Node
from .base import FNBaseNode
from ..sockets import FNSocketMaterial, FNSocketString

class FNNewMaterial(Node, FNBaseNode):
    bl_idname = "FNNewMaterial"
    bl_label = "New Material"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        sock = self.inputs.new('FNSocketString', "Name")
        sock.value = "Material"
        self.outputs.new('FNSocketMaterial', "Material")

    def process(self, context, inputs):
        name = inputs.get("Name") or "Material"
        mat = bpy.data.materials.new(name)
        return {"Material": mat}


def register():
    bpy.utils.register_class(FNNewMaterial)


def unregister():
    bpy.utils.unregister_class(FNNewMaterial)
