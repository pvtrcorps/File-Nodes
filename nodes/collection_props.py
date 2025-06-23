import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketCollection
from ..operators import get_active_mod_item, auto_evaluate_if_enabled


class FNCollectionProps(Node, FNBaseNode):
    bl_idname = "FNCollectionProps"
    bl_label = "Collection Properties"

    hide_viewport: bpy.props.BoolProperty(
        name="Hide Viewport",
        update=auto_evaluate_if_enabled,
    )

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketCollection', "Collection")
        self.outputs.new('FNSocketCollection', "Collection")

    def draw_buttons(self, context, layout):
        layout.prop(self, "hide_viewport", text="Hide Viewport")

    def process(self, context, inputs):
        coll = inputs.get("Collection")
        if coll:
            mod = get_active_mod_item()
            if mod:
                mod.store_original(coll, "hide_viewport")
            try:
                coll.hide_viewport = self.hide_viewport
            except Exception:
                pass
        return {"Collection": coll}


def register():
    bpy.utils.register_class(FNCollectionProps)

def unregister():
    bpy.utils.unregister_class(FNCollectionProps)
