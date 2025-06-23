import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketObject
from ..operators import get_active_mod_item, auto_evaluate_if_enabled


class FNEeveeObjectProps(Node, FNBaseNode):
    bl_idname = "FNEeveeObjectProps"
    bl_label = "Eevee Object Properties"

    visible_shadow: bpy.props.BoolProperty(
        name="Visible Shadow",
        update=auto_evaluate_if_enabled,
    )

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketObject', "Object")
        self.outputs.new('FNSocketObject', "Object")

    def draw_buttons(self, context, layout):
        layout.prop(self, "visible_shadow", text="Visible Shadow")

    def process(self, context, inputs):
        obj = inputs.get("Object")
        if obj:
            mod = get_active_mod_item()
            if mod:
                mod.store_original(obj, "visible_shadow")
            try:
                obj.visible_shadow = self.visible_shadow
            except Exception:
                pass
        return {"Object": obj}


def register():
    bpy.utils.register_class(FNEeveeObjectProps)

def unregister():
    bpy.utils.unregister_class(FNEeveeObjectProps)
