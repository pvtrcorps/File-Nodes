import bpy
from bpy.types import Operator
from . import ADDON_NAME
from .common import LIST_TO_SINGLE

_active_tree = None


class FN_OT_evaluate_all(Operator):
    bl_idname = "file_nodes.evaluate"
    bl_label = "Evaluate File Nodes"

    def execute(self, context):
        count = evaluate_tree(context)
        self.report({"INFO"}, f"Evaluated {count} File Node trees")
        return {"FINISHED"}


class FN_OT_new_tree(Operator):
    bl_idname = "file_nodes.new_tree"
    bl_label = "New File Nodes Tree"

    def execute(self, context):
        tree = bpy.data.node_groups.new("File Nodes", "FileNodesTreeType")
        tree.use_fake_user = True
        context.scene.file_nodes_tree = tree
        return {"FINISHED"}


class FN_OT_remove_tree(Operator):
    bl_idname = "file_nodes.remove_tree"
    bl_label = "Remove File Nodes Tree"

    @classmethod
    def poll(cls, context):
        return context.scene.file_nodes_tree is not None

    def execute(self, context):
        tree = context.scene.file_nodes_tree
        if tree:
            bpy.data.node_groups.remove(tree)
            context.scene.file_nodes_tree = None
        return {"FINISHED"}


class FN_OT_group_nodes(Operator):
    bl_idname = "file_nodes.group_nodes"
    bl_label = "Group Selected Nodes"

    def execute(self, context):
        try:
            bpy.ops.node.group_make()
        except Exception:
            return {"CANCELLED"}
        return {"FINISHED"}


class FN_OT_ungroup_nodes(Operator):
    bl_idname = "file_nodes.ungroup_nodes"
    bl_label = "Ungroup Nodes"

    def execute(self, context):
        try:
            bpy.ops.node.group_ungroup()
        except Exception:
            return {"CANCELLED"}
        return {"FINISHED"}


class FN_OT_render_scenes(Operator):
    bl_idname = "file_nodes.render_scenes"
    bl_label = "Render Scenes"

    def execute(self, context):
        node = context.active_node
        if (
            not isinstance(node, bpy.types.Node)
            or node.bl_idname != "FNRenderScenesNode"
        ):
            return {"CANCELLED"}

        evaluate_tree(context)

        tree = node.id_data
        resolved = {}

        def eval_socket(sock):
            if sock.is_linked and sock.links:
                from_sock = sock.links[0].from_socket
                outputs = eval_node(from_sock.node)
                value = outputs.get(from_sock.name)
                if value is None:
                    ident = getattr(from_sock, "identifier", from_sock.name)
                    value = outputs.get(ident)
                single = LIST_TO_SINGLE.get(sock.bl_idname)
                if single and from_sock.bl_idname == single:
                    return [value] if value is not None else []
                return value
            if hasattr(sock, "value"):
                return sock.value
            return None

        def eval_node(n):
            if n in resolved:
                return resolved[n]
            inputs = {s.name: eval_socket(s) for s in n.inputs}
            outputs = {}
            if hasattr(n, "process"):
                outputs = n.process(context, inputs) or {}
            for s in n.outputs:
                key = getattr(s, "identifier", s.name)
                outputs.setdefault(key, None)
                if key != s.name:
                    outputs.setdefault(s.name, outputs[key])
            resolved[n] = outputs
            return outputs

        scenes = eval_socket(node.inputs.get("Scenes")) or []
        for sc in scenes:
            if not sc:
                continue
            try:
                bpy.ops.render.render("INVOKE_DEFAULT", scene=sc.name)
            except Exception:
                pass
        return {"FINISHED"}


def auto_evaluate_if_enabled(self=None, context=None):
    """Evaluate all file node trees if the preference is enabled."""
    if context is None and isinstance(self, bpy.types.Context):
        context = self
    context = context or bpy.context
    prefs = context.preferences.addons.get(ADDON_NAME)
    if prefs and prefs.preferences.auto_evaluate and _active_tree is None:
        evaluate_tree(context)


### Evaluator ###
def evaluate_tree(context):
    """Evaluate all File Nodes trees in the current blend file."""
    global _active_tree
    count = 0

    for tree in bpy.data.node_groups:
        if getattr(tree, "bl_idname", "") != "FileNodesTreeType":
            continue
        if not getattr(tree, "fn_enabled", True):
            continue

        ctx = getattr(tree, "fn_inputs", None)
        if ctx:
            ctx.reset_to_originals()
            ctx.scenes_to_keep = []
            ctx.sync_inputs(tree)
            ctx.prepare_eval_scene(context.scene)

        _active_tree = tree
        _evaluate_tree(tree, context)
        _active_tree = None
        count += 1

    return count


