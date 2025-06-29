"""Node for creating new scenes."""

import bpy
from bpy.types import Node
from .base import FNBaseNode, FNCacheIDMixin
from ..sockets import FNSocketScene, FNSocketString


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
        ctx = getattr(getattr(self, "id_data", None), "fn_inputs", None)
        if cached is None and ctx:
            storage = getattr(ctx, "_original_values", {})
            for sc in storage.get("created_ids", []):
                if isinstance(sc, bpy.types.Scene) and sc.name == name:
                    cached = sc
                    break
        if cached is not None:
            return {"Scene": cached}
        scene = bpy.data.scenes.new(name)
        self.cache_store(name, scene)
        if ctx:
            ctx.remember_created_scene(scene)
            ctx.remember_created_id(scene)
        return {"Scene": scene}


def register():
    bpy.utils.register_class(FNNewScene)


def unregister():
    bpy.utils.unregister_class(FNNewScene)
