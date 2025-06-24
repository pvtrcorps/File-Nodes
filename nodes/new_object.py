import bpy
from bpy.types import Node
from .base import FNBaseNode
from ..sockets import (
    FNSocketObject, FNSocketMesh, FNSocketLight, FNSocketCamera
)
from ..operators import auto_evaluate_if_enabled

_object_data_socket = {
    'EMPTY': None,
    'MESH': 'FNSocketMesh',
    'LIGHT': 'FNSocketLight',
    'CAMERA': 'FNSocketCamera',
}

class FNNewObject(Node, FNBaseNode):
    bl_idname = "FNNewObject"
    bl_label = "New Object"

    name: bpy.props.StringProperty(name="Name", default="Object", update=auto_evaluate_if_enabled)
    obj_type: bpy.props.EnumProperty(
        name="Type",
        items=[
            ('EMPTY', 'Empty', ''),
            ('MESH', 'Mesh', ''),
            ('LIGHT', 'Light', ''),
            ('CAMERA', 'Camera', ''),
        ],
        default='EMPTY',
        update=lambda self, context: self.update_sockets(context)
    )

    def update_sockets(self, context):
        while self.inputs:
            self.inputs.remove(self.inputs[-1])
        if _object_data_socket[self.obj_type]:
            self.inputs.new(_object_data_socket[self.obj_type], "Data")
        while self.outputs:
            self.outputs.remove(self.outputs[-1])
        self.outputs.new('FNSocketObject', "Object")
        auto_evaluate_if_enabled(context)

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.update_sockets(context)

    def draw_buttons(self, context, layout):
        layout.prop(self, "name", text="Name")
        layout.prop(self, "obj_type", text="Type")

    def process(self, context, inputs):
        data = None
        if self.obj_type == 'MESH':
            data = inputs.get("Data") or bpy.data.meshes.new(f"{self.name}Mesh")
        elif self.obj_type == 'LIGHT':
            data = inputs.get("Data") or bpy.data.lights.new(f"{self.name}Light", type='POINT')
        elif self.obj_type == 'CAMERA':
            data = inputs.get("Data") or bpy.data.cameras.new(f"{self.name}Camera")
        obj = bpy.data.objects.new(self.name, data)
        return {"Object": obj}


def register():
    bpy.utils.register_class(FNNewObject)


def unregister():
    bpy.utils.unregister_class(FNNewObject)
