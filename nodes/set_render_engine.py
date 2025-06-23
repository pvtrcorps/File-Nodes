import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketScene
from ..operators import get_active_mod_item, auto_evaluate_if_enabled


class FNSetRenderEngine(Node, FNBaseNode):
    bl_idname = "FNSetRenderEngine"
    bl_label = "Set Render Engine"

    engine: bpy.props.EnumProperty(
        name="Engine",
        items=[
            ("BLENDER_EEVEE", "Eevee", ""),
            ("CYCLES", "Cycles", ""),
            ("BLENDER_WORKBENCH", "Workbench", ""),
        ],
        default="BLENDER_EEVEE",
        update=auto_evaluate_if_enabled,
    )

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketScene', "Scene")
        self.outputs.new('FNSocketScene', "Scene")

    def draw_buttons(self, context, layout):
        layout.prop(self, "engine", text="Engine")

    def process(self, context, inputs):
        scene = inputs.get("Scene")
        if scene:
            mod = get_active_mod_item()
            if mod:
                mod.store_original(scene.render, "engine")
            try:
                scene.render.engine = self.engine
            except Exception:
                pass
        return {"Scene": scene}


def register():
    bpy.utils.register_class(FNSetRenderEngine)

def unregister():
    bpy.utils.unregister_class(FNSetRenderEngine)
