"""Node for editing camera properties."""

import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketCamera, FNSocketFloat



class FNCameraProps(Node, FNBaseNode):
    """Set camera properties such as focal length."""
    bl_idname = "FNCameraProps"
    bl_label = "Camera Properties"


    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketCamera', "Camera")
        sock = self.inputs.new('FNSocketFloat', "Focal Length")
        sock.value = 50.0
        self.outputs.new('FNSocketCamera', "Camera")

    def process(self, context, inputs, manager):
        cam = inputs.get("Camera")
        if cam:
            lens = inputs.get("Focal Length")
            try:
                cam.lens = lens
            except Exception:
                pass
        return {"Camera": cam}


def register():
    bpy.utils.register_class(FNCameraProps)

def unregister():
    bpy.utils.unregister_class(FNCameraProps)