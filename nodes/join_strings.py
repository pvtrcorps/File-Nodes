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
    separator: bpy.props.StringProperty(name="Separator", default="", update=auto_evaluate_if_enabled)

    def init(self, context):
        self._update_sockets()

    def draw_buttons(self, context, layout):
        layout.prop(self, "separator", text="Separator")

    def process(self, context, inputs):
        values = inputs.get("String")
        if values is None:
            parts = []
        elif isinstance(values, (list, tuple)):
            parts = [str(v) for v in values if v is not None]
        else:
            parts = [str(values)]
        joined = self.separator.join(parts)
        return {"String": joined}

    def _update_sockets(self):
        while self.inputs:
            self.inputs.remove(self.inputs[-1])
        while self.outputs:
            self.outputs.remove(self.outputs[-1])
        sock = self.inputs.new('FNSocketString', "String")
        sock.link_limit = 0
        sock.display_shape = 'CIRCLE_DOT'
        self.outputs.new('FNSocketString', "String")


def register():
    bpy.utils.register_class(FNJoinStrings)


def unregister():
    bpy.utils.unregister_class(FNJoinStrings)
