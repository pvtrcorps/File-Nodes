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
        count, kept_scenes = evaluate_tree(context)
        scene_names = ", ".join([s.name for s in kept_scenes]) if kept_scenes else "None"
        self.report({"INFO"}, f"Evaluated {count} File Node trees. Kept scenes: {scene_names}")
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

        # Set the exec value to true to trigger the render in the process method
        node.inputs.get("Exec").value = True

        # Run a full evaluation
        evaluate_tree(context)

        # Reset the exec value
        node.inputs.get("Exec").value = False

        return {"FINISHED"}


class FN_OT_execute_input(Operator):
    bl_idname = "file_nodes.execute_input"
    bl_label = "Execute"

    def execute(self, context):
        node = context.active_node
        if (
            not isinstance(node, bpy.types.Node)
            or node.bl_idname != "FNExecInputNode"
        ):
            return {"CANCELLED"}

        node.outputs.get("Exec").value = True
        evaluate_tree(context)
        node.outputs.get("Exec").value = False

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
    from .data_manager import DataManager # Import DataManager here
    manager = DataManager() # Instantiate DataManager
    all_kept_scenes = [] # New list to collect all kept scenes

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
        cow_engine.evaluate_tree(tree, context, manager)
        _active_tree = None

        if ctx:
            # Add scenes from this tree's ctx to the overall list
            if ctx.scenes_to_keep:
                for scene_ref in ctx.scenes_to_keep:
                    if scene_ref.scene:
                        all_kept_scenes.append(scene_ref.scene)

            keep = set(sr.scene for sr in ctx.scenes_to_keep if sr.scene)
            if ctx.eval_scene:
                keep.add(ctx.eval_scene)
            for sc in list(bpy.data.scenes):
                if sc not in keep and getattr(sc, "use_extra_user", False):
                    bpy.data.scenes.remove(sc)

        count += 1

    return count, all_kept_scenes





### Registration ###
def register():
    bpy.utils.register_class(FN_OT_evaluate_all)
    bpy.utils.register_class(FN_OT_group_nodes)
    bpy.utils.register_class(FN_OT_ungroup_nodes)
    bpy.utils.register_class(FN_OT_trigger_exec)
    bpy.utils.register_class(FN_OT_render_scenes)
    bpy.utils.register_class(FN_OT_execute_input)
    bpy.utils.register_class(FN_OT_new_tree)
    bpy.utils.register_class(FN_OT_remove_tree)


def unregister():
    bpy.utils.unregister_class(FN_OT_remove_tree)
    bpy.utils.unregister_class(FN_OT_new_tree)
    bpy.utils.unregister_class(FN_OT_render_scenes)
    bpy.utils.unregister_class(FN_OT_execute_input)
    bpy.utils.unregister_class(FN_OT_trigger_exec)
    bpy.utils.unregister_class(FN_OT_ungroup_nodes)
    bpy.utils.unregister_class(FN_OT_group_nodes)
    bpy.utils.unregister_class(FN_OT_evaluate_all)
