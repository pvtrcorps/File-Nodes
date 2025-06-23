import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketLight
from ..operators import get_active_mod_item, auto_evaluate_if_enabled


class FNLightProps(Node, FNBaseNode):
    bl_idname = "FNLightProps"
    bl_label = "Light Properties"

    energy: bpy.props.FloatProperty(
        name="Energy",
        default=10.0,
        min=0.0,
        update=auto_evaluate_if_enabled,
    )

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketLight', "Light")
        self.outputs.new('FNSocketLight', "Light")

    def draw_buttons(self, context, layout):
        layout.prop(self, "energy", text="Energy")

    def process(self, context, inputs):
        light = inputs.get("Light")
        if light:
            mod = get_active_mod_item()
            if mod:
                mod.store_original(light, "energy")
            try:
                light.energy = self.energy
            except Exception:
                pass
        return {"Light": light}


def register():
    bpy.utils.register_class(FNLightProps)

def unregister():
    bpy.utils.unregister_class(FNLightProps)
