import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketScene, FNSocketInt



class FNOutputProps(Node, FNBaseNode):
    bl_idname = "FNOutputProps"
    bl_label = "Output Properties"


    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        FNBaseNode.init(self, context)
        self.inputs.new('FNSocketScene', "Scene")
        sock = self.inputs.new('FNSocketInt', "Resolution X")
        sock.value = 1920
        sock = self.inputs.new('FNSocketInt', "Resolution Y")
        sock.value = 1080
        self.outputs.new('FNSocketScene', "Scene")

    def process(self, context, inputs):
        scene = inputs.get("Scene")
        if scene:
            res_x = inputs.get("Resolution X")
            res_y = inputs.get("Resolution Y")
            ctx = getattr(getattr(self, "id_data", None), "fn_inputs", None)
            if ctx:
                ctx.store_original(scene.render, "resolution_x")
                ctx.store_original(scene.render, "resolution_y")
            try:
                scene.render.resolution_x = res_x
                scene.render.resolution_y = res_y
            except Exception:
                pass
        return {"Scene": scene}


def register():
    bpy.utils.register_class(FNOutputProps)

def unregister():
    bpy.utils.unregister_class(FNOutputProps)
