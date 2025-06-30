"""Node for creating new materials."""

import bpy
from bpy.types import Node
from .base import FNBaseNode, FNCacheIDMixin
from ..sockets import FNSocketMaterial, FNSocketString


class FNNewMaterial(Node, FNCacheIDMixin, FNBaseNode):
    """Create a new material with the given name."""
    bl_idname = "FNNewMaterial"
    bl_label = "New Material"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        sock = self.inputs.new('FNSocketString', "Name")
        sock.value = "Material"
        self.outputs.new('FNSocketMaterial', "Material")

    def free(self):
        self._invalidate_cache()

    def process(self, context, inputs):
        name = inputs.get("Name") or "Material"
        ctx = getattr(getattr(self, "id_data", None), "fn_inputs", None)
        cached = self.cache_get(name)
        if cached is not None:
            return {"Material": cached}

        if ctx:
            storage = getattr(ctx, "_original_values", {})
            for m in storage.get("created_ids", []):
                if isinstance(m, bpy.types.Material) and m.name == name:
                    cached = m
                    break

        if cached is None:
            existing = bpy.data.materials.get(name)
            if existing is not None:
                cached = existing

        if cached is not None:
            self.cache_store(name, cached)
            if ctx:
                ctx.remember_created_id(cached)
            return {"Material": cached}

        mat = bpy.data.materials.new(name)
        self.cache_store(name, mat)
        if ctx:
            ctx.remember_created_id(mat)
        return {"Material": mat}


def register():
    bpy.utils.register_class(FNNewMaterial)


def unregister():
    bpy.utils.unregister_class(FNNewMaterial)
