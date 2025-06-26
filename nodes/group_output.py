
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
        self._ensure_virtual()

    def update(self):
        self._sync_with_interface()
        self._ensure_virtual()

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
        self._ensure_virtual()

    def process(self, context, inputs):
        # Terminal node, no action needed
        return {}

    def insert_link(self, link):
        if link.to_node == self and link.to_socket.bl_idname == 'NodeSocketVirtual':
            tree = self.id_data
            iface = tree.interface
            name_base = "Output"
            existing = {i.name for i in iface.items_tree if getattr(i, 'in_out', None) == 'OUTPUT'}
            name = name_base
            idx = 1
            while name in existing:
                idx += 1
                name = f"{name_base} {idx}"
            new_item = iface.new_socket(name=name, in_out='OUTPUT', socket_type=link.from_socket.bl_idname)
            new_sock = self.inputs.new(new_item.socket_type, new_item.name)
            self.inputs.move(self.inputs.find(new_sock.name), len(self.inputs)-1)
            # Reuse the dragged link, remove Blender's temporary one and
            # return success so Blender does not create another link.
            tree.links.new(link.from_socket, new_sock)
            try:
                tree.links.remove(link)
            except RuntimeError:
                pass
            self._ensure_virtual()
            return {'FINISHED'}
        return None

    def _ensure_virtual(self):
        if not self.inputs or self.inputs[-1].bl_idname != 'NodeSocketVirtual':
            self.inputs.new('NodeSocketVirtual', "")

def register():
    bpy.utils.register_class(FNGroupOutputNode)
def unregister():
    bpy.utils.unregister_class(FNGroupOutputNode)
