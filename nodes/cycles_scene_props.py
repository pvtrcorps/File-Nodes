import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketScene, FNSocketInt



class FNCyclesSceneProps(Node, FNBaseNode):
    bl_idname = "FNCyclesSceneProps"
    bl_label = "Cycles Scene Properties"


    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketScene', "Scene")
        sock = self.inputs.new('FNSocketInt', "Samples")
        sock.value = 64
        self.outputs.new('FNSocketScene', "Scene")

    def process(self, context, inputs):
        scene = inputs.get("Scene")
        if scene and hasattr(scene, "cycles"):
            samples = inputs.get("Samples")
            ctx = getattr(getattr(self, "id_data", None), "fn_inputs", None)
            if ctx:
                ctx.store_original(scene.cycles, "samples")
            try:
                scene.cycles.samples = samples
            except Exception:
                pass
        return {"Scene": scene}


def register():
    bpy.utils.register_class(FNCyclesSceneProps)

def unregister():
    bpy.utils.unregister_class(FNCyclesSceneProps)
