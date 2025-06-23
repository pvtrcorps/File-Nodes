import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketMesh
from ..operators import get_active_mod_item, auto_evaluate_if_enabled


class FNMeshProps(Node, FNBaseNode):
    bl_idname = "FNMeshProps"
    bl_label = "Mesh Properties"

    use_auto_smooth: bpy.props.BoolProperty(
        name="Auto Smooth",
        update=auto_evaluate_if_enabled,
    )

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketMesh', "Mesh")
        self.outputs.new('FNSocketMesh', "Mesh")

    def draw_buttons(self, context, layout):
        layout.prop(self, "use_auto_smooth", text="Auto Smooth")

    def process(self, context, inputs):
        mesh = inputs.get("Mesh")
        if mesh:
            mod = get_active_mod_item()
            if mod:
                mod.store_original(mesh, "use_auto_smooth")
            try:
                mesh.use_auto_smooth = self.use_auto_smooth
            except Exception:
                pass
        return {"Mesh": mesh}


def register():
    bpy.utils.register_class(FNMeshProps)

def unregister():
    bpy.utils.unregister_class(FNMeshProps)
