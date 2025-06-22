
import bpy
from bpy.types import Node
from .base import FNBaseNode


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

    def update(self):
        self._sync_with_interface()

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

    def process(self, context, inputs):
        outputs = {}
        for item in _interface_inputs(self.id_data):
            if item.name == "Scene":
                outputs[item.name] = context.scene
            else:
                outputs[item.name] = None
        return outputs

def register():
    bpy.utils.register_class(FNGroupInputNode)
def unregister():
    bpy.utils.unregister_class(FNGroupInputNode)
