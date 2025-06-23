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
}

class FNGetItemByIndex(Node, FNBaseNode):
    bl_idname = "FNGetItemByIndex"
    bl_label = "Get Item by Index"

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
        ],
        default='WORLD',
        update=lambda self, context: self.update_type(context)
    )

    index: bpy.props.IntProperty(name='Index', default=0, update=auto_evaluate_if_enabled)

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
        sock = self.inputs.new(list_sock, f"{self.data_type.title()}s")
        sock.display_shape = 'SQUARE'
        self.outputs.new(single, self.data_type.title())

    def init(self, context):
        self.update_sockets()

    def draw_buttons(self, context, layout):
        layout.prop(self, "data_type", text="Type")
        layout.prop(self, "index", text="Index")

    def process(self, context, inputs):
        lst = inputs.get(f"{self.data_type.title()}s", [])
        item = None
        idx = self.index
        if isinstance(lst, (list, tuple)) and 0 <= idx < len(lst):
            item = lst[idx]
        return {self.data_type.title(): item}

def register():
    bpy.utils.register_class(FNGetItemByIndex)

def unregister():
    bpy.utils.unregister_class(FNGetItemByIndex)
