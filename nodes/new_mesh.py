"""Node for creating new meshes."""

import bpy
from bpy.types import Node
from .base import FNBaseNode, FNCacheIDMixin
from ..sockets import FNSocketMesh, FNSocketString
from .. import uuid_manager


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

    def process(self, context, inputs, manager):
        name = inputs.get("Name") or "Mesh"
        
        node_tree = self.id_data
        node_key = f"{self.name}"
        
        mesh = None
        existing_uuid = node_tree.get_datablock_uuid(node_key)
        if existing_uuid:
            mesh = uuid_manager.find_datablock_by_uuid(existing_uuid, bpy.data.meshes)

        if mesh is None:
            mesh = bpy.data.meshes.get(name)
            if mesh and uuid_manager.get_uuid(mesh) is None:
                pass
            else:
                mesh = None

        if mesh is None:
            mesh = bpy.data.meshes.new(name)
            mesh_uuid = uuid_manager.get_or_create_uuid(mesh)
            node_tree.set_datablock_uuid(node_key, mesh_uuid)
        else:
            if mesh.name != name:
                mesh.name = name
            mesh_uuid = uuid_manager.get_or_create_uuid(mesh)
            node_tree.set_datablock_uuid(node_key, mesh_uuid)

        return {"Mesh": mesh}


def register():
    bpy.utils.register_class(FNNewMesh)


def unregister():
    bpy.utils.unregister_class(FNNewMesh)