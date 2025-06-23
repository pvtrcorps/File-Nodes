import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketScene, FNSocketInt
from ..operators import get_active_mod_item


class FNEeveeSceneProps(Node, FNBaseNode):
    bl_idname = "FNEeveeSceneProps"
    bl_label = "Eevee Scene Properties"


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
        if scene and hasattr(scene, "eevee"):
            samples = inputs.get("Samples")
            mod = get_active_mod_item()
            if mod:
                mod.store_original(scene.eevee, "taa_render_samples")
            try:
                scene.eevee.taa_render_samples = samples
            except Exception:
                pass
        return {"Scene": scene}


def register():
    bpy.utils.register_class(FNEeveeSceneProps)

def unregister():
    bpy.utils.unregister_class(FNEeveeSceneProps)
