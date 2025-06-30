"""Node for creating new meshes."""

import bpy
from bpy.types import Node
from .base import FNBaseNode, FNCacheIDMixin
from ..sockets import FNSocketMesh, FNSocketString


class FNNewMesh(Node, FNCacheIDMixin, FNBaseNode):
    """Create a new mesh datablock."""
    bl_idname = "FNNewMesh"
    bl_label = "New Mesh"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        sock = self.inputs.new('FNSocketString', "Name")
        sock.value = "Mesh"
        self.outputs.new('FNSocketMesh', "Mesh")

    def free(self):
        self._invalidate_cache()

    def process(self, context, inputs):
        name = inputs.get("Name") or "Mesh"
        cached = self.cache_get(name)
        if cached is not None:
            return {"Mesh": cached}

        existing = bpy.data.meshes.get(name)
        if existing is not None:
            cached = existing

        if cached is not None:
            self.cache_store(name, cached)
            return {"Mesh": cached}

        mesh = bpy.data.meshes.new(name)
        self.cache_store(name, mesh)
        return {"Mesh": mesh}


def register():
    bpy.utils.register_class(FNNewMesh)


def unregister():
    bpy.utils.unregister_class(FNNewMesh)
