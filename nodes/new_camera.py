"""Node for creating new cameras."""

import bpy
from bpy.types import Node
from .base import FNBaseNode, FNCacheIDMixin
from ..sockets import FNSocketCamera, FNSocketString
from .. import uuid_manager


class FNNewCamera(Node, FNCacheIDMixin, FNBaseNode):
    """Create a new camera datablock."""
    bl_idname = "FNNewCamera"
    bl_label = "New Camera"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        sock = self.inputs.new('FNSocketString', "Name")
        sock.value = "Camera"
        self.outputs.new('FNSocketCamera', "Camera")

    def free(self):
        self._invalidate_cache()

    def process(self, context, inputs, manager):
        name = inputs.get("Name") or "Camera"
        
        node_tree = self.id_data
        node_key = f"{self.name}"
        
        cam = None
        existing_uuid = node_tree.get_datablock_uuid(node_key)
        if existing_uuid:
            cam = uuid_manager.find_datablock_by_uuid(existing_uuid, bpy.data.cameras)

        if cam is None:
            cam = bpy.data.cameras.get(name)
            if cam and uuid_manager.get_uuid(cam) is None:
                pass
            else:
                cam = None

        if cam is None:
            cam = bpy.data.cameras.new(name)
            cam_uuid = uuid_manager.get_or_create_uuid(cam)
            node_tree.set_datablock_uuid(node_key, cam_uuid)
        else:
            if cam.name != name:
                cam.name = name
            cam_uuid = uuid_manager.get_or_create_uuid(cam)
            node_tree.set_datablock_uuid(node_key, cam_uuid)

        return {"Camera": cam}


def register():
    bpy.utils.register_class(FNNewCamera)


def unregister():
    bpy.utils.unregister_class(FNNewCamera)