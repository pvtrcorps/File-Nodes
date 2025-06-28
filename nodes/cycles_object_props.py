import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketObject, FNSocketBool



class FNCyclesObjectProps(Node, FNBaseNode):
    bl_idname = "FNCyclesObjectProps"
    bl_label = "Cycles Object Properties"


    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketObject', "Object")
        sock = self.inputs.new('FNSocketBool', "Holdout")
        sock.value = False
        self.outputs.new('FNSocketObject', "Object")

    def process(self, context, inputs):
        obj = inputs.get("Object")
        if obj:
            holdout = inputs.get("Holdout")
            ctx = getattr(getattr(self, "id_data", None), "fn_inputs", None)
            if ctx:
                ctx.store_original(obj, "is_holdout")
            try:
                obj.is_holdout = holdout
            except Exception:
                pass
        return {"Object": obj}


def register():
    bpy.utils.register_class(FNCyclesObjectProps)

def unregister():
    bpy.utils.unregister_class(FNCyclesObjectProps)
