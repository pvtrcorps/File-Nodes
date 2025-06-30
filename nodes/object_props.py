"""Node for adjusting object visibility settings."""

import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketObject, FNSocketBool
from ..cow_engine import ensure_mutable



class FNObjectProps(Node, FNBaseNode):
    """Set visibility flags on an object."""
    bl_idname = "FNObjectProps"
    bl_label = "Object Properties"


    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketObject', "Object")
        sock = self.inputs.new('FNSocketBool', "Hide Viewport")
        sock.value = False
        sock = self.inputs.new('FNSocketBool', "Hide Render")
        sock.value = False
        self.outputs.new('FNSocketObject', "Object")

    def process(self, context, inputs):
        obj = inputs.get("Object")
        if obj:
            hide_vp = inputs.get("Hide Viewport")
            hide_re = inputs.get("Hide Render")
            obj = ensure_mutable(obj)
            try:
                obj.hide_viewport = hide_vp
                obj.hide_render = hide_re
            except Exception:
                pass
        return {"Object": obj}


def register():
    bpy.utils.register_class(FNObjectProps)

def unregister():
    bpy.utils.unregister_class(FNObjectProps)
