import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketCamera
from ..operators import get_active_mod_item, auto_evaluate_if_enabled


class FNCameraProps(Node, FNBaseNode):
    bl_idname = "FNCameraProps"
    bl_label = "Camera Properties"

    lens: bpy.props.FloatProperty(
        name="Focal Length",
        default=50.0,
        min=1.0,
        update=auto_evaluate_if_enabled,
    )

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketCamera', "Camera")
        self.outputs.new('FNSocketCamera', "Camera")

    def draw_buttons(self, context, layout):
        layout.prop(self, "lens", text="Focal Length")

    def process(self, context, inputs):
        cam = inputs.get("Camera")
        if cam:
            mod = get_active_mod_item()
            if mod:
                mod.store_original(cam, "lens")
            try:
                cam.lens = self.lens
            except Exception:
                pass
        return {"Camera": cam}


def register():
    bpy.utils.register_class(FNCameraProps)

def unregister():
    bpy.utils.unregister_class(FNCameraProps)
