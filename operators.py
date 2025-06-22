
import bpy
from .tree import FileNodesTree
from bpy.types import Operator
from collections import deque

class FN_OT_evaluate_all(Operator):
    bl_idname = "file_nodes.evaluate"
    bl_label = "Evaluate File Nodes"

    def execute(self, context):
        trees = [nt for nt in bpy.data.node_groups if isinstance(nt, FileNodesTree) and nt.fn_enabled]
        trees.sort(key=lambda t: t.fn_stack_index)
        for tree in trees:
            evaluate_tree(tree, context)
        self.report({'INFO'}, f'Evaluated {len(trees)} File Node trees')
        return {'FINISHED'}

### Evaluator ###
def evaluate_tree(tree, context):
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
