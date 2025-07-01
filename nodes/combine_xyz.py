"""Node that combines X, Y and Z values into a vector."""

import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketFloat, FNSocketVector


class FNCombineXYZ(Node, FNBaseNode):
    """Combine separate X, Y and Z inputs into a vector."""
    bl_idname = "FNCombineXYZ"
    bl_label = "Combine XYZ"

    def init(self, context):
        self.inputs.new('FNSocketFloat', "X")
        self.inputs.new('FNSocketFloat', "Y")
        self.inputs.new('FNSocketFloat', "Z")
        self.outputs.new('FNSocketVector', "Vector")

    def process(self, context, inputs, manager):
        x = inputs.get("X") or 0.0
        y = inputs.get("Y") or 0.0
        z = inputs.get("Z") or 0.0
        return {"Vector": (x, y, z)}


def register():
    bpy.utils.register_class(FNCombineXYZ)


def unregister():
    bpy.utils.unregister_class(FNCombineXYZ)
