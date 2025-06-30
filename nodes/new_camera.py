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

    def process(self, context, inputs):
        name = inputs.get("Name") or "Camera"
        cached = self.cache_get(name)
        ctx = getattr(getattr(self, "id_data", None), "fn_inputs", None)
        if cached is not None:
            return {"Camera": cached}

        if ctx:
            storage = getattr(ctx, "_original_values", {})
            for cam in storage.get("created_ids", []):
                if isinstance(cam, bpy.types.Camera) and cam.name == name:
                    cached = cam
                    break

        if cached is None:
            existing = bpy.data.cameras.get(name)
            if existing is not None:
                cached = existing

        if cached is not None:
            self.cache_store(name, cached)
            if ctx:
                ctx.remember_created_id(cached)
            return {"Camera": cached}

        cam = bpy.data.cameras.new(name)
        self.cache_store(name, cam)
        if ctx:
            ctx.remember_created_id(cam)
        return {"Camera": cam}


def register():
    bpy.utils.register_class(FNNewCamera)


def unregister():
    bpy.utils.unregister_class(FNNewCamera)
