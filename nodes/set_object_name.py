import bpy
from bpy.types import Node
from .base import FNBaseNode
from ..sockets import FNSocketObject, FNSocketString



class FNSetObjectName(Node, FNBaseNode):
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

    def process(self, context, inputs):
        obj = inputs.get("Object")
        if obj:
            name = inputs.get("Name") or ""
            ctx = getattr(getattr(self, "id_data", None), "fn_inputs", None)
            if ctx:
                ctx.store_original(obj, "name")
            try:
                obj.name = name
            except Exception:
                pass
        return {"Object": obj}


def register():
    bpy.utils.register_class(FNSetObjectName)


def unregister():
    bpy.utils.unregister_class(FNSetObjectName)
