"""Node for modifying material settings."""

import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketMaterial, FNSocketBool
from ..cow_engine import ensure_mutable



class FNMaterialProps(Node, FNBaseNode):
    """Toggle the use of nodes for a material."""
    bl_idname = "FNMaterialProps"
    bl_label = "Material Properties"


    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketMaterial', "Material")
        sock = self.inputs.new('FNSocketBool', "Use Nodes")
        sock.value = True
        self.outputs.new('FNSocketMaterial', "Material")

    def process(self, context, inputs):
        mat = inputs.get("Material")
        if mat:
            use_nodes = inputs.get("Use Nodes")
            mat = ensure_mutable(mat)
            try:
                mat.use_nodes = use_nodes
            except Exception:
                pass
        return {"Material": mat}


def register():
    bpy.utils.register_class(FNMaterialProps)

def unregister():
    bpy.utils.unregister_class(FNMaterialProps)
