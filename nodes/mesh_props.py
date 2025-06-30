"""Node for changing mesh properties."""

import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketMesh, FNSocketBool
from ..cow_engine import ensure_mutable



class FNMeshProps(Node, FNBaseNode):
    """Toggle auto-smoothing on a mesh."""
    bl_idname = "FNMeshProps"
    bl_label = "Mesh Properties"


    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketMesh', "Mesh")
        sock = self.inputs.new('FNSocketBool', "Auto Smooth")
        sock.value = False
        self.outputs.new('FNSocketMesh', "Mesh")

    def process(self, context, inputs):
        mesh = inputs.get("Mesh")
        if mesh:
            auto = inputs.get("Auto Smooth")
            ensure_mutable(mesh)
            try:
                mesh.use_auto_smooth = auto
            except Exception:
                pass
        return {"Mesh": mesh}


def register():
    bpy.utils.register_class(FNMeshProps)

def unregister():
    bpy.utils.unregister_class(FNMeshProps)
