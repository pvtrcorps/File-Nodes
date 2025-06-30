"""Node for creating new collections."""

import bpy
from bpy.types import Node
from .base import FNBaseNode, FNCacheIDMixin
from ..sockets import FNSocketCollection, FNSocketString


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
        ctx = getattr(getattr(self, "id_data", None), "fn_inputs", None)
        cached = self.cache_get(name)
        if cached is not None:
            return {"Collection": cached}

        if ctx:
            storage = getattr(ctx, "_original_values", {})
            for c in storage.get("created_ids", []):
                if isinstance(c, bpy.types.Collection) and c.name == name:
                    cached = c
                    break

        if cached is None:
            existing = bpy.data.collections.get(name)
            if existing is not None:
                cached = existing

        if cached is not None:
            self.cache_store(name, cached)
            if ctx:
                ctx.remember_created_id(cached)
            return {"Collection": cached}

        coll = bpy.data.collections.new(name)
        self.cache_store(name, coll)
        if ctx:
            ctx.remember_created_id(coll)
        return {"Collection": coll}


def register():
    bpy.utils.register_class(FNNewCollection)


def unregister():
    bpy.utils.unregister_class(FNNewCollection)
