"""Node for creating new cameras."""

import bpy
from bpy.types import Node
from .base import FNBaseNode, FNCacheIDMixin
from ..sockets import FNSocketCamera, FNSocketString


class FNNewCamera(Node, FNCacheIDMixin, FNBaseNode):
    """Create a new camera datablock."""
    bl_idname = "FNNewCamera"
    bl_label = "New Camera"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        sock = self.inputs.new('FNSocketString', "Name")
        sock.value = "Camera"
        self.outputs.new('FNSocketCamera', "Camera")

    def free(self):
        self._invalidate_cache()

    def process(self, context, inputs, manager):
        name = inputs.get("Name") or "Camera"
        cached = self.cache_get(name)
        if cached is not None:
            return {"Camera": cached}

        existing = bpy.data.cameras.get(name)
        if existing is not None:
            cached = existing

        if cached is not None:
            self.cache_store(name, cached)
            return {"Camera": cached}

        cam = bpy.data.cameras.new(name)
        self.cache_store(name, cam)
        return {"Camera": cam}


def register():
    bpy.utils.register_class(FNNewCamera)


def unregister():
    bpy.utils.unregister_class(FNNewCamera)