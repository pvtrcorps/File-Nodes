"""Node for creating new scenes."""

import bpy
from bpy.types import Node
from .base import FNBaseNode, FNCacheIDMixin
from ..sockets import FNSocketScene, FNSocketString
from ..cow_engine import DataProxy


class FNNewScene(Node, FNCacheIDMixin, FNBaseNode):
    """Create a new scene with the given name."""
    bl_idname = "FNNewScene"
    bl_label = "New Scene"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        sock = self.inputs.new('FNSocketString', "Name")
        sock.value = "Scene"
        self.outputs.new('FNSocketScene', "Scene")

    def free(self):
        self._invalidate_cache()

    def process(self, context, inputs):
        name = inputs.get("Name") or "Scene"
        cached = self.cache_get(name)
        if cached is not None:
            return {"Scene": DataProxy(cached)}

        existing = bpy.data.scenes.get(name)
        if existing is not None:
            cached = existing

        if cached is not None:
            self.cache_store(name, cached)
            return {"Scene": DataProxy(cached)}

        scene = bpy.data.scenes.new(name)
        scene.use_extra_user = True
        self.cache_store(name, scene)
        return {"Scene": DataProxy(scene)}


def register():
    bpy.utils.register_class(FNNewScene)


def unregister():
    bpy.utils.unregister_class(FNNewScene)
