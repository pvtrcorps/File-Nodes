
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
        self.outputs.new('FNSocketScene', "Scene")

    def process(self, context, inputs):
        scene = inputs.get("Scene")
        world = inputs.get("World")
        if scene and world:
            ctx = getattr(getattr(self, "id_data", None), "fn_inputs", None)
            if ctx:
                ctx.store_original(scene, "world")
            scene.world = world
        return {"Scene": scene}

def register():
    bpy.utils.register_class(FNSetWorld)
def unregister():
    bpy.utils.unregister_class(FNSetWorld)
