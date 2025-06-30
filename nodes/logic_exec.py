import bpy
from bpy.types import Node
from .base import FNBaseNode
from ..operators import auto_evaluate_if_enabled
from ..sockets import FNSocketExec

class FNLogicExec(Node, FNBaseNode):
    """Logic operations for execution sockets."""
    bl_idname = "FNLogicExec"
    bl_label = "Logic"

    operation: bpy.props.EnumProperty(
        name="Operation",
        items=[('AND', 'And', ''), ('OR', 'Or', '')],
        default='OR',
        update=lambda self, context: auto_evaluate_if_enabled(context)
    )

    def init(self, context):
        self.inputs.new('FNSocketExec', "A")
        self.inputs.new('FNSocketExec', "B")
        self.outputs.new('FNSocketExec', "Result")

    def draw_buttons(self, context, layout):
        layout.prop(self, "operation", text="")

    def process(self, context, inputs):
        a = bool(inputs.get("A"))
        b = bool(inputs.get("B"))
        if self.operation == 'AND':
            value = a and b
        else:
            value = a or b
        return {"Result": value}


def register():
    bpy.utils.register_class(FNLogicExec)


def unregister():
    bpy.utils.unregister_class(FNLogicExec)
