import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketCamera, FNSocketFloat



class FNCameraProps(Node, FNBaseNode):
    bl_idname = "FNCameraProps"
    bl_label = "Camera Properties"
    color_tag = 'OUTPUT'


    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketCamera', "Camera")
        sock = self.inputs.new('FNSocketFloat', "Focal Length")
        sock.value = 50.0
        self.outputs.new('FNSocketCamera', "Camera")

    def process(self, context, inputs):
        cam = inputs.get("Camera")
        if cam:
            lens = inputs.get("Focal Length")
            ctx = getattr(getattr(self, "id_data", None), "fn_inputs", None)
            if ctx:
                ctx.store_original(cam, "lens")
            try:
                cam.lens = lens
            except Exception:
                pass
        return {"Camera": cam}


def register():
    bpy.utils.register_class(FNCameraProps)

def unregister():
    bpy.utils.unregister_class(FNCameraProps)
