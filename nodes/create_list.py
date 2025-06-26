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

class FNCreateList(Node, FNBaseNode):
    bl_idname = "FNCreateList"
    bl_label = "Create List"



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

    def update_type(self, context):
        self._update_sockets()
        auto_evaluate_if_enabled(context)

    def _update_sockets(self):
        while self.inputs:
            self.inputs.remove(self.inputs[-1])
        while self.outputs:
            self.outputs.remove(self.outputs[-1])
        single = _socket_single[self.data_type]
        lst = _socket_list[self.data_type]
        sock = self.inputs.new(single, self.data_type.title())
        sock.link_limit = 0
        sock.display_shape = 'CIRCLE_DOT'
        out = self.outputs.new(lst, f"{self.data_type.title()}s")
        out.display_shape = 'SQUARE'

    def init(self, context):
        self._update_sockets()

    def draw_buttons(self, context, layout):
        layout.prop(self, "data_type", text="Type")

    def process(self, context, inputs):
        output_name = f"{self.data_type.title()}s"
        values = inputs.get(self.data_type.title())
        if values is None:
            lst = []
        elif isinstance(values, (list, tuple)):
            lst = [v for v in values if v is not None]
        else:
            lst = [values]
        return {output_name: lst}


def register():
    bpy.utils.register_class(FNCreateList)

def unregister():
    bpy.utils.unregister_class(FNCreateList)
