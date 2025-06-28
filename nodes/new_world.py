import bpy
from bpy.types import Node
from .base import FNBaseNode, FNCacheIDMixin
from ..sockets import FNSocketWorld, FNSocketString


class FNNewWorld(Node, FNCacheIDMixin, FNBaseNode):
    bl_idname = "FNNewWorld"
    bl_label = "New World"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        FNBaseNode.init(self, context)
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
        world = bpy.data.worlds.new(name)
        self.cache_store(name, world)
        ctx = getattr(getattr(self, "id_data", None), "fn_inputs", None)
        if ctx:
            ctx.remember_created_id(world)
        return {"World": world}


def register():
    bpy.utils.register_class(FNNewWorld)


def unregister():
    bpy.utils.unregister_class(FNNewWorld)
