import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketScene, FNSocketInt
from ..operators import get_active_mod_item


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
            mod = get_active_mod_item()
            if mod and hasattr(scene.display, 'render_aa'):
                mod.store_original(scene.display, 'render_aa')
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
