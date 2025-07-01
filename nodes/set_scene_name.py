"""Node to rename a scene."""

import bpy
from bpy.types import Node
from .base import FNBaseNode
from ..sockets import FNSocketScene, FNSocketString



class FNSetSceneName(Node, FNBaseNode):
    """Rename the provided scene."""
    bl_idname = "FNSetSceneName"
    bl_label = "Set Scene Name"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketScene', "Scene")
        sock = self.inputs.new('FNSocketString', "Name")
        sock.value = ""
        self.outputs.new('FNSocketScene', "Scene")

    def process(self, context, inputs, manager):
        scene = inputs.get("Scene")
        if scene:
            name = inputs.get("Name") or ""
            try:
                scene.name = name
            except Exception:
                pass
        return {"Scene": scene}


def register():
    bpy.utils.register_class(FNSetSceneName)


def unregister():
    bpy.utils.unregister_class(FNSetSceneName)