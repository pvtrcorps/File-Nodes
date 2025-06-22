
import bpy
from .tree import FileNodesTree
from bpy.types import Operator
from collections import deque
from . import ADDON_NAME

class FN_OT_evaluate_all(Operator):
    bl_idname = "file_nodes.evaluate"
    bl_label = "Evaluate File Nodes"

    def execute(self, context):
        count = evaluate_tree(context)
        self.report({'INFO'}, f'Evaluated {count} File Node trees')
        return {'FINISHED'}


def auto_evaluate_if_enabled(self=None, context=None):
    """Evaluate all file node trees if the preference is enabled."""
    if context is None and isinstance(self, bpy.types.Context):
        context = self
    context = context or bpy.context
    prefs = context.preferences.addons.get(ADDON_NAME)
    if prefs and prefs.preferences.auto_evaluate:
        evaluate_tree(context)

### Evaluator ###
def evaluate_tree(context):
    count = 0
    for mod in sorted(context.scene.file_node_modifiers, key=lambda m: m.stack_index):
        if mod.enabled and mod.node_tree:
            _evaluate_tree(mod.node_tree, context)
            count += 1
    return count

def _evaluate_tree(tree, context):
    resolved = {}

    def eval_socket(sock):
        if sock.is_linked and sock.links:
            from_sock = sock.links[0].from_socket
            return eval_node(from_sock.node)[from_sock.name]
        # Unlinked: return stored value if exists
        if hasattr(sock, 'value'):
            return sock.value
        return None

    def eval_node(node):
        if node in resolved:
            return resolved[node]
        # Build inputs dict
        inputs = {sock.name: eval_socket(sock) for sock in node.inputs}
        outputs = {}
        if hasattr(node, 'process'):
            outputs = node.process(context, inputs) or {}
        # Fall back: store each output as None if not provided
        for sock in node.outputs:
            outputs.setdefault(sock.name, None)
        resolved[node] = outputs
        return outputs

    # Evaluate all nodes to resolve actions
    for n in tree.nodes:
        eval_node(n)

### Registration ###
def register():
    bpy.utils.register_class(FN_OT_evaluate_all)

def unregister():
    bpy.utils.unregister_class(FN_OT_evaluate_all)
