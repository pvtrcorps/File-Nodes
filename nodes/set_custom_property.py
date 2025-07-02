"""Node to set a custom property on a datablock."""
import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..operators import auto_evaluate_if_enabled
from ..sockets import (
    FNSocketBool, FNSocketFloat, FNSocketInt, FNSocketString, FNSocketVector,
    FNSocketScene, FNSocketObject, FNSocketCollection, FNSocketWorld,
    FNSocketCamera, FNSocketImage, FNSocketLight, FNSocketMaterial,
    FNSocketMesh, FNSocketNodeTree, FNSocketText, FNSocketWorkSpace,
    FNSocketViewLayer,
)

_single_socket = {
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

_value_socket = {
    'BOOL': 'FNSocketBool',
    'FLOAT': 'FNSocketFloat',
    'INT': 'FNSocketInt',
    'STRING': 'FNSocketString',
    'VECTOR': 'FNSocketVector',
}


class FNSetCustomProperty(Node, FNBaseNode):
    """Assign a custom property on any datablock."""
    bl_idname = "FNSetCustomProperty"
    bl_label = "Set Custom Property"

    data_type: bpy.props.EnumProperty(
        name="Data Type",
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
        default='OBJECT',
        update=lambda self, ctx: self._update_sockets(ctx)
    )

    value_type: bpy.props.EnumProperty(
        name="Value Type",
        items=[
            ('BOOL', 'Boolean', ''),
            ('FLOAT', 'Float', ''),
            ('INT', 'Integer', ''),
            ('STRING', 'String', ''),
            ('VECTOR', 'Vector', ''),
        ],
        default='STRING',
        update=lambda self, ctx: self._update_sockets(ctx)
    )

    def _update_sockets(self, context=None):
        while self.inputs:
            self.inputs.remove(self.inputs[-1])
        while self.outputs:
            self.outputs.remove(self.outputs[-1])
        single = _single_socket[self.data_type]
        value_sock = _value_socket[self.value_type]
        id_in = self.inputs.new(single, "ID")
        id_in.show_selector = True
        self.inputs.new('FNSocketString', "Name").value = "prop"
        self.inputs.new(value_sock, "Value")
        self.outputs.new(single, "ID")
        if context is not None:
            auto_evaluate_if_enabled(context)

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self._update_sockets(context)

    def draw_buttons(self, context, layout):
        layout.prop(self, "data_type", text="Type")
        layout.prop(self, "value_type", text="Value")

    def process(self, context, inputs, manager):
        id_data = inputs.get("ID")
        if id_data:
            name = inputs.get("Name") or "prop"
            value = inputs.get("Value")
            try:
                id_data[name] = value
            except Exception:
                pass
        return {"ID": id_data}


def register():
    bpy.utils.register_class(FNSetCustomProperty)


def unregister():
    bpy.utils.unregister_class(FNSetCustomProperty)
