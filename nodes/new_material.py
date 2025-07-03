"""Node for creating new materials."""

import bpy
from bpy.types import Node
from .base import FNBaseNode, FNCacheIDMixin
from ..sockets import FNSocketMaterial, FNSocketString
from .. import uuid_manager


class FNNewMaterial(Node, FNCacheIDMixin, FNBaseNode):
    """Create a new material with the given name."""
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

    def process(self, context, inputs, manager):
        name = inputs.get("Name") or "Material"
        
        node_tree = self.id_data
        node_key = f"{self.name}"
        
        mat = None
        existing_uuid = node_tree.get_datablock_uuid(node_key)
        if existing_uuid:
            mat = uuid_manager.find_datablock_by_uuid(existing_uuid, bpy.data.materials)

        if mat is None:
            mat = bpy.data.materials.get(name)
            if mat and uuid_manager.get_uuid(mat) is None:
                pass
            else:
                mat = None

        if mat is None:
            mat = bpy.data.materials.new(name)
            mat_uuid = uuid_manager.get_or_create_uuid(mat)
            node_tree.set_datablock_uuid(node_key, mat_uuid)
        else:
            if mat.name != name:
                mat.name = name
            mat_uuid = uuid_manager.get_or_create_uuid(mat)
            node_tree.set_datablock_uuid(node_key, mat_uuid)

        return {"Material": mat}


def register():
    bpy.utils.register_class(FNNewMaterial)


def unregister():
    bpy.utils.unregister_class(FNNewMaterial)