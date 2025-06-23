import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketScene
from ..operators import get_active_mod_item, auto_evaluate_if_enabled


class FNOutputProps(Node, FNBaseNode):
    bl_idname = "FNOutputProps"
    bl_label = "Output Properties"

    resolution_x: bpy.props.IntProperty(
        name="Resolution X",
        default=1920,
        min=1,
        update=auto_evaluate_if_enabled,
    )
    resolution_y: bpy.props.IntProperty(
        name="Resolution Y",
        default=1080,
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
        layout.prop(self, "resolution_x", text="Res X")
        layout.prop(self, "resolution_y", text="Res Y")

    def process(self, context, inputs):
        scene = inputs.get("Scene")
        if scene:
            mod = get_active_mod_item()
            if mod:
                mod.store_original(scene.render, "resolution_x")
                mod.store_original(scene.render, "resolution_y")
            try:
                scene.render.resolution_x = self.resolution_x
                scene.render.resolution_y = self.resolution_y
            except Exception:
                pass
        return {"Scene": scene}


def register():
    bpy.utils.register_class(FNOutputProps)

def unregister():
    bpy.utils.unregister_class(FNOutputProps)
