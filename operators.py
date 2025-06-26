import bpy
from bpy.types import Operator
from . import ADDON_NAME

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


class FN_OT_group_make(Operator):
    bl_idname = "file_nodes.group_make"
    bl_label = "Make File Nodes Group"

    @classmethod
    def poll(cls, context):
        tree = getattr(getattr(context, "space_data", None), "edit_tree", None)
        if not tree or getattr(tree, "bl_idname", "") != "FileNodesTreeType":
            return False
        return any(getattr(n, "select", False) for n in getattr(tree, "nodes", []))

    def execute(self, context):
        from .tree import FileNodesTree, FileNodesTreeInputs
        from .nodes.group_input import FNGroupInputNode
        from .nodes.group_output import FNGroupOutputNode
        from .nodes.group_node import FNGroupNode

        space = context.space_data
        tree = space.edit_tree
        selected = [n for n in tree.nodes if getattr(n, "select", False)]
        if not selected:
            return {"CANCELLED"}

        new_tree = FileNodesTree.__new__(FileNodesTree)
        new_tree.nodes = []
        new_tree.links = type(tree.links)()
        new_tree.interface = type("Iface", (), {
            "items_tree": [],
            "new_socket": lambda self, **kw: self.items_tree.append(type("I", (), kw)()) or self.items_tree[-1],
        })()
        new_tree.fn_inputs = FileNodesTreeInputs.__new__(FileNodesTreeInputs)

        gi = FNGroupInputNode.__new__(FNGroupInputNode)
        gi.id_data = new_tree
        gi.inputs = type(tree.nodes[0].inputs)(gi)
        gi.outputs = type(tree.nodes[0].outputs)(gi)
        gi.init(None)

        go = FNGroupOutputNode.__new__(FNGroupOutputNode)
        go.id_data = new_tree
        go.inputs = type(tree.nodes[0].inputs)(go)
        go.outputs = type(tree.nodes[0].outputs)(go)
        go.init(None)

        new_tree.nodes.extend([gi, go])

        group_node = FNGroupNode.__new__(FNGroupNode)
        group_node.id_data = tree
        group_node.inputs = type(tree.nodes[0].inputs)(group_node)
        group_node.outputs = type(tree.nodes[0].outputs)(group_node)
        group_node.node_tree = new_tree
        group_node.init(None)

        tree.nodes.append(group_node)

        for n in selected:
            tree.nodes.remove(n)
            n.id_data = new_tree
            new_tree.nodes.append(n)

        for link in list(tree.links):
            if link.from_node in selected and link.to_node in selected:
                tree.links.remove(link)
                new_tree.links.append(link)
            elif link.to_node in selected and link.from_node not in selected:
                tree.links.remove(link)
                iface_item = new_tree.interface.new_socket(name=link.to_socket.name, in_out='INPUT', socket_type=link.from_socket.bl_idname)
                in_sock = group_node.inputs.new(link.from_socket.bl_idname, iface_item.name)
                gi_sock = gi.outputs.new(link.from_socket.bl_idname, iface_item.name)
                new_tree.links.new(gi_sock, link.to_socket)
                tree.links.new(link.from_socket, in_sock)
            elif link.from_node in selected and link.to_node not in selected:
                tree.links.remove(link)
                iface_item = new_tree.interface.new_socket(name=link.from_socket.name, in_out='OUTPUT', socket_type=link.from_socket.bl_idname)
                out_sock = group_node.outputs.new(link.from_socket.bl_idname, iface_item.name)
                go_sock = go.inputs.new(link.from_socket.bl_idname, iface_item.name)
                new_tree.links.new(link.from_socket, go_sock)
                tree.links.new(out_sock, link.to_socket)

        return {"FINISHED"}


