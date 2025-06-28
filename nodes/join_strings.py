import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketString
from ..operators import auto_evaluate_if_enabled


class FNJoinStrings(Node, FNBaseNode):
    bl_idname = "FNJoinStrings"
    bl_label = "Join Strings"

    input_count: bpy.props.IntProperty(
        name="Inputs",
        default=2,
        min=1,
        update=lambda self, context: self._update_sockets(context)
    )

    # Join separator between strings
    separator: bpy.props.StringProperty(name="Separator", default="", update=auto_evaluate_if_enabled)

    def init(self, context):
        self._update_sockets(context)

    def draw_buttons(self, context, layout):
        layout.prop(self, "separator", text="Separator")
        layout.prop(self, "input_count", text="Inputs")

    def process(self, context, inputs):
        parts = []
        for i in range(max(1, int(self.input_count))):
            value = inputs.get(f"String {i}")
            if isinstance(value, (list, tuple)):
                parts.extend(str(v) for v in value if v is not None)
            elif value is not None:
                parts.append(str(value))
        joined = self.separator.join(parts)
        return {"String": joined}

    def _update_sockets(self, context=None):
        while self.inputs:
            self.inputs.remove(self.inputs[-1])
        while self.outputs:
            self.outputs.remove(self.outputs[-1])
        count = max(1, int(self.input_count))
        for i in range(count):
            self.inputs.new('FNSocketString', f"String {i}")
        self.outputs.new('FNSocketString', "String")
        if context is not None:
            auto_evaluate_if_enabled(context)


def register():
    bpy.utils.register_class(FNJoinStrings)


def unregister():
    bpy.utils.unregister_class(FNJoinStrings)
