import bpy
from bpy.types import Node
from .base import FNBaseNode, FNCacheIDMixin
from ..sockets import FNSocketScene, FNSocketString
from ..operators import get_active_mod_item

class FNNewScene(Node, FNCacheIDMixin, FNBaseNode):
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
            return {"Scene": cached}
        scene = bpy.data.scenes.new(name)
        self.cache_store(name, scene)
        mod = get_active_mod_item()
        if mod:
            mod.remember_created_scene(scene)
            mod.remember_created_id(scene)
        return {"Scene": scene}


def register():
    bpy.utils.register_class(FNNewScene)


def unregister():
    bpy.utils.unregister_class(FNNewScene)
