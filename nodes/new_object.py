"""Node for creating new objects of various types."""

import bpy
from bpy.types import Node
from .base import FNBaseNode, FNCacheIDMixin
from ..sockets import (
    FNSocketObject, FNSocketMesh, FNSocketLight, FNSocketCamera, FNSocketString
)
from ..operators import auto_evaluate_if_enabled
from .. import uuid_manager

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
            sock = self.inputs.new(_object_data_socket[self.obj_type], "Data")
            sock.is_mutable = False
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

    def process(self, context, inputs, manager):
        data = inputs.get("Data")
        name = inputs.get("Name") or "Object"
        
        # Get the node tree this node belongs to
        node_tree = self.id_data
        
        # Generate a unique key for this node within the tree
        node_key = f"{self.name}_{self.obj_type}"
        
        # Try to find an existing object managed by this node
        obj = None
        existing_uuid = node_tree.get_datablock_uuid(node_key)
        if existing_uuid:
            obj = uuid_manager.find_datablock_by_uuid(existing_uuid, bpy.data.objects)

        if obj is None:
            # If no managed object found, try to find an existing one by name
            obj = bpy.data.objects.get(name)
            if obj and uuid_manager.get_uuid(obj) is None: # Only use if not managed by another node
                pass # Use this existing object
            else:
                obj = None # Don't use it if it's managed by another node

        if obj is None:
            # Create new object if no existing one was found
            if data is None:
                if self.obj_type == 'MESH':
                    data = bpy.data.meshes.new(f"{name}Mesh")
                elif self.obj_type == 'LIGHT':
                    data = bpy.data.lights.new(f"{name}Light", type='POINT')
                elif self.obj_type == 'CAMERA':
                    data = bpy.data.cameras.new(f"{name}Camera")
            obj = bpy.data.objects.new(name, data)
            # Assign a UUID and store it in the state map
            obj_uuid = uuid_manager.get_or_create_uuid(obj)
            node_tree.set_datablock_uuid(node_key, obj_uuid)
        else:
            # Update existing object
            if obj.name != name:
                obj.name = name
            if data is not None:
                try:
                    obj.data = data
                except Exception:
                    pass
            # Ensure it has a UUID and is in the state map
            obj_uuid = uuid_manager.get_or_create_uuid(obj)
            node_tree.set_datablock_uuid(node_key, obj_uuid)

        return {"Object": obj}


def register():
    bpy.utils.register_class(FNNewObject)


def unregister():
    bpy.utils.unregister_class(FNNewObject)