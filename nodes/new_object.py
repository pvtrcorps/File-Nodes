import bpy
from bpy.types import Node
from .base import FNBaseNode, FNCacheIDMixin
from ..sockets import (
    FNSocketObject, FNSocketMesh, FNSocketLight, FNSocketCamera, FNSocketString
)
from ..operators import auto_evaluate_if_enabled

_object_data_socket = {
    'EMPTY': None,
    'MESH': 'FNSocketMesh',
    'LIGHT': 'FNSocketLight',
    'CAMERA': 'FNSocketCamera',
}

class FNNewObject(Node, FNCacheIDMixin, FNBaseNode):
    bl_idname = "FNNewObject"
    bl_label = "New Object"
    color_tag = 'OUTPUT'
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
        name_sock = self.inputs.new('FNSocketString', "Name")
        name_sock.value = "Object"
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
        layout.prop(self, "obj_type", text="Type")

    def free(self):
        self._invalidate_cache()

    def process(self, context, inputs):
        data = None
        created_data = None
        if self.obj_type == 'MESH':
            data = inputs.get("Data")
            if not data:
                data = bpy.data.meshes.new(f"{inputs.get('Name') or 'Object'}Mesh")
                created_data = data
        elif self.obj_type == 'LIGHT':
            data = inputs.get("Data")
            if not data:
                data = bpy.data.lights.new(f"{inputs.get('Name') or 'Object'}Light", type='POINT')
                created_data = data
        elif self.obj_type == 'CAMERA':
            data = inputs.get("Data")
            if not data:
                data = bpy.data.cameras.new(f"{inputs.get('Name') or 'Object'}Camera")
                created_data = data
        name = inputs.get("Name") or "Object"
        key = (self.obj_type, name, data)
        cached = self.cache_get(key)
        if cached is not None:
            return {"Object": cached}
        obj = bpy.data.objects.new(name, data)
        self.cache_store(key, obj)
        ctx = getattr(getattr(self, "id_data", None), "fn_inputs", None)
        if ctx:
            ctx.remember_created_id(obj)
            if created_data:
                ctx.remember_created_id(created_data)
        return {"Object": obj}


def register():
    bpy.utils.register_class(FNNewObject)


def unregister():
    bpy.utils.unregister_class(FNNewObject)
