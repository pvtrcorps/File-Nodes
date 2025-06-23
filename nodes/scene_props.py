import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketScene
from ..operators import get_active_mod_item, auto_evaluate_if_enabled


class FNSceneProps(Node, FNBaseNode):
    bl_idname = "FNSceneProps"
    bl_label = "Scene Properties"

    frame_start: bpy.props.IntProperty(
        name="Start Frame",
        default=1,
        update=auto_evaluate_if_enabled,
    )
    frame_end: bpy.props.IntProperty(
        name="End Frame",
        default=250,
        update=auto_evaluate_if_enabled,
    )

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketScene', "Scene")
        self.outputs.new('FNSocketScene', "Scene")

    def draw_buttons(self, context, layout):
        layout.prop(self, "frame_start", text="Start")
        layout.prop(self, "frame_end", text="End")

    def process(self, context, inputs):
        scene = inputs.get("Scene")
        if scene:
            mod = get_active_mod_item()
            if mod:
                mod.store_original(scene, "frame_start")
                mod.store_original(scene, "frame_end")
            try:
                scene.frame_start = self.frame_start
                scene.frame_end = self.frame_end
            except Exception:
                pass
        return {"Scene": scene}


def register():
    bpy.utils.register_class(FNSceneProps)

def unregister():
    bpy.utils.unregister_class(FNSceneProps)
