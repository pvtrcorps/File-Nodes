"""Node for creating new collections."""

import bpy
from bpy.types import Node
from .base import FNBaseNode, FNCacheIDMixin
from ..sockets import FNSocketCollection, FNSocketString
from .. import uuid_manager


class FNNewCollection(Node, FNCacheIDMixin, FNBaseNode):
    """Create a new collection with the specified name."""
    bl_idname = "FNNewCollection"
    bl_label = "New Collection"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        sock = self.inputs.new('FNSocketString', "Name")
        sock.value = "Collection"
        self.outputs.new('FNSocketCollection', "Collection")

    def free(self):
        self._invalidate_cache()

    def process(self, context, inputs, manager):
        name = inputs.get("Name") or "Collection"
        
        node_tree = self.id_data
        node_key = f"{self.name}"
        
        coll = None
        existing_uuid = node_tree.get_datablock_uuid(node_key)
        if existing_uuid:
            coll = uuid_manager.find_datablock_by_uuid(existing_uuid, bpy.data.collections)

        if coll is None:
            coll = bpy.data.collections.get(name)
            if coll and uuid_manager.get_uuid(coll) is None:
                pass
            else:
                coll = None

        if coll is None:
            coll = bpy.data.collections.new(name)
            coll_uuid = uuid_manager.get_or_create_uuid(coll)
            node_tree.set_datablock_uuid(node_key, coll_uuid)
        else:
            if coll.name != name:
                coll.name = name
            coll_uuid = uuid_manager.get_or_create_uuid(coll)
            node_tree.set_datablock_uuid(node_key, coll_uuid)

        return {"Collection": coll}


def register():
    bpy.utils.register_class(FNNewCollection)


def unregister():
    bpy.utils.unregister_class(FNNewCollection)