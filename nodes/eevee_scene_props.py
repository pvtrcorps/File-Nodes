"""Node for configuring Eevee scene rendering options."""

import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketScene, FNSocketInt
from ..cow_engine import ensure_mutable



class FNEeveeSceneProps(Node, FNBaseNode):
    """Adjust Eevee render samples for a scene."""
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
            ensure_mutable(scene)
            try:
                scene.eevee.taa_render_samples = samples
            except Exception:
                pass
        return {"Scene": scene}


def register():
    bpy.utils.register_class(FNEeveeSceneProps)

def unregister():
    bpy.utils.unregister_class(FNEeveeSceneProps)
