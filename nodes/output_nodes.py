"""Nodes that output or render scenes."""

import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketSceneList, FNSocketExec



class FNRenderScenesNode(Node, FNBaseNode):
    """Operator button to render all provided scenes."""
    bl_idname = "FNRenderScenesNode"
    bl_label = "Render Scenes"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketExec', "Exec")
        sock = self.inputs.new('FNSocketSceneList', "Scenes")
        sock.is_mutable = False
        sock.display_shape = 'SQUARE'

    def draw_buttons(self, context, layout):
        layout.operator('file_nodes.render_scenes', text="Render Scenes")

    def process(self, context, inputs, manager):
        if inputs.get("Exec"):
            scenes = inputs.get("Scenes") or []
            for sc in scenes:
                if not sc:
                    continue
                try:
                    bpy.ops.render.render("INVOKE_DEFAULT", scene=sc.name)
                except Exception:
                    pass
        return {}


class FNOutputScenesNode(Node, FNBaseNode):
    """Collect scenes for use elsewhere in the tree."""
    bl_idname = "FNOutputScenesNode"
    bl_label = "Output Scenes"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        sock = self.inputs.new('FNSocketSceneList', "Scenes")
        sock.is_mutable = False
        sock.display_shape = 'SQUARE'

    def process(self, context, inputs, manager):
        scenes = inputs.get("Scenes") or []
        ctx = getattr(getattr(self, "id_data", None), "fn_inputs", None)
        if ctx:
            if getattr(ctx, "scenes_to_keep", None) is None:
                ctx.scenes_to_keep = []
            ctx.scenes_to_keep.extend([s for s in scenes if s])
        return {}


def register():
    bpy.utils.register_class(FNRenderScenesNode)
    bpy.utils.register_class(FNOutputScenesNode)


def unregister():
    bpy.utils.unregister_class(FNOutputScenesNode)
    bpy.utils.unregister_class(FNRenderScenesNode)

