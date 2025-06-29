"""Node to select items from an input list."""

import bpy
from bpy.types import Node, PropertyGroup, UIList
from .base import FNBaseNode
from ..operators import auto_evaluate_if_enabled
from ..sockets import (
    FNSocketScene, FNSocketObject, FNSocketCollection, FNSocketWorld,
    FNSocketCamera, FNSocketImage, FNSocketLight, FNSocketMaterial,
    FNSocketMesh, FNSocketNodeTree, FNSocketText, FNSocketWorkSpace,
    FNSocketSceneList, FNSocketObjectList, FNSocketCollectionList, FNSocketWorldList,
    FNSocketCameraList, FNSocketImageList, FNSocketLightList, FNSocketMaterialList,
    FNSocketMeshList, FNSocketNodeTreeList, FNSocketTextList, FNSocketWorkSpaceList,
    FNSocketViewLayer, FNSocketViewLayerList
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


class FNItemInList(PropertyGroup):
    """Representation of one element for the UI list."""

    name: bpy.props.StringProperty()
    index: bpy.props.IntProperty()
    selected: bpy.props.BoolProperty(name="", update=auto_evaluate_if_enabled)


class FN_UL_items_in_list(UIList):
    bl_idname = "FN_UL_items_in_list"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, "selected", text="")
            row.label(text=item.name)


class FNGetItemInList(Node, FNBaseNode):
    """Select items from an input list."""
    bl_idname = "FNGetItemInList"
    bl_label = "Get Item in List"

    items: bpy.props.CollectionProperty(type=FNItemInList)
    active_index: bpy.props.IntProperty()

    # Internal enum to know which output socket should be present. It is hidden
    # so the user does not interact with it directly.
    output_mode: bpy.props.EnumProperty(
        items=[('SINGLE', 'Single', ''), ('LIST', 'List', '')],
        options={'HIDDEN'},
        name="Output Mode",
        default='LIST',
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
        self.update_sockets(self.output_mode == 'SINGLE')
        auto_evaluate_if_enabled(context)

    def update_sockets(self, single_output):
        while self.inputs:
            self.inputs.remove(self.inputs[-1])
        while self.outputs:
            self.outputs.remove(self.outputs[-1])
        list_sock = _socket_list[self.data_type]
        single = _socket_single[self.data_type]
        inp = self.inputs.new(list_sock, f"{self.data_type.title()}s")
        inp.display_shape = 'SQUARE'
        if single_output:
            self.outputs.new(single, self.data_type.title())
            self.output_mode = 'SINGLE'
        else:
            out = self.outputs.new(list_sock, f"{self.data_type.title()}s")
            out.display_shape = 'SQUARE'
            self.output_mode = 'LIST'

    def init(self, context):
        self.update_sockets(False)

    def _sync_items(self, lst):
        old = {item.name: item.selected for item in self.items}
        self.items.clear()
        for idx, val in enumerate(lst):
            it = self.items.add()
            name = getattr(val, "name", str(val)) if val is not None else "<None>"
            it.name = name
            it.index = idx
            it.selected = old.get(name, False)

    def draw_buttons(self, context, layout):
        layout.prop(self, "data_type", text="Type")
        if not self.items:
            layout.label(text="No Items")
            return
        layout.template_list(
            "FN_UL_items_in_list",
            "",
            self,
            "items",
            self,
            "active_index",
            rows=4,
        )

    def process(self, context, inputs):
        lst = inputs.get(f"{self.data_type.title()}s") or []
        if not isinstance(lst, (list, tuple)):
            lst = [lst] if lst else []
        self._sync_items(lst)
        selected = [
            lst[item.index]
            for item in self.items
            if item.selected and 0 <= item.index < len(lst)
        ]
        mode_single = len(selected) == 1
        if (
            mode_single and self.output_mode != 'SINGLE'
        ) or (
            not mode_single and self.output_mode != 'LIST'
        ):
            self.update_sockets(mode_single)
            auto_evaluate_if_enabled(context)
        if mode_single:
            return {self.data_type.title(): selected[0]}
        return {f"{self.data_type.title()}s": selected}


_classes = (
    FNItemInList,
    FN_UL_items_in_list,
    FNGetItemInList,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
