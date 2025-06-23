
import bpy
from bpy.types import Node
from .base import FNBaseNode
from ..operators import get_active_mod_item


def _interface_inputs(tree):
    iface = getattr(tree, "interface", None)
    for item in getattr(iface, "items_tree", []):
        if getattr(item, "in_out", None) == 'INPUT':
            yield item

class FNGroupInputNode(Node, FNBaseNode):
    bl_idname = "FNGroupInputNode"
    bl_label = "Group Input"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self._sync_with_interface()
        self._ensure_virtual()

    def update(self):
        self._sync_with_interface()
        self._ensure_virtual()

    def _sync_with_interface(self):
        tree = self.id_data
        if not tree:
            return
        iface_sockets = list(_interface_inputs(tree))
        names = [s.name for s in iface_sockets]
        for sock in list(self.outputs):
            if sock.name not in names:
                self.outputs.remove(sock)
        for item in iface_sockets:
            sock = self.outputs.get(item.name)
            if sock is None:
                sock = self.outputs.new(item.socket_type, item.name)
            elif sock.bl_idname != item.socket_type:
                self.outputs.remove(sock)
                sock = self.outputs.new(item.socket_type, item.name)
            sock.name = item.name
        self._ensure_virtual()

    def process(self, context, inputs):
        outputs = {}
        mod = get_active_mod_item()
        for item in _interface_inputs(self.id_data):
            if item.name == "Scene":
                outputs[item.name] = context.scene
            elif mod:
                outputs[item.name] = mod.get_input_value(item.name)
            else:
                outputs[item.name] = None
        return outputs

    def insert_link(self, link):
        if link.from_node == self and link.from_socket.bl_idname == 'NodeSocketVirtual':
            tree = self.id_data
            iface = tree.interface
            name_base = "Input"
            existing = {i.name for i in iface.items_tree if getattr(i, 'in_out', None) == 'INPUT'}
            name = name_base
            idx = 1
            while name in existing:
                idx += 1
                name = f"{name_base} {idx}"
            new_item = iface.new_socket(name=name, in_out='INPUT', socket_type=link.to_socket.bl_idname)
            new_sock = self.outputs.new(new_item.socket_type, new_item.name)
            self.outputs.move(self.outputs.find(new_sock.name), len(self.outputs)-1)
            self.id_data.links.new(new_sock, link.to_socket)
            self._ensure_virtual()
            return True
        return False

    def _ensure_virtual(self):
        if not self.outputs or self.outputs[-1].bl_idname != 'NodeSocketVirtual':
            self.outputs.new('NodeSocketVirtual', "")

def register():
    bpy.utils.register_class(FNGroupInputNode)
def unregister():
    bpy.utils.unregister_class(FNGroupInputNode)
