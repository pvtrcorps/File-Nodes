"""Node for creating new lights."""

import bpy
from bpy.types import Node
from .base import FNBaseNode, FNCacheIDMixin
from ..sockets import FNSocketLight, FNSocketString
from .. import uuid_manager


class FNNewLight(Node, FNCacheIDMixin, FNBaseNode):
    """Create a new light datablock."""
    bl_idname = "FNNewLight"
    bl_label = "New Light"

    light_type: bpy.props.EnumProperty(
        name="Type",
        items=[
            ('POINT', 'Point', ''),
            ('SUN', 'Sun', ''),
            ('SPOT', 'Spot', ''),
            ('AREA', 'Area', ''),
        ],
        default='POINT',
        update=lambda self, context: None,
    )

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        sock = self.inputs.new('FNSocketString', "Name")
        sock.value = "Light"
        self.outputs.new('FNSocketLight', "Light")

    def draw_buttons(self, context, layout):
        layout.prop(self, "light_type", text="Type")

    def free(self):
        self._invalidate_cache()

    def process(self, context, inputs, manager):
        name = inputs.get("Name") or "Light"
        
        node_tree = self.id_data
        node_key = f"{self.name}_{self.light_type}"
        
        light = None
        existing_uuid = node_tree.get_datablock_uuid(node_key)
        if existing_uuid:
            light = uuid_manager.find_datablock_by_uuid(existing_uuid, bpy.data.lights)

        if light is None:
            light = bpy.data.lights.get(name)
            if light and uuid_manager.get_uuid(light) is None:
                pass
            else:
                light = None

        if light is None:
            light = bpy.data.lights.new(name, type=self.light_type)
            light_uuid = uuid_manager.get_or_create_uuid(light)
            node_tree.set_datablock_uuid(node_key, light_uuid)
        else:
            if light.name != name:
                light.name = name
            if light.type != self.light_type:
                light.type = self.light_type
            light_uuid = uuid_manager.get_or_create_uuid(light)
            node_tree.set_datablock_uuid(node_key, light_uuid)

        return {"Light": light}


def register():
    bpy.utils.register_class(FNNewLight)


def unregister():
    bpy.utils.unregister_class(FNNewLight)