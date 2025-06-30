"""Node for setting scene frame range."""

import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketScene, FNSocketInt
from ..cow_engine import ensure_mutable



class FNSceneProps(Node, FNBaseNode):
    """Adjust the frame start and end of a scene."""
    bl_idname = "FNSceneProps"
    bl_label = "Scene Properties"


    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketScene', "Scene")
        sock = self.inputs.new('FNSocketInt', "Start")
        sock.value = 1
        sock = self.inputs.new('FNSocketInt', "End")
        sock.value = 250
        self.outputs.new('FNSocketScene', "Scene")

    def process(self, context, inputs):
        scene = inputs.get("Scene")
        if scene:
            start = inputs.get("Start")
            end = inputs.get("End")
            scene = ensure_mutable(scene)
            try:
                scene.frame_start = start
                scene.frame_end = end
            except Exception:
                pass
        return {"Scene": scene}


def register():
    bpy.utils.register_class(FNSceneProps)

def unregister():
    bpy.utils.unregister_class(FNSceneProps)
