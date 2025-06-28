import bpy
from bpy.types import Node
from .base import FNBaseNode, FNCacheIDMixin
from ..sockets import FNSocketCollection, FNSocketString


class FNNewCollection(Node, FNCacheIDMixin, FNBaseNode):
    bl_idname = "FNNewCollection"
    bl_label = "New Collection"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        FNBaseNode.init(self, context)
        sock = self.inputs.new('FNSocketString', "Name")
        sock.value = "Collection"
        self.outputs.new('FNSocketCollection', "Collection")

    def free(self):
        self._invalidate_cache()

    def process(self, context, inputs):
        name = inputs.get("Name") or "Collection"
        cached = self.cache_get(name)
        if cached is not None:
            return {"Collection": cached}
        coll = bpy.data.collections.new(name)
        self.cache_store(name, coll)
        ctx = getattr(getattr(self, "id_data", None), "fn_inputs", None)
        if ctx:
            ctx.remember_created_id(coll)
        return {"Collection": coll}


def register():
    bpy.utils.register_class(FNNewCollection)


def unregister():
    bpy.utils.unregister_class(FNNewCollection)
