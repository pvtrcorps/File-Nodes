"""Node that outputs view layers from a scene."""

import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..operators import auto_evaluate_if_enabled
from ..sockets import FNSocketScene, FNSocketViewLayer


class FNSceneViewlayers(Node, FNBaseNode):
    """Provide each view layer of a scene as a separate output socket."""
    bl_idname = "FNSceneViewlayers"
    bl_label = "Scene View Layers"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketScene', "Scene")
        scene = getattr(context, "scene", None)
        self._cached_names = []
        self._update_sockets(scene, context)

    def _update_sockets(self, scene, context=None):
        names = [vl.name for vl in getattr(scene, "view_layers", [])] if scene else []
        if names == getattr(self, "_cached_names", None):
            return
        while self.outputs:
            self.outputs.remove(self.outputs[-1])
        for name in names:
            self.outputs.new('FNSocketViewLayer', name)
        self._cached_names = list(names)
        if context is not None:
            auto_evaluate_if_enabled(context)

    def process(self, context, inputs):
        scene = inputs.get("Scene")
        self._update_sockets(scene, context)
        result = {}
        if scene:
            for vl in scene.view_layers:
                result[vl.name] = vl
        else:
            for sock in self.outputs:
                result[sock.name] = None
        return result


def register():
    bpy.utils.register_class(FNSceneViewlayers)


def unregister():
    bpy.utils.unregister_class(FNSceneViewlayers)