def _evaluate_tree(tree, context):
    resolved = {}
    evaluating = set()

    output_types = {
        "FNOutputScenesNode",
        "FNRenderScenesNode",
        "NodeGroupOutput",
        "FNOutlinerNode",
    }

    def eval_socket(sock):
        if sock.is_linked and sock.links:
            single = LIST_TO_SINGLE.get(sock.bl_idname)
            if getattr(sock, "is_multi_input", False):
                values = []
                for link in sock.links:
                    from_sock = link.from_socket
                    outputs = eval_node(from_sock.node)
                    value = outputs.get(from_sock.name)
                    if value is None:
                        ident = getattr(from_sock, "identifier", from_sock.name)
                        value = outputs.get(ident)
                    if single and from_sock.bl_idname == single:
                        if value is not None:
                            values.append(value)
                    else:
                        values.append(value)
                return values
            else:
                from_sock = sock.links[0].from_socket
                outputs = eval_node(from_sock.node)
                value = outputs.get(from_sock.name)
                if value is None:
                    ident = getattr(from_sock, "identifier", from_sock.name)
                    value = outputs.get(ident)
                if single and from_sock.bl_idname == single:
                    return [value] if value is not None else []
                return value
        if hasattr(sock, "value"):
            return sock.value
        return None

    def eval_node(node):
        if node in resolved:
            return resolved[node]
        if node in evaluating:
            # Break cycles by returning already stored outputs
            return resolved.setdefault(node, {s.name: None for s in node.outputs})

        evaluating.add(node)

        if getattr(node, "bl_idname", "") == "NodeGroupInput":
            outputs = {}
            ctx = getattr(node.id_data, "fn_inputs", None)
            for s in node.outputs:
                key = getattr(s, "identifier", s.name)
                value = ctx.get_input_value(s.name) if ctx else None
                outputs[key] = value
                if key != s.name:
                    outputs.setdefault(s.name, value)
            resolved[node] = outputs
            evaluating.discard(node)
            return outputs

        inputs = {s.name: eval_socket(s) for s in node.inputs}
        outputs = {}
        if hasattr(node, "process"):
            outputs = node.process(context, inputs) or {}
        for s in node.outputs:
            key = getattr(s, "identifier", s.name)
            outputs.setdefault(key, None)
            if key != s.name:
                outputs.setdefault(s.name, outputs[key])
        resolved[node] = outputs
        evaluating.discard(node)
        return outputs

    visited = set()

    def traverse(node):
        if node in visited:
            return
        visited.add(node)
        eval_node(node)
        for sock in node.inputs:
            if sock.is_linked and sock.links:
                for link in sock.links:
                    from_node = link.from_node
                    traverse(from_node)

    for node in tree.nodes:
        if node.bl_idname in output_types:
            traverse(node)

    ctx = getattr(tree, "fn_inputs", None)
    if ctx:
        for node in tree.nodes:
            if getattr(node, "bl_idname", "") == "NodeGroupOutput":
                for sock in getattr(node, "inputs", []):
                    stype = getattr(sock, "bl_idname", "")
                    if stype not in {"FNSocketScene", "FNSocketSceneList"}:
                        continue
                    value = eval_socket(sock)
                    if stype in LIST_TO_SINGLE:
                        scenes = value or []
                    else:
                        scenes = [value] if value is not None else []
                    for sc in scenes:
                        if sc:
                            ctx.scenes_to_keep.append(sc)


### Registration ###
def register():
    bpy.utils.register_class(FN_OT_evaluate_all)
    bpy.utils.register_class(FN_OT_group_nodes)
    bpy.utils.register_class(FN_OT_ungroup_nodes)
    bpy.utils.register_class(FN_OT_render_scenes)
    bpy.utils.register_class(FN_OT_new_tree)
    bpy.utils.register_class(FN_OT_remove_tree)


def unregister():
    bpy.utils.unregister_class(FN_OT_remove_tree)
    bpy.utils.unregister_class(FN_OT_new_tree)
    bpy.utils.unregister_class(FN_OT_render_scenes)
    bpy.utils.unregister_class(FN_OT_ungroup_nodes)
    bpy.utils.unregister_class(FN_OT_group_nodes)
    bpy.utils.unregister_class(FN_OT_evaluate_all)
