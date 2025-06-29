"""Node to retrieve an item from a list by its name."""

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

class FNGetItemByName(Node, FNBaseNode):
    """Output the item matching a given name from a list."""
    bl_idname = "FNGetItemByName"
    bl_label = "Get Item by Name"

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
        self.update_sockets()
        auto_evaluate_if_enabled(context)

    def update_sockets(self):
        while self.inputs:
            self.inputs.remove(self.inputs[-1])
        while self.outputs:
            self.outputs.remove(self.outputs[-1])
        list_sock = _socket_list[self.data_type]
        single = _socket_single[self.data_type]
        name = self.data_type.replace('_', ' ').title()
        sock = self.inputs.new(list_sock, f"{name}s")
        sock.display_shape = 'SQUARE'
        self.inputs.new('FNSocketString', "Name")
        self.outputs.new(single, name)

    def init(self, context):
        self.update_sockets()

    def draw_buttons(self, context, layout):
        layout.prop(self, "data_type", text="Type")

    def process(self, context, inputs):
        name = self.data_type.replace('_', ' ').title()
        lst = inputs.get(f"{name}s", [])
        name = inputs.get("Name") or ""
        target = None
        for item in lst:
            if item and item.name == name:
                target = item
                break
        return {name: target}

def register():
    bpy.utils.register_class(FNGetItemByName)

def unregister():
    bpy.utils.unregister_class(FNGetItemByName)
