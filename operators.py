
import bpy
from .tree import FileNodesTree
from bpy.types import Operator
from . import ADDON_NAME

_active_tree = None

class FN_OT_evaluate_all(Operator):
    bl_idname = "file_nodes.evaluate"
    bl_label = "Evaluate File Nodes"

    def execute(self, context):
        count = evaluate_tree(context)
        self.report({'INFO'}, f'Evaluated {count} File Node trees')
        return {'FINISHED'}


class FN_OT_render_scenes(Operator):
    bl_idname = "file_nodes.render_scenes"
    bl_label = "Render Scenes"

    def execute(self, context):
        node = context.active_node
        if not isinstance(node, bpy.types.Node) or node.bl_idname != 'FNRenderScenesNode':
            return {'CANCELLED'}

        evaluate_tree(context)

        tree = node.id_data
        resolved = {}

        _list_to_single = {
            'FNSocketSceneList': 'FNSocketScene',
            'FNSocketObjectList': 'FNSocketObject',
            'FNSocketCollectionList': 'FNSocketCollection',
            'FNSocketWorldList': 'FNSocketWorld',
            'FNSocketCameraList': 'FNSocketCamera',
            'FNSocketImageList': 'FNSocketImage',
            'FNSocketLightList': 'FNSocketLight',
            'FNSocketMaterialList': 'FNSocketMaterial',
            'FNSocketMeshList': 'FNSocketMesh',
            'FNSocketNodeTreeList': 'FNSocketNodeTree',
            'FNSocketStringList': 'FNSocketString',
            'FNSocketTextList': 'FNSocketText',
            'FNSocketWorkSpaceList': 'FNSocketWorkSpace',
        }

        def eval_socket(sock):
            if sock.is_linked and sock.links:
                from_sock = sock.links[0].from_socket
                value = eval_node(from_sock.node)[from_sock.name]
                single = _list_to_single.get(sock.bl_idname)
                if single and from_sock.bl_idname == single:
                    return [value] if value is not None else []
                return value
            if hasattr(sock, 'value'):
                return sock.value
            return None

        def eval_node(n):
            if n in resolved:
                return resolved[n]
            inputs = {s.name: eval_socket(s) for s in n.inputs}
            outputs = {}
            if hasattr(n, 'process'):
                outputs = n.process(context, inputs) or {}
            for s in n.outputs:
                outputs.setdefault(s.name, None)
            resolved[n] = outputs
            return outputs

        scenes = eval_socket(node.inputs.get('Scenes')) or []
        for sc in scenes:
            if not sc:
                continue
            try:
                bpy.ops.render.render('INVOKE_DEFAULT', scene=sc.name)
            except Exception:
                pass
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
    global _active_tree
    count = 0
    trees = [t for t in bpy.data.node_groups
             if isinstance(t, FileNodesTree) and getattr(t, "fn_enabled", True)]
    trees = sorted(trees, key=lambda t: getattr(t, "fn_stack_index", 0))

    for tree in trees:
        ctx = getattr(tree, "fn_inputs", None)
        if ctx:
            ctx.scenes_to_keep = []
            ctx.reset_to_originals()

    for tree in trees:
        ctx = getattr(tree, "fn_inputs", None)
        if ctx:
            ctx.sync_inputs(tree)
            ctx.prepare_eval_scene(context.scene)
            _active_tree = tree
            _evaluate_tree(tree, context)
            _active_tree = None
            count += 1
    return count

def _evaluate_tree(tree, context):
    resolved = {}

    _list_to_single = {
        'FNSocketSceneList': 'FNSocketScene',
        'FNSocketObjectList': 'FNSocketObject',
        'FNSocketCollectionList': 'FNSocketCollection',
        'FNSocketWorldList': 'FNSocketWorld',
        'FNSocketCameraList': 'FNSocketCamera',
        'FNSocketImageList': 'FNSocketImage',
        'FNSocketLightList': 'FNSocketLight',
        'FNSocketMaterialList': 'FNSocketMaterial',
        'FNSocketMeshList': 'FNSocketMesh',
        'FNSocketNodeTreeList': 'FNSocketNodeTree',
        'FNSocketStringList': 'FNSocketString',
        'FNSocketTextList': 'FNSocketText',
        'FNSocketWorkSpaceList': 'FNSocketWorkSpace',
    }

    output_types = {
        'FNOutputScenesNode',
        'FNRenderScenesNode',
        'FNGroupOutputNode',
    }

    def eval_socket(sock):
        if sock.is_linked and sock.links:
            from_sock = sock.links[0].from_socket
            value = eval_node(from_sock.node)[from_sock.name]
            single = _list_to_single.get(sock.bl_idname)
            if single and from_sock.bl_idname == single:
                return [value] if value is not None else []
            return value
        if hasattr(sock, 'value'):
            return sock.value
        return None

    def eval_node(node):
        if node in resolved:
            return resolved[node]

        inputs = {s.name: eval_socket(s) for s in node.inputs}
        outputs = {}
        if hasattr(node, 'process'):
            outputs = node.process(context, inputs) or {}
        for s in node.outputs:
            outputs.setdefault(s.name, None)
        resolved[node] = outputs
        return outputs

    visited = set()

    def traverse(node):
        if node in visited:
            return
        visited.add(node)
        eval_node(node)
        for sock in node.inputs:
            if sock.is_linked and sock.links:
                from_node = sock.links[0].from_node
                traverse(from_node)

    for node in tree.nodes:
        if node.bl_idname in output_types:
            traverse(node)

### Registration ###
def register():
    bpy.utils.register_class(FN_OT_evaluate_all)
    bpy.utils.register_class(FN_OT_render_scenes)

def unregister():
    bpy.utils.unregister_class(FN_OT_render_scenes)
    bpy.utils.unregister_class(FN_OT_evaluate_all)
