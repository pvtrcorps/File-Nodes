import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketScene
from ..operators import get_active_mod_item, auto_evaluate_if_enabled


class FNEeveeSceneProps(Node, FNBaseNode):
    bl_idname = "FNEeveeSceneProps"
    bl_label = "Eevee Scene Properties"

    samples: bpy.props.IntProperty(
        name="Samples",
        default=64,
        min=1,
        update=auto_evaluate_if_enabled,
    )

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketScene', "Scene")
        self.outputs.new('FNSocketScene', "Scene")

    def draw_buttons(self, context, layout):
        layout.prop(self, "samples", text="Samples")

    def process(self, context, inputs):
        scene = inputs.get("Scene")
        if scene and hasattr(scene, "eevee"):
            mod = get_active_mod_item()
            if mod:
                mod.store_original(scene.eevee, "taa_render_samples")
            try:
                scene.eevee.taa_render_samples = self.samples
            except Exception:
                pass
        return {"Scene": scene}


def register():
    bpy.utils.register_class(FNEeveeSceneProps)

def unregister():
    bpy.utils.unregister_class(FNEeveeSceneProps)
