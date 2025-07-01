"""Node for creating new view layers."""

import bpy
from bpy.types import Node
from .base import FNBaseNode, FNCacheIDMixin
from ..sockets import FNSocketScene, FNSocketString, FNSocketViewLayer


class FNNewViewLayer(Node, FNCacheIDMixin, FNBaseNode):
    """Create a new view layer in the given scene."""
    bl_idname = "FNNewViewLayer"
    bl_label = "New ViewLayer"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketScene', "Scene")
        sock = self.inputs.new('FNSocketString', "Name")
        sock.value = "ViewLayer"
        self.outputs.new('FNSocketViewLayer', "ViewLayer")

    def free(self):
        self._invalidate_cache()

    def process(self, context, inputs, manager):
        scene = inputs.get("Scene")
        if not scene:
            return {"ViewLayer": None}
        name = inputs.get("Name") or "ViewLayer"
        key = (scene.as_pointer(), name)
        cached = self.cache_get(key)
        if cached is not None:
            return {"ViewLayer": cached}

        existing = scene.view_layers.get(name)
        if existing is not None:
            cached = existing

        if cached is not None:
            self.cache_store(key, cached)
            return {"ViewLayer": cached}

        view_layer = scene.view_layers.new(name)
        self.cache_store(key, view_layer)
        return {"ViewLayer": view_layer}


def register():
    bpy.utils.register_class(FNNewViewLayer)


def unregister():
    bpy.utils.unregister_class(FNNewViewLayer)