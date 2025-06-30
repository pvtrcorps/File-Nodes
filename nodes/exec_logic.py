import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..operators import auto_evaluate_if_enabled
from ..sockets import FNSocketExec


class FNExecLogic(Node, FNBaseNode):
    """Logic operations on execution sockets."""
    bl_idname = "FNExecLogic"
    bl_label = "Execution Logic"

    op: bpy.props.EnumProperty(
        name="Operation",
        items=[('AND', 'And', ''), ('OR', 'Or', '')],
        default='AND',
        update=auto_evaluate_if_enabled,
    )

    input_count: bpy.props.IntProperty(
        name="Inputs",
        default=2,
        min=1,
        update=lambda self, ctx: self._update_sockets(ctx)
    )

    def _update_sockets(self, context=None):
        while self.inputs:
            self.inputs.remove(self.inputs[-1])
        while self.outputs:
            self.outputs.remove(self.outputs[-1])
        count = max(1, int(self.input_count))
        for i in range(count):
            self.inputs.new('FNSocketExec', f"Exec {i}")
        self.outputs.new('FNSocketExec', 'Exec')
        if context is not None:
            auto_evaluate_if_enabled(context)

    def init(self, context):
        self._update_sockets(context)

    def draw_buttons(self, context, layout):
        layout.prop(self, "op", text="Operation")
        layout.prop(self, "input_count", text="Inputs")

    def process(self, context, inputs):
        values = [inputs.get(f"Exec {i}") for i in range(max(1, int(self.input_count)))]
        values = [bool(v) for v in values]
        result = all(values) if self.op == 'AND' else any(values)
        return {"Exec": result}


def register():
    bpy.utils.register_class(FNExecLogic)


def unregister():
    bpy.utils.unregister_class(FNExecLogic)
