import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketObject, FNSocketBool



class FNEeveeObjectProps(Node, FNBaseNode):
    bl_idname = "FNEeveeObjectProps"
    bl_label = "Eevee Object Properties"
    color_tag = 'OUTPUT'


    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketObject', "Object")
        sock = self.inputs.new('FNSocketBool', "Visible Shadow")
        sock.value = False
        self.outputs.new('FNSocketObject', "Object")

    def process(self, context, inputs):
        obj = inputs.get("Object")
        if obj:
            shadow = inputs.get("Visible Shadow")
            ctx = getattr(getattr(self, "id_data", None), "fn_inputs", None)
            if ctx:
                ctx.store_original(obj, "visible_shadow")
            try:
                obj.visible_shadow = shadow
            except Exception:
                pass
        return {"Object": obj}


def register():
    bpy.utils.register_class(FNEeveeObjectProps)

def unregister():
    bpy.utils.unregister_class(FNEeveeObjectProps)
