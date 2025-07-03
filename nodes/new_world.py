"""Node for creating a new World datablock."""

import bpy
from bpy.types import Node
from .base import FNBaseNode, FNCacheIDMixin
from ..sockets import FNSocketWorld, FNSocketString
from .. import uuid_manager


class FNNewWorld(Node, FNCacheIDMixin, FNBaseNode):
    """Create a new world with the given name."""
    bl_idname = "FNNewWorld"
    bl_label = "New World"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        sock = self.inputs.new('FNSocketString', "Name")
        sock.value = "World"
        self.outputs.new('FNSocketWorld', "World")

    def free(self):
        self._invalidate_cache()

    def process(self, context, inputs, manager):
        name = inputs.get("Name") or "World"
        
        node_tree = self.id_data
        node_key = f"{self.name}"
        
        world = None
        existing_uuid = node_tree.get_datablock_uuid(node_key)
        if existing_uuid:
            world = uuid_manager.find_datablock_by_uuid(existing_uuid, bpy.data.worlds)

        if world is None:
            world = bpy.data.worlds.get(name)
            if world and uuid_manager.get_uuid(world) is None:
                pass
            else:
                world = None

        if world is None:
            world = bpy.data.worlds.new(name)
            world_uuid = uuid_manager.get_or_create_uuid(world)
            node_tree.set_datablock_uuid(node_key, world_uuid)
        else:
            if world.name != name:
                world.name = name
            world_uuid = uuid_manager.get_or_create_uuid(world)
            node_tree.set_datablock_uuid(node_key, world_uuid)

        return {"World": world}


def register():
    bpy.utils.register_class(FNNewWorld)


def unregister():
    bpy.utils.unregister_class(FNNewWorld)