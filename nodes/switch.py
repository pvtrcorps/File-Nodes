"""Node that outputs one of two values based on a boolean switch."""

import bpy
from bpy.types import Node
from .base import FNBaseNode
from ..operators import auto_evaluate_if_enabled
from ..sockets import (
    FNSocketScene, FNSocketObject, FNSocketCollection, FNSocketWorld,
    FNSocketCamera, FNSocketImage, FNSocketLight, FNSocketMaterial,
    FNSocketMesh, FNSocketNodeTree, FNSocketText, FNSocketWorkSpace,
)

_socket_single = {
    'SCENE': 'FNSocketScene',
    'OBJECT': 'FNSocketObject',
    'COLLECTION': 'FNSocketCollection',
    'WORLD': 'FNSocketWorld',
    'CAMERA': 'FNSocketCamera',
    'IMAGE': 'FNSocketImage',
    'LIGHT': 'FNSocketLight',
    'MATERIAL': 'FNSocketMaterial',
    'MESH': 'FNSocketMesh',
    'NODETREE': 'FNSocketNodeTree',
    'TEXT': 'FNSocketText',
    'WORKSPACE': 'FNSocketWorkSpace',
    'VIEW_LAYER': 'FNSocketViewLayer',
}


class FNSwitch(Node, FNBaseNode):
    """Choose between two inputs based on a boolean value."""
    bl_idname = "FNSwitch"
    bl_label = "Switch"

    data_type: bpy.props.EnumProperty(
        name="Type",
        items=[
            ('SCENE', 'Scene', ''),
            ('OBJECT', 'Object', ''),
            ('COLLECTION', 'Collection', ''),
            ('WORLD', 'World', ''),
            ('CAMERA', 'Camera', ''),
            ('IMAGE', 'Image', ''),
            ('LIGHT', 'Light', ''),
            ('MATERIAL', 'Material', ''),
            ('MESH', 'Mesh', ''),
            ('NODETREE', 'Node Tree', ''),
            ('TEXT', 'Text', ''),
            ('WORKSPACE', 'WorkSpace', ''),
            ('VIEW_LAYER', 'View Layer', ''),
        ],
        default='SCENE',
        update=lambda self, context: self.update_type(context)
    )

    def update_type(self, context):
        self._update_sockets()
        auto_evaluate_if_enabled(context)

    def _update_sockets(self):
        while self.inputs:
            self.inputs.remove(self.inputs[-1])
        while self.outputs:
            self.outputs.remove(self.outputs[-1])
        single = _socket_single[self.data_type]
        name = self.data_type.replace('_', ' ').title()
        self.inputs.new('FNSocketBool', "Switch")
        self.inputs.new(single, "False")
        self.inputs.new(single, "True")
        self.outputs.new(single, name)

    def init(self, context):
        self._update_sockets()

    def draw_buttons(self, context, layout):
        layout.prop(self, "data_type", text="Type")

    def process(self, context, inputs):
        flag = inputs.get("Switch")
        val_false = inputs.get("False")
        val_true = inputs.get("True")
        result = val_true if flag else val_false
        name = self.data_type.replace('_', ' ').title()
        return {name: result}


def register():
    bpy.utils.register_class(FNSwitch)


def unregister():
    bpy.utils.unregister_class(FNSwitch)
