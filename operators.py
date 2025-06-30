import bpy
from bpy.types import Operator
from . import ADDON_NAME
from .common import LIST_TO_SINGLE
from . import cow_engine

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


class FN_OT_trigger_exec(Operator):
    bl_idname = "file_nodes.trigger_exec"
    bl_label = "Execute Socket"

    tree_name: bpy.props.StringProperty()
    node_name: bpy.props.StringProperty()
    socket_name: bpy.props.StringProperty()
    group_input: bpy.props.BoolProperty(default=False)

    def execute(self, context):
        tree = bpy.data.node_groups.get(self.tree_name)
        if not tree:
            return {'CANCELLED'}
        auto_eval = False
        prefs = context.preferences.addons.get(ADDON_NAME)
        if prefs:
            auto_eval = prefs.preferences.auto_evaluate
        if self.group_input:
            inp = tree.fn_inputs.inputs.get(self.socket_name)
            if not inp:
                return {'CANCELLED'}
            inp.exec_value = True
            auto_evaluate_if_enabled(context=context)
            if not auto_eval:
                evaluate_tree(context)
            inp.exec_value = False
        else:
            node = tree.nodes.get(self.node_name)
            if not node:
                return {'CANCELLED'}
            sock = node.inputs.get(self.socket_name)
            if not sock:
                return {'CANCELLED'}
            sock.value = True
            auto_evaluate_if_enabled(context=context)
            if not auto_eval:
                evaluate_tree(context)
            sock.value = False
        return {'FINISHED'}


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
            ctx.sync_inputs(tree)
            ctx.prepare_eval_scene(context.scene)

        _active_tree = tree
        cow_engine.evaluate_tree(tree, context)
        _active_tree = None
        count += 1

    return count


def _evaluate_tree(tree, context):
    """Wrapper that delegates evaluation to the copy-on-write engine."""
    cow_engine.evaluate_tree(tree, context)


### Registration ###
def register():
    bpy.utils.register_class(FN_OT_evaluate_all)
    bpy.utils.register_class(FN_OT_group_nodes)
    bpy.utils.register_class(FN_OT_ungroup_nodes)
    bpy.utils.register_class(FN_OT_trigger_exec)
    bpy.utils.register_class(FN_OT_render_scenes)
    bpy.utils.register_class(FN_OT_new_tree)
    bpy.utils.register_class(FN_OT_remove_tree)


def unregister():
    bpy.utils.unregister_class(FN_OT_remove_tree)
    bpy.utils.unregister_class(FN_OT_new_tree)
    bpy.utils.unregister_class(FN_OT_render_scenes)
    bpy.utils.unregister_class(FN_OT_trigger_exec)
    bpy.utils.unregister_class(FN_OT_ungroup_nodes)
    bpy.utils.unregister_class(FN_OT_group_nodes)
    bpy.utils.unregister_class(FN_OT_evaluate_all)
