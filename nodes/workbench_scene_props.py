import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketScene
from ..operators import get_active_mod_item, auto_evaluate_if_enabled


class FNWorkbenchSceneProps(Node, FNBaseNode):
    bl_idname = "FNWorkbenchSceneProps"
    bl_label = "Workbench Scene Properties"

    aa_samples: bpy.props.IntProperty(
        name="AA Samples",
        default=16,
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
        layout.prop(self, "aa_samples", text="AA Samples")

    def process(self, context, inputs):
        scene = inputs.get("Scene")
        if scene and hasattr(scene, "display"):
            mod = get_active_mod_item()
            if mod and hasattr(scene.display, 'render_aa'):
                mod.store_original(scene.display, 'render_aa')
            try:
                if hasattr(scene.display, 'render_aa'):
                    scene.display.render_aa = self.aa_samples
            except Exception:
                pass
        return {"Scene": scene}


def register():
    bpy.utils.register_class(FNWorkbenchSceneProps)

def unregister():
    bpy.utils.unregister_class(FNWorkbenchSceneProps)
