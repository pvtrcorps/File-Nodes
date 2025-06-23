import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketObject
from ..operators import get_active_mod_item, auto_evaluate_if_enabled


class FNCyclesObjectProps(Node, FNBaseNode):
    bl_idname = "FNCyclesObjectProps"
    bl_label = "Cycles Object Properties"

    is_holdout: bpy.props.BoolProperty(
        name="Holdout",
        update=auto_evaluate_if_enabled,
    )

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketObject', "Object")
        self.outputs.new('FNSocketObject', "Object")

    def draw_buttons(self, context, layout):
        layout.prop(self, "is_holdout", text="Holdout")

    def process(self, context, inputs):
        obj = inputs.get("Object")
        if obj:
            mod = get_active_mod_item()
            if mod:
                mod.store_original(obj, "is_holdout")
            try:
                obj.is_holdout = self.is_holdout
            except Exception:
                pass
        return {"Object": obj}


def register():
    bpy.utils.register_class(FNCyclesObjectProps)

def unregister():
    bpy.utils.unregister_class(FNCyclesObjectProps)
