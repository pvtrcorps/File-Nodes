import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketCollection, FNSocketBool



class FNCollectionProps(Node, FNBaseNode):
    bl_idname = "FNCollectionProps"
    bl_label = "Collection Properties"


    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        FNBaseNode.init(self, context)
        self.inputs.new('FNSocketCollection', "Collection")
        sock = self.inputs.new('FNSocketBool', "Hide Viewport")
        sock.value = False
        self.outputs.new('FNSocketCollection', "Collection")

    def process(self, context, inputs):
        coll = inputs.get("Collection")
        if coll:
            hide_vp = inputs.get("Hide Viewport")
            ctx = getattr(getattr(self, "id_data", None), "fn_inputs", None)
            if ctx:
                ctx.store_original(coll, "hide_viewport")
            try:
                coll.hide_viewport = hide_vp
            except Exception:
                pass
        return {"Collection": coll}


def register():
    bpy.utils.register_class(FNCollectionProps)

def unregister():
    bpy.utils.unregister_class(FNCollectionProps)
