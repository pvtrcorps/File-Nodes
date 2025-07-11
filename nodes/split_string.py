"""Node that splits a string by a separator."""

import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketString, FNSocketStringList


class FNSplitString(Node, FNBaseNode):
    """Split an input string into a list of substrings."""
    bl_idname = "FNSplitString"
    bl_label = "Split String"

    def init(self, context):
        self.inputs.new('FNSocketString', "String")
        self.inputs.new('FNSocketString', "Separator")
        self.outputs.new('FNSocketStringList', "Strings")

    def process(self, context, inputs, manager):
        text = inputs.get("String") or ""
        sep = inputs.get("Separator")
        sep = sep if sep is not None else ""
        if sep == "":
            parts = list(text)
        else:
            parts = text.split(sep)
        return {"Strings": parts}


def register():
    bpy.utils.register_class(FNSplitString)


def unregister():
    bpy.utils.unregister_class(FNSplitString)
