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

    # Provide two sockets by default plus a virtual socket so that
    # newly added nodes can be used immediately without crashing when
    # no real sockets exist.
    item_count: bpy.props.IntProperty(default=2)

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
        self.update_sockets()
        auto_evaluate_if_enabled(context)

    def update_sockets(self):
        while self.inputs:
            self.inputs.remove(self.inputs[-1])
        while self.outputs:
            self.outputs.remove(self.outputs[-1])
        single = _socket_single[self.data_type]
        lst = _socket_list[self.data_type]
        # Two initial sockets are created to prevent crashes that
        # occurred when only a single real socket existed. The
        # virtual socket remains available for adding more.
        self.item_count = 2
        self.inputs.new(single, f"{self.data_type.title()} 1")
        self.inputs.new(single, f"{self.data_type.title()} 2")
        self.inputs.new('NodeSocketVirtual', "")
        sock = self.outputs.new(lst, f"{self.data_type.title()}s")
        sock.display_shape = 'SQUARE'

    def init(self, context):
        self.update_sockets()

    def update(self):
        self._ensure_virtual()

    def draw_buttons(self, context, layout):
        layout.prop(self, "data_type", text="Type")

    def process(self, context, inputs):
        output_name = f"{self.data_type.title()}s"
        lst = []
        for sock in self.inputs:
            if sock.is_linked:
                lst.append(inputs.get(sock.name))
            else:
                if getattr(sock, 'value', None):
                    lst.append(sock.value)
        return {output_name: lst}

    def insert_link(self, link):
        # Blender may crash if we access link.to_socket.node during link creation
        # because the topology cache is not yet built. Compare sockets directly
        # instead of accessing the owner node.
        if self.inputs and link.to_socket == self.inputs[-1] and link.to_socket.bl_idname == 'NodeSocketVirtual':
            idx = self.item_count + 1
            new_sock = self.inputs.new(
                _socket_single[self.data_type],
                f"{self.data_type.title()} {idx}"
            )
            self.inputs.move(
                self.inputs.find(new_sock.name),
                len(self.inputs) - 2
            )
            self.item_count += 1
            # Reuse the dragged link instead of creating a new one
            # to avoid potential crashes when the temporary link
            # is removed by Blender during the operation.
            tree = self.id_data
            tree.links.new(link.from_socket, new_sock)
            self._ensure_virtual()
            return None
        return None

    def _ensure_virtual(self):
        if not self.inputs:
            return

        real_inputs = [s for s in self.inputs if s.bl_idname != 'NodeSocketVirtual']
        type_name = self.data_type.title()
        while len(real_inputs) > 2 and not (real_inputs[-1].is_linked or getattr(real_inputs[-1], 'value', None)):
            self.inputs.remove(real_inputs[-1])
            real_inputs.pop()
            self.item_count -= 1

        if self.inputs[-1].bl_idname != 'NodeSocketVirtual':
            self.inputs.new('NodeSocketVirtual', "")

        for idx, sock in enumerate(real_inputs, 1):
            sock.name = f"{type_name} {idx}"

        self.item_count = len(real_inputs)

def register():
    bpy.utils.register_class(FNCreateList)

def unregister():
    bpy.utils.unregister_class(FNCreateList)
