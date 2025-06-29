"""Node for gathering multiple inputs into a list."""

import bpy
from bpy.types import Node
from ..operators import auto_evaluate_if_enabled
from .base import FNBaseNode
from ..sockets import (
    FNSocketScene, FNSocketObject, FNSocketCollection, FNSocketWorld,
    FNSocketCamera, FNSocketImage, FNSocketLight, FNSocketMaterial,
    FNSocketMesh, FNSocketNodeTree, FNSocketText, FNSocketWorkSpace,
    FNSocketSceneList, FNSocketObjectList, FNSocketCollectionList, FNSocketWorldList,
    FNSocketCameraList, FNSocketImageList, FNSocketLightList, FNSocketMaterialList,
    FNSocketMeshList, FNSocketNodeTreeList, FNSocketTextList, FNSocketWorkSpaceList,
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
_socket_list = {
    'SCENE': 'FNSocketSceneList',
    'OBJECT': 'FNSocketObjectList',
    'COLLECTION': 'FNSocketCollectionList',
    'WORLD': 'FNSocketWorldList',
    'CAMERA': 'FNSocketCameraList',
    'IMAGE': 'FNSocketImageList',
    'LIGHT': 'FNSocketLightList',
    'MATERIAL': 'FNSocketMaterialList',
    'MESH': 'FNSocketMeshList',
    'NODETREE': 'FNSocketNodeTreeList',
    'TEXT': 'FNSocketTextList',
    'WORKSPACE': 'FNSocketWorkSpaceList',
    'VIEW_LAYER': 'FNSocketViewLayerList',
}

class FNCreateList(Node, FNBaseNode):
    """Create a list from several inputs of the chosen type."""
    bl_idname = "FNCreateList"
    bl_label = "Create List"



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
        update=lambda self, context: self.update_type(context)
    )

    def update_type(self, context):
        self._update_sockets(context)
        auto_evaluate_if_enabled(context)

    def _update_sockets(self, context=None):
        while self.inputs:
            self.inputs.remove(self.inputs[-1])
        while self.outputs:
            self.outputs.remove(self.outputs[-1])
        single = _socket_single[self.data_type]
        lst = _socket_list[self.data_type]
        name = self.data_type.replace('_', ' ').title()
        count = max(1, int(self.input_count))
        for i in range(count):
            self.inputs.new(single, f"{name} {i}")
        out = self.outputs.new(lst, f"{name}s")
        out.display_shape = 'SQUARE'
        if context is not None:
            auto_evaluate_if_enabled(context)

    def init(self, context):
        self._update_sockets(context)

    def draw_buttons(self, context, layout):
        layout.prop(self, "data_type", text="Type")
        layout.prop(self, "input_count", text="Inputs")

    def process(self, context, inputs):
        name = self.data_type.replace('_', ' ').title()
        output_name = f"{name}s"
        items = []
        count = max(1, int(self.input_count))
        for i in range(count):
            value = inputs.get(f"{name} {i}")
            if isinstance(value, (list, tuple)):
                items.extend(v for v in value if v is not None)
            elif value is not None:
                items.append(value)
        return {output_name: items}


def register():
    bpy.utils.register_class(FNCreateList)

def unregister():
    bpy.utils.unregister_class(FNCreateList)
