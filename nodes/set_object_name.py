"""Node to rename an object."""

import bpy
from bpy.types import Node
from .base import FNBaseNode
from ..sockets import FNSocketObject, FNSocketString



class FNSetObjectName(Node, FNBaseNode):
    """Change the name of an object."""
    bl_idname = "FNSetObjectName"
    bl_label = "Set Object Name"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketObject', "Object")
        sock = self.inputs.new('FNSocketString', "Name")
        sock.value = ""
        self.outputs.new('FNSocketObject', "Object")

    def process(self, context, inputs, manager):
        obj = inputs.get("Object")
        if obj:
            name = inputs.get("Name") or ""
            try:
                obj.name = name
            except Exception:
                pass
        return {"Object": obj}


def register():
    bpy.utils.register_class(FNSetObjectName)


def unregister():
    bpy.utils.unregister_class(FNSetObjectName)