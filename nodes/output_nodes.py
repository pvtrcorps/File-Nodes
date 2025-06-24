import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketSceneList
from ..operators import get_active_mod_item


class FNRenderScenesNode(Node, FNBaseNode):
    bl_idname = "FNRenderScenesNode"
    bl_label = "Render Scenes"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        sock = self.inputs.new('FNSocketSceneList', "Scenes")
        sock.display_shape = 'SQUARE'

    def draw_buttons(self, context, layout):
        layout.operator('file_nodes.render_scenes', text="Render Scenes")

    def process(self, context, inputs):
        # Terminal node, no automatic action
        return {}


class FNOutputScenesNode(Node, FNBaseNode):
    bl_idname = "FNOutputScenesNode"
    bl_label = "Output Scenes"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        sock = self.inputs.new('FNSocketSceneList', "Scenes")
        sock.display_shape = 'SQUARE'

    def process(self, context, inputs):
        scenes = inputs.get("Scenes") or []
        mod = get_active_mod_item()
        if mod:
            mod.scenes_to_keep.extend([s for s in scenes if s])
        return {}


def register():
    bpy.utils.register_class(FNRenderScenesNode)
    bpy.utils.register_class(FNOutputScenesNode)


def unregister():
    bpy.utils.unregister_class(FNOutputScenesNode)
    bpy.utils.unregister_class(FNRenderScenesNode)

