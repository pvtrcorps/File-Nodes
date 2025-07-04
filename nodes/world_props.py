"""Node for changing world settings."""

import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketWorld, FNSocketBool



class FNWorldProps(Node, FNBaseNode):
    """Enable or disable nodes for a world."""
    bl_idname = "FNWorldProps"
    bl_label = "World Properties"


    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketWorld', "World")
        sock = self.inputs.new('FNSocketBool', "Use Nodes")
        sock.value = True
        self.outputs.new('FNSocketWorld', "World")

    def process(self, context, inputs, manager):
        world = inputs.get("World")
        if world:
            use_nodes = inputs.get("Use Nodes")
            try:
                world.use_nodes = use_nodes
            except Exception:
                pass
        return {"World": world}


def register():
    bpy.utils.register_class(FNWorldProps)

def unregister():
    bpy.utils.unregister_class(FNWorldProps)