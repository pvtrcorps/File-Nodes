import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketString
from ..operators import auto_evaluate_if_enabled


class FNJoinStrings(Node, FNBaseNode):
    bl_idname = "FNJoinStrings"
    bl_label = "Join Strings"

    # Start with two string inputs by default so users can immediately
    # join at least two items without manually adding sockets.
    item_count: bpy.props.IntProperty(default=2)
    separator: bpy.props.StringProperty(name="Separator", default="", update=auto_evaluate_if_enabled)

    def init(self, context):
        # Provide two inputs by default to avoid crashes when the node
        # is evaluated with an empty socket list. Users can add more
        # sockets via the virtual socket as usual.
        self.inputs.new('FNSocketString', "String 1")
        self.inputs.new('FNSocketString', "String 2")
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
        # Accessing link.to_socket.node can crash during link creation.
        # Instead, compare with the last input socket directly.
        if self.inputs and link.to_socket == self.inputs[-1] and link.to_socket.bl_idname == 'NodeSocketVirtual':
            idx = self.item_count + 1
            new_sock = self.inputs.new('FNSocketString', f"String {idx}")
            self.inputs.move(self.inputs.find(new_sock.name), len(self.inputs) - 2)
            self.item_count += 1
            # Reuse the dragged link and remove the temporary one so the
            # operation succeeds without Blender creating another link.
            tree = self.id_data
            tree.links.new(link.from_socket, new_sock)
            # Safely remove Blender's temporary link if it was added. Avoid
            # using `in` which can raise TypeError; iterate manually instead.
            if any(l is link for l in tree.links):
                tree.links.remove(link)
            self._ensure_virtual()
            return None
        return None

    def _ensure_virtual(self):
        real_inputs = [s for s in self.inputs if s.bl_idname != 'NodeSocketVirtual']
        while len(real_inputs) > 2 and not (real_inputs[-1].is_linked or getattr(real_inputs[-1], 'value', None)):
            self.inputs.remove(real_inputs[-1])
            real_inputs.pop()
            self.item_count -= 1

        if not self.inputs or self.inputs[-1].bl_idname != 'NodeSocketVirtual':
            self.inputs.new('NodeSocketVirtual', "")

        for idx, sock in enumerate(real_inputs, 1):
            sock.name = f"String {idx}"

        self.item_count = len(real_inputs)


def register():
    bpy.utils.register_class(FNJoinStrings)


def unregister():
    bpy.utils.unregister_class(FNJoinStrings)
