import bpy
from bpy.types import Node
from .base import FNBaseNode
from ..sockets import FNSocketCollection, FNSocketString
from ..operators import get_active_mod_item

class FNNewCollection(Node, FNBaseNode):
    bl_idname = "FNNewCollection"
    bl_label = "New Collection"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        sock = self.inputs.new('FNSocketString', "Name")
        sock.value = "Collection"
        self.outputs.new('FNSocketCollection', "Collection")

    def process(self, context, inputs):
        name = inputs.get("Name") or "Collection"
        coll = bpy.data.collections.new(name)
        mod = get_active_mod_item()
        if mod:
            mod.remember_created_id(coll)
        return {"Collection": coll}


def register():
    bpy.utils.register_class(FNNewCollection)


def unregister():
    bpy.utils.unregister_class(FNNewCollection)
