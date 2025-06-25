import bpy
from bpy.types import Node
from .base import FNBaseNode
from ..sockets import FNSocketCollection, FNSocketString



class FNSetCollectionName(Node, FNBaseNode):
    bl_idname = "FNSetCollectionName"
    bl_label = "Set Collection Name"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketCollection', "Collection")
        sock = self.inputs.new('FNSocketString', "Name")
        sock.value = ""
        self.outputs.new('FNSocketCollection', "Collection")

    def process(self, context, inputs):
        coll = inputs.get("Collection")
        if coll:
            name = inputs.get("Name") or ""
            ctx = getattr(getattr(self, "id_data", None), "fn_inputs", None)
            if ctx:
                ctx.store_original(coll, "name")
            try:
                coll.name = name
            except Exception:
                pass
        return {"Collection": coll}


def register():
    bpy.utils.register_class(FNSetCollectionName)


def unregister():
    bpy.utils.unregister_class(FNSetCollectionName)
