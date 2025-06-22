import bpy
from bpy.types import Node
from .base import FNBaseNode
from ..sockets import (
    FNSocketScene, FNSocketObject, FNSocketCollection, FNSocketWorld,
    FNSocketSceneList, FNSocketObjectList, FNSocketCollectionList, FNSocketWorldList,
)

_socket_single = {
    'SCENE': 'FNSocketScene',
    'OBJECT': 'FNSocketObject',
    'COLLECTION': 'FNSocketCollection',
    'WORLD': 'FNSocketWorld',
}
_socket_list = {
    'SCENE': 'FNSocketSceneList',
    'OBJECT': 'FNSocketObjectList',
    'COLLECTION': 'FNSocketCollectionList',
    'WORLD': 'FNSocketWorldList',
}

class FNGetItemByName(Node, FNBaseNode):
    bl_idname = "FNGetItemByName"
    bl_label = "Get Item by Name"

    data_type: bpy.props.EnumProperty(
        name="Type",
        items=[
            ('SCENE', 'Scene', ''),
            ('OBJECT', 'Object', ''),
            ('COLLECTION', 'Collection', ''),
            ('WORLD', 'World', ''),
        ],
        default='WORLD',
        update=lambda self, context: self.update_sockets()
    )

    item_name: bpy.props.StringProperty(name='Name', default='')

    def update_sockets(self):
        while self.inputs:
            self.inputs.remove(self.inputs[-1])
        while self.outputs:
            self.outputs.remove(self.outputs[-1])
        list_sock = _socket_list[self.data_type]
        single = _socket_single[self.data_type]
        self.inputs.new(list_sock, f"{self.data_type.title()}s")
        self.outputs.new(single, self.data_type.title())

    def init(self, context):
        self.update_sockets()

    def draw_buttons(self, context, layout):
        layout.prop(self, "data_type", text="Type")
        layout.prop(self, "item_name", text="Name")

    def process(self, context, inputs):
        lst = inputs.get(f"{self.data_type.title()}s", [])
        target = None
        for item in lst:
            if item and item.name == self.item_name:
                target = item
                break
        return {self.data_type.title(): target}

def register():
    bpy.utils.register_class(FNGetItemByName)

def unregister():
    bpy.utils.unregister_class(FNGetItemByName)
