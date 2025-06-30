"""Node for creating a new World datablock."""

import bpy
from bpy.types import Node
from .base import FNBaseNode, FNCacheIDMixin
from ..sockets import FNSocketWorld, FNSocketString


class FNNewWorld(Node, FNCacheIDMixin, FNBaseNode):
    """Create a new world with the given name."""
    bl_idname = "FNNewWorld"
    bl_label = "New World"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        sock = self.inputs.new('FNSocketString', "Name")
        sock.value = "World"
        self.outputs.new('FNSocketWorld', "World")

    def free(self):
        self._invalidate_cache()

    def process(self, context, inputs):
        name = inputs.get("Name") or "World"
        cached = self.cache_get(name)
        if cached is not None:
            return {"World": cached}

        ctx = getattr(getattr(self, "id_data", None), "fn_inputs", None)
        if ctx:
            storage = getattr(ctx, "_original_values", {})
            for w in storage.get("created_ids", []):
                if isinstance(w, bpy.types.World) and w.name == name:
                    cached = w
                    break

        if cached is None:
            existing = bpy.data.worlds.get(name)
            if existing is not None:
                cached = existing

        if cached is not None:
            self.cache_store(name, cached)
            if ctx:
                ctx.remember_created_id(cached)
            return {"World": cached}

        world = bpy.data.worlds.new(name)
        self.cache_store(name, world)
        if ctx:
            ctx.remember_created_id(world)
        return {"World": world}


def register():
    bpy.utils.register_class(FNNewWorld)


def unregister():
    bpy.utils.unregister_class(FNNewWorld)
