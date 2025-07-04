"""Node for modifying light properties."""

import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketLight, FNSocketFloat



class FNLightProps(Node, FNBaseNode):
    """Adjust light settings such as energy."""
    bl_idname = "FNLightProps"
    bl_label = "Light Properties"


    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketLight', "Light")
        sock = self.inputs.new('FNSocketFloat', "Energy")
        sock.value = 10.0
        self.outputs.new('FNSocketLight', "Light")

    def process(self, context, inputs, manager):
        light = inputs.get("Light")
        if light:
            energy = inputs.get("Energy")
            try:
                light.energy = energy
            except Exception:
                pass
        return {"Light": light}


def register():
    bpy.utils.register_class(FNLightProps)

def unregister():
    bpy.utils.unregister_class(FNLightProps)