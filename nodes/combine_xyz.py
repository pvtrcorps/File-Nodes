import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketFloat, FNSocketVector


class FNCombineXYZ(Node, FNBaseNode):
    bl_idname = "FNCombineXYZ"
    bl_label = "Combine XYZ"
    color_tag = 'OUTPUT'

    def init(self, context):
        self.inputs.new('FNSocketFloat', "X")
        self.inputs.new('FNSocketFloat', "Y")
        self.inputs.new('FNSocketFloat', "Z")
        self.outputs.new('FNSocketVector', "Vector")

    def process(self, context, inputs):
        x = inputs.get("X") or 0.0
        y = inputs.get("Y") or 0.0
        z = inputs.get("Z") or 0.0
        return {"Vector": (x, y, z)}


def register():
    bpy.utils.register_class(FNCombineXYZ)


def unregister():
    bpy.utils.unregister_class(FNCombineXYZ)
