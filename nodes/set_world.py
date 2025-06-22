
import bpy
from bpy.types import Node
from .base import FNBaseNode
from ..sockets import FNSocketScene, FNSocketWorld

class FNSetWorld(Node, FNBaseNode):
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"
    bl_idname = "FNSetWorldNode"
    bl_label = "Set World to Scene"

    def init(self, context):
        self.inputs.new('FNSocketScene', "Scene")
        self.inputs.new('FNSocketWorld', "World")

    def process(self, context, inputs):
        scene = inputs.get("Scene")
        world = inputs.get("World")
        if scene and world:
            scene.world = world
        return {}

def register():
    bpy.utils.register_class(FNSetWorld)
def unregister():
    bpy.utils.unregister_class(FNSetWorld)