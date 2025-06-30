"""Node for creating new collections."""

import bpy
from bpy.types import Node
from .base import FNBaseNode, FNCacheIDMixin
from ..sockets import FNSocketCollection, FNSocketString
from ..cow_engine import DataProxy


class FNNewCollection(Node, FNCacheIDMixin, FNBaseNode):
    """Create a new collection with the specified name."""
    bl_idname = "FNNewCollection"
    bl_label = "New Collection"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        sock = self.inputs.new('FNSocketString', "Name")
        sock.value = "Collection"
        self.outputs.new('FNSocketCollection', "Collection")

    def free(self):
        self._invalidate_cache()

    def process(self, context, inputs):
        name = inputs.get("Name") or "Collection"
        cached = self.cache_get(name)
        if cached is not None:
            return {"Collection": DataProxy(cached)}

        existing = bpy.data.collections.get(name)
        if existing is not None:
            cached = existing

        if cached is not None:
            self.cache_store(name, cached)
            return {"Collection": DataProxy(cached)}

        coll = bpy.data.collections.new(name)
        self.cache_store(name, coll)
        return {"Collection": DataProxy(coll)}


def register():
    bpy.utils.register_class(FNNewCollection)


def unregister():
    bpy.utils.unregister_class(FNNewCollection)