class FN_OT_group_ungroup(Operator):
    bl_idname = "file_nodes.group_ungroup"
    bl_label = "Ungroup File Nodes"

    @classmethod
    def poll(cls, context):
        tree = getattr(getattr(context, "space_data", None), "edit_tree", None)
        if not tree or getattr(tree, "bl_idname", "") != "FileNodesTreeType":
            return False
        groups = [n for n in getattr(tree, "nodes", []) if getattr(n, "select", False) and n.bl_idname == "FNGroupNode"]
        return len(groups) == 1

    def execute(self, context):
        from .nodes.group_input import FNGroupInputNode
        from .nodes.group_output import FNGroupOutputNode

        tree = context.space_data.edit_tree
        group_node = next(n for n in tree.nodes if getattr(n, "select", False))
        sub = group_node.node_tree
        gi = next((n for n in sub.nodes if n.bl_idname == "FNGroupInputNode"), None)
        go = next((n for n in sub.nodes if n.bl_idname == "FNGroupOutputNode"), None)
        inner = [n for n in sub.nodes if n not in (gi, go)]

        for n in inner:
            sub.nodes.remove(n)
            n.id_data = tree
            tree.nodes.append(n)

        for link in list(sub.links):
            if link.from_node in inner and link.to_node in inner:
                sub.links.remove(link)
                tree.links.append(link)

        for link in list(tree.links):
            if link.to_node == group_node:
                name = link.to_socket.name
                target_link = next((l for l in sub.links if l.from_node == gi and l.from_socket.name == name), None)
                if target_link:
                    tree.links.new(link.from_socket, target_link.to_socket)
                tree.links.remove(link)
            elif link.from_node == group_node:
                name = link.from_socket.name
                target_link = next((l for l in sub.links if l.to_node == go and l.to_socket.name == name), None)
                if target_link:
                    tree.links.new(target_link.from_socket, link.to_socket)
                tree.links.remove(link)

        tree.nodes.remove(group_node)

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

        _list_to_single = {
            "FNSocketSceneList": "FNSocketScene",
            "FNSocketObjectList": "FNSocketObject",
            "FNSocketCollectionList": "FNSocketCollection",
            "FNSocketWorldList": "FNSocketWorld",
            "FNSocketCameraList": "FNSocketCamera",
            "FNSocketImageList": "FNSocketImage",
            "FNSocketLightList": "FNSocketLight",
            "FNSocketMaterialList": "FNSocketMaterial",
            "FNSocketMeshList": "FNSocketMesh",
            "FNSocketNodeTreeList": "FNSocketNodeTree",
            "FNSocketStringList": "FNSocketString",
            "FNSocketTextList": "FNSocketText",
            "FNSocketWorkSpaceList": "FNSocketWorkSpace",
        }

        def eval_socket(sock):
            if sock.is_linked and sock.links:
                from_sock = sock.links[0].from_socket
                value = eval_node(from_sock.node)[from_sock.name]
                single = _list_to_single.get(sock.bl_idname)
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
                outputs.setdefault(s.name, None)
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
    if prefs and prefs.preferences.auto_evaluate:
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
            ctx.scenes_to_keep = []
            ctx.reset_to_originals()
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
        "FNSocketSceneList": "FNSocketScene",
        "FNSocketObjectList": "FNSocketObject",
        "FNSocketCollectionList": "FNSocketCollection",
        "FNSocketWorldList": "FNSocketWorld",
        "FNSocketCameraList": "FNSocketCamera",
        "FNSocketImageList": "FNSocketImage",
        "FNSocketLightList": "FNSocketLight",
        "FNSocketMaterialList": "FNSocketMaterial",
        "FNSocketMeshList": "FNSocketMesh",
        "FNSocketNodeTreeList": "FNSocketNodeTree",
        "FNSocketStringList": "FNSocketString",
        "FNSocketTextList": "FNSocketText",
        "FNSocketWorkSpaceList": "FNSocketWorkSpace",
    }

    output_types = {
        "FNOutputScenesNode",
        "FNRenderScenesNode",
        "FNGroupOutputNode",
    }

    def eval_socket(sock):
        if sock.is_linked and sock.links:
            single = _list_to_single.get(sock.bl_idname)
            if getattr(sock, "is_multi_input", False):
                values = []
                for link in sock.links:
                    from_sock = link.from_socket
                    value = eval_node(from_sock.node)[from_sock.name]
                    if single and from_sock.bl_idname == single:
                        if value is not None:
                            values.append(value)
                    else:
                        values.append(value)
                return values
            else:
                from_sock = sock.links[0].from_socket
                value = eval_node(from_sock.node)[from_sock.name]
                if single and from_sock.bl_idname == single:
                    return [value] if value is not None else []
                return value
        if hasattr(sock, "value"):
            return sock.value
        return None

    def eval_node(node):
        if node in resolved:
            return resolved[node]

        inputs = {s.name: eval_socket(s) for s in node.inputs}
        outputs = {}
        if hasattr(node, "process"):
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
                for link in sock.links:
                    from_node = link.from_node
                    traverse(from_node)

    for node in tree.nodes:
        if node.bl_idname in output_types:
            traverse(node)


### Registration ###
def register():
    bpy.utils.register_class(FN_OT_evaluate_all)
    bpy.utils.register_class(FN_OT_group_make)
    bpy.utils.register_class(FN_OT_group_ungroup)
    bpy.utils.register_class(FN_OT_render_scenes)
    bpy.utils.register_class(FN_OT_new_tree)
    bpy.utils.register_class(FN_OT_remove_tree)


def unregister():
    bpy.utils.unregister_class(FN_OT_remove_tree)
    bpy.utils.unregister_class(FN_OT_new_tree)
    bpy.utils.unregister_class(FN_OT_render_scenes)
    bpy.utils.unregister_class(FN_OT_group_ungroup)
    bpy.utils.unregister_class(FN_OT_group_make)
    bpy.utils.unregister_class(FN_OT_evaluate_all)
