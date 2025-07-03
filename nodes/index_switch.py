"""Node to choose one of several inputs based on an index."""

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


class FNIndexSwitch(Node, FNBaseNode):
    """Select an input socket by index."""
    bl_idname = "FNIndexSwitch"
    bl_label = "Index Switch"

    input_count: bpy.props.IntProperty(
        name="Inputs",
        default=2,
        min=1,
        update=lambda self, context: self._update_sockets(context)
    )

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
        update=lambda self, context: self._update_sockets(context)
    )

    def _update_sockets(self, context=None):
        while self.inputs:
            self.inputs.remove(self.inputs[-1])
        while self.outputs:
            self.outputs.remove(self.outputs[-1])
        self.inputs.new('FNSocketInt', "Index")
        single = _socket_single[self.data_type]
        name = self.data_type.replace('_', ' ').title()
        count = max(1, int(self.input_count))
        for i in range(count):
            sock = self.inputs.new(single, f"Value {i}")
            sock.is_mutable = False
        self.outputs.new(single, name)
        if context is not None:
            auto_evaluate_if_enabled(context)

    # Backwards compatible name used in tests
    def update_sockets(self, context=None):
        self._update_sockets(context)

    def init(self, context):
        self._update_sockets(context)

    def draw_buttons(self, context, layout):
        layout.prop(self, "data_type", text="Type")
        layout.prop(self, "input_count", text="Inputs")

    def process(self, context, inputs, manager):
        idx = inputs.get("Index") or 0
        values = [inputs.get(f"Value {i}") for i in range(max(1, int(self.input_count)))]
        result = values[idx] if isinstance(idx, int) and 0 <= idx < len(values) else None
        name = self.data_type.replace('_', ' ').title()
        return {name: result}


def register():
    bpy.utils.register_class(FNIndexSwitch)


def unregister():
    bpy.utils.unregister_class(FNIndexSwitch)
