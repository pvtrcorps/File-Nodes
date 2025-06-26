import bpy
from bpy.types import Node

from .base import FNBaseNode, DynamicSocketMixin
from ..sockets import FNSocketString
from ..operators import auto_evaluate_if_enabled


class FNJoinStrings(Node, FNBaseNode, DynamicSocketMixin):
    bl_idname = "FNJoinStrings"
    bl_label = "Join Strings"

    # Start with two string inputs by default so users can immediately
    # join at least two items without manually adding sockets.
    separator: bpy.props.StringProperty(name="Separator", default="", update=auto_evaluate_if_enabled)

    def init(self, context):
        self._update_sockets()

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
        return DynamicSocketMixin.insert_link(self, link)

    def add_socket(self, idx):
        return self.inputs.new('FNSocketString', f"String {idx}")

    def socket_name(self, idx):
        return f"String {idx}"

    def _update_sockets(self):
        while self.inputs:
            self.inputs.remove(self.inputs[-1])
        while self.outputs:
            self.outputs.remove(self.outputs[-1])
        self.add_socket(1)
        self.add_socket(2)
        self.inputs.new('NodeSocketVirtual', "")
        self.outputs.new('FNSocketString', "String")
        self.item_count = 2
        self.update()


def register():
    bpy.utils.register_class(FNJoinStrings)


def unregister():
    bpy.utils.unregister_class(FNJoinStrings)
