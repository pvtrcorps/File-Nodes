"""Node for creating new objects of various types."""

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
    """Create a new object of the chosen type."""
    bl_idname = "FNNewObject"
    bl_label = "New Object"
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
        data = inputs.get("Data")
        created_data = None
        name = inputs.get("Name") or "Object"
        key = (self.obj_type, name)
        cached = self.cache_get(key)
        ctx = getattr(getattr(self, "id_data", None), "fn_inputs", None)
        if cached is not None:
            obj = cached
        else:
            obj = None

        if obj is None and ctx:
            storage = getattr(ctx, "_original_values", {})
            for o in storage.get("created_ids", []):
                if isinstance(o, bpy.types.Object) and o.name == name:
                    obj = o
                    break

        if obj is None:
            existing = bpy.data.objects.get(name)
            if existing is not None:
                obj = existing

        if data is None:
            if self.obj_type == 'MESH':
                data = bpy.data.meshes.new(f"{name}Mesh")
                created_data = data
            elif self.obj_type == 'LIGHT':
                data = bpy.data.lights.new(f"{name}Light", type='POINT')
                created_data = data
            elif self.obj_type == 'CAMERA':
                data = bpy.data.cameras.new(f"{name}Camera")
                created_data = data

        if obj is not None:
            try:
                obj.data = data
            except Exception:
                pass
        else:
            obj = bpy.data.objects.new(name, data)
            if ctx:
                ctx.remember_created_id(obj)
        if created_data and ctx:
            ctx.remember_created_id(created_data)
        self.cache_store(key, obj)
        return {"Object": obj}


def register():
    bpy.utils.register_class(FNNewObject)


def unregister():
    bpy.utils.unregister_class(FNNewObject)
