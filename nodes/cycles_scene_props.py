import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketScene
from ..operators import get_active_mod_item, auto_evaluate_if_enabled


class FNCyclesSceneProps(Node, FNBaseNode):
    bl_idname = "FNCyclesSceneProps"
    bl_label = "Cycles Scene Properties"

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
        if scene and hasattr(scene, "cycles"):
            mod = get_active_mod_item()
            if mod:
                mod.store_original(scene.cycles, "samples")
            try:
                scene.cycles.samples = self.samples
            except Exception:
                pass
        return {"Scene": scene}


def register():
    bpy.utils.register_class(FNCyclesSceneProps)

def unregister():
    bpy.utils.unregister_class(FNCyclesSceneProps)
