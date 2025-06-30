"""Node for creating new materials."""

import bpy
from bpy.types import Node
from .base import FNBaseNode, FNCacheIDMixin
from ..sockets import FNSocketMaterial, FNSocketString
from ..cow_engine import DataProxy


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
        cached = self.cache_get(name)
        if cached is not None:
            return {"Material": DataProxy(cached)}

        existing = bpy.data.materials.get(name)
        if existing is not None:
            cached = existing

        if cached is not None:
            self.cache_store(name, cached)
            return {"Material": DataProxy(cached)}

        mat = bpy.data.materials.new(name)
        self.cache_store(name, mat)
        return {"Material": DataProxy(mat)}


def register():
    bpy.utils.register_class(FNNewMaterial)


def unregister():
    bpy.utils.unregister_class(FNNewMaterial)
