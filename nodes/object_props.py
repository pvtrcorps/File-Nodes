import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketObject
from ..operators import get_active_mod_item, auto_evaluate_if_enabled


class FNObjectProps(Node, FNBaseNode):
    bl_idname = "FNObjectProps"
    bl_label = "Object Properties"

    hide_viewport: bpy.props.BoolProperty(
        name="Hide Viewport",
        update=auto_evaluate_if_enabled,
    )
    hide_render: bpy.props.BoolProperty(
        name="Hide Render",
        update=auto_evaluate_if_enabled,
    )

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketObject', "Object")
        self.outputs.new('FNSocketObject', "Object")

    def draw_buttons(self, context, layout):
        layout.prop(self, "hide_viewport", text="Hide Viewport")
        layout.prop(self, "hide_render", text="Hide Render")

    def process(self, context, inputs):
        obj = inputs.get("Object")
        if obj:
            mod = get_active_mod_item()
            if mod:
                mod.store_original(obj, "hide_viewport")
                mod.store_original(obj, "hide_render")
            try:
                obj.hide_viewport = self.hide_viewport
                obj.hide_render = self.hide_render
            except Exception:
                pass
        return {"Object": obj}


def register():
    bpy.utils.register_class(FNObjectProps)

def unregister():
    bpy.utils.unregister_class(FNObjectProps)
