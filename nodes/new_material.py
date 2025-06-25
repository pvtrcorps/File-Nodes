import bpy
from bpy.types import Node
from .base import FNBaseNode, FNCacheIDMixin
from ..sockets import FNSocketMaterial, FNSocketString
from ..operators import get_active_mod_item

class FNNewMaterial(Node, FNCacheIDMixin, FNBaseNode):
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
            return {"Material": cached}
        mat = bpy.data.materials.new(name)
        self.cache_store(name, mat)
        mod = get_active_mod_item()
        if mod:
            mod.remember_created_id(mat)
        return {"Material": mat}


def register():
    bpy.utils.register_class(FNNewMaterial)


def unregister():
    bpy.utils.unregister_class(FNNewMaterial)
