import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketScene, FNSocketInt



class FNSceneProps(Node, FNBaseNode):
    bl_idname = "FNSceneProps"
    bl_label = "Scene Properties"
    color_tag = 'OUTPUT'


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
            ctx = getattr(getattr(self, "id_data", None), "fn_inputs", None)
            if ctx:
                ctx.store_original(scene, "frame_start")
                ctx.store_original(scene, "frame_end")
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
