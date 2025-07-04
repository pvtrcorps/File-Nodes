"""Node for editing collection properties."""

import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketCollection, FNSocketBool



class FNCollectionProps(Node, FNBaseNode):
    """Set collection options such as visibility."""
    bl_idname = "FNCollectionProps"
    bl_label = "Collection Properties"


    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketCollection', "Collection")
        sock = self.inputs.new('FNSocketBool', "Hide Viewport")
        sock.value = False
        self.outputs.new('FNSocketCollection', "Collection")

    def process(self, context, inputs, manager):
        coll = inputs.get("Collection")
        if coll:
            hide_vp = inputs.get("Hide Viewport")
            try:
                coll.hide_viewport = hide_vp
            except Exception:
                pass
        return {"Collection": coll}


def register():
    bpy.utils.register_class(FNCollectionProps)

def unregister():
    bpy.utils.unregister_class(FNCollectionProps)