import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketScene, FNSocketInt



class FNWorkbenchSceneProps(Node, FNBaseNode):
    bl_idname = "FNWorkbenchSceneProps"
    bl_label = "Workbench Scene Properties"


    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketScene', "Scene")
        sock = self.inputs.new('FNSocketInt', "AA Samples")
        sock.value = 16
        self.outputs.new('FNSocketScene', "Scene")

    def process(self, context, inputs):
        scene = inputs.get("Scene")
        if scene and hasattr(scene, "display"):
            samples = inputs.get("AA Samples")
            ctx = getattr(getattr(self, "id_data", None), "fn_inputs", None)
            if ctx and hasattr(scene.display, 'render_aa'):
                ctx.store_original(scene.display, 'render_aa')
            try:
                if hasattr(scene.display, 'render_aa'):
                    scene.display.render_aa = samples
            except Exception:
                pass
        return {"Scene": scene}


def register():
    bpy.utils.register_class(FNWorkbenchSceneProps)

def unregister():
    bpy.utils.unregister_class(FNWorkbenchSceneProps)
