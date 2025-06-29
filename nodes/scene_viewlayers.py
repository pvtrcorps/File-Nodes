"""Node that outputs viewlayers from a scene."""

import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketScene, FNSocketViewLayerList


class FNSceneViewlayers(Node, FNBaseNode):
    """Output all viewlayers from a scene as a list."""
    bl_idname = "FNSceneViewlayers"
    bl_label = "Scene Viewlayers"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketScene', "Scene")
        out = self.outputs.new('FNSocketViewLayerList', "Viewlayers")
        out.display_shape = 'SQUARE'

    def update(self):
        pass

    def process(self, context, inputs):
        scene = inputs.get("Scene")
        if scene:
            return {"Viewlayers": list(scene.view_layers)}
        return {"Viewlayers": []}


def register():
    bpy.utils.register_class(FNSceneViewlayers)


def unregister():
    bpy.utils.unregister_class(FNSceneViewlayers)
