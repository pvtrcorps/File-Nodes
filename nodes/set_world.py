"""Node that assigns a world to a scene."""

import bpy
from bpy.types import Node
from .base import FNBaseNode
from ..sockets import FNSocketScene, FNSocketWorld
from ..cow_engine import ensure_mutable


class FNSetWorld(Node, FNBaseNode):
    """Assign the provided world to the scene."""
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"
    bl_idname = "FNSetWorldNode"
    bl_label = "Set World to Scene"

    def init(self, context):
        self.inputs.new('FNSocketScene', "Scene")
        self.inputs.new('FNSocketWorld', "World")
        self.outputs.new('FNSocketScene', "Scene")

    def process(self, context, inputs):
        scene = inputs.get("Scene")
        world = inputs.get("World")
        if scene and world:
            ensure_mutable(scene)
            scene.world = world
        return {"Scene": scene}

def register():
    bpy.utils.register_class(FNSetWorld)
def unregister():
    bpy.utils.unregister_class(FNSetWorld)
