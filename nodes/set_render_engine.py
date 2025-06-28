import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketScene, FNSocketString



class FNSetRenderEngine(Node, FNBaseNode):
    bl_idname = "FNSetRenderEngine"
    bl_label = "Set Render Engine"
    color_tag = 'OUTPUT'


    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketScene', "Scene")
        sock = self.inputs.new('FNSocketString', "Engine")
        sock.value = "BLENDER_EEVEE"
        self.outputs.new('FNSocketScene', "Scene")

    def process(self, context, inputs):
        scene = inputs.get("Scene")
        if scene:
            engine = inputs.get("Engine")
            ctx = getattr(getattr(self, "id_data", None), "fn_inputs", None)
            if ctx:
                ctx.store_original(scene.render, "engine")
            try:
                scene.render.engine = engine
            except Exception:
                pass
        return {"Scene": scene}


def register():
    bpy.utils.register_class(FNSetRenderEngine)

def unregister():
    bpy.utils.unregister_class(FNSetRenderEngine)
