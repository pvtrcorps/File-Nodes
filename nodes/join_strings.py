import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketString
from ..operators import auto_evaluate_if_enabled


class FNJoinStrings(Node, FNBaseNode):
    bl_idname = "FNJoinStrings"
    bl_label = "Join Strings"

    item_count: bpy.props.IntProperty(default=1)
    separator: bpy.props.StringProperty(name="Separator", default="", update=auto_evaluate_if_enabled)

    def init(self, context):
        self.inputs.new('FNSocketString', "String 1")
        self.inputs.new('NodeSocketVirtual', "")
        self.outputs.new('FNSocketString', "String")

    def update(self):
        self._ensure_virtual()

    def draw_buttons(self, context, layout):
        layout.prop(self, "separator", text="Separator")

    def process(self, context, inputs):
        parts = []
        for sock in self.inputs:
            if sock.bl_idname == 'NodeSocketVirtual':
                continue
            value = inputs.get(sock.name)
            if value is not None:
                parts.append(str(value))
        joined = self.separator.join(parts)
        return {"String": joined}

    def insert_link(self, link):
        if link.to_socket.node == self and link.to_socket.bl_idname == 'NodeSocketVirtual':
            idx = self.item_count + 1
            new_sock = self.inputs.new('FNSocketString', f"String {idx}")
            self.inputs.move(self.inputs.find(new_sock.name), len(self.inputs) - 2)
            self.item_count += 1
            self.id_data.links.new(link.from_socket, new_sock)
            self._ensure_virtual()
            return True
        return False

    def _ensure_virtual(self):
        if not self.inputs or self.inputs[-1].bl_idname != 'NodeSocketVirtual':
            self.inputs.new('NodeSocketVirtual', "")
        last = self.inputs[-1]
        if last.is_linked or getattr(last, 'value', None):
            idx = self.item_count + 1
            last.name = f"String {idx}"
            self.inputs.new('NodeSocketVirtual', "")
            self.item_count += 1


def register():
    bpy.utils.register_class(FNJoinStrings)


def unregister():
    bpy.utils.unregister_class(FNJoinStrings)
