
import bpy
from bpy.types import Node
from .base import FNBaseNode


def _interface_outputs(tree):
    iface = getattr(tree, "interface", None)
    for item in getattr(iface, "items_tree", []):
        if getattr(item, "in_out", None) == 'OUTPUT':
            yield item

class FNGroupOutputNode(Node, FNBaseNode):
    bl_idname = "FNGroupOutputNode"
    bl_label = "Group Output"

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
        iface_sockets = list(_interface_outputs(tree))
        names = [s.name for s in iface_sockets]
        for sock in list(self.inputs):
            if sock.name not in names:
                self.inputs.remove(sock)
        for item in iface_sockets:
            sock = self.inputs.get(item.name)
            if sock is None:
                sock = self.inputs.new(item.socket_type, item.name)
            elif sock.bl_idname != item.socket_type:
                self.inputs.remove(sock)
                sock = self.inputs.new(item.socket_type, item.name)
            sock.name = item.name

    def process(self, context, inputs):
        # Terminal node, no action needed
        return {}

def register():
    bpy.utils.register_class(FNGroupOutputNode)
def unregister():
    bpy.utils.unregister_class(FNGroupOutputNode)
