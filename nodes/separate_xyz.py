"""Node that separates a vector into X, Y and Z components."""

import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketFloat, FNSocketVector


class FNSeparateXYZ(Node, FNBaseNode):
    """Split a vector into its individual components."""
    bl_idname = "FNSeparateXYZ"
    bl_label = "Separate XYZ"

    def init(self, context):
        self.inputs.new('FNSocketVector', "Vector")
        self.outputs.new('FNSocketFloat', "X")
        self.outputs.new('FNSocketFloat', "Y")
        self.outputs.new('FNSocketFloat', "Z")

    def process(self, context, inputs):
        vec = inputs.get("Vector")
        if isinstance(vec, (list, tuple)) and len(vec) >= 3:
            x, y, z = vec[:3]
        else:
            x = y = z = 0.0
        return {"X": x, "Y": y, "Z": z}


def register():
    bpy.utils.register_class(FNSeparateXYZ)


def unregister():
    bpy.utils.unregister_class(FNSeparateXYZ)
