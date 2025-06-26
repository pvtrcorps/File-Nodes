import bpy
from bpy.types import Node

from .base import FNBaseNode
from .. import operators


class FNGroupInstanceNode(Node, FNBaseNode):
    bl_idname = "FNGroupInstanceNode"
    bl_label = "Group Instance"

    def _tree_poll(self, tree):
        return getattr(tree, "bl_idname", None) == "FileNodesTreeType"

    def _tree_update(self, context):
        self._sync_sockets()
        operators.auto_evaluate_if_enabled(context)

    node_tree: bpy.props.PointerProperty(
        type=bpy.types.NodeTree,
        poll=_tree_poll,
        update=_tree_update,
    )

    def init(self, context):
        self._sync_sockets()

    def _sync_sockets(self):
        while self.inputs:
            self.inputs.remove(self.inputs[-1])
        while self.outputs:
            self.outputs.remove(self.outputs[-1])
        tree = getattr(self, "node_tree", None)
        iface = getattr(tree, "interface", None)
        if not tree or not iface:
            return
        for item in iface.items_tree:
            if getattr(item, "in_out", None) == "INPUT":
                self.inputs.new(item.socket_type, item.name)
            elif getattr(item, "in_out", None) == "OUTPUT":
                self.outputs.new(item.socket_type, item.name)

    def process(self, context, inputs):
        tree = self.node_tree
        if not tree:
            return {sock.name: None for sock in self.outputs}
        ctx = getattr(tree, "fn_inputs", None)
        if ctx:
            ctx.sync_inputs(tree)
            ctx.prepare_eval_scene(getattr(context, "scene", None))
            for inp in ctx.inputs:
                val = inputs.get(inp.name)
                prop = getattr(inp, "prop_name", lambda: "value")()
                setattr(inp, prop, val)
        operators._evaluate_tree(tree, context)

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
            if not sock:
                return None
            if sock.is_linked and getattr(sock, "links", None):
                single = _list_to_single.get(sock.bl_idname)
                if getattr(sock, "is_multi_input", False):
                    values = []
                    for link in sock.links:
                        from_sock = link.from_socket
                        val = eval_node(from_sock.node)[from_sock.name]
                        if single and from_sock.bl_idname == single:
                            if val is not None:
                                values.append(val)
                        else:
                            values.append(val)
                    return values
                else:
                    link = sock.links[0]
                    val = eval_node(link.from_node)[link.from_socket.name]
                    if single and link.from_socket.bl_idname == single:
                        return [val] if val is not None else []
                    return val
            if hasattr(sock, "value"):
                return sock.value
            return None

        def eval_node(node):
            if node in resolved:
                return resolved[node]
            node_inputs = {s.name: eval_socket(s) for s in node.inputs}
            node_outputs = {}
            if hasattr(node, "process"):
                node_outputs = node.process(context, node_inputs) or {}
            for s in node.outputs:
                node_outputs.setdefault(s.name, None)
            resolved[node] = node_outputs
            return node_outputs

        # pick first group output node
        out_node = None
        for n in getattr(tree, "nodes", []):
            if getattr(n, "bl_idname", "") == "FNGroupOutputNode":
                out_node = n
                break
        result = {}
        iface = getattr(tree, "interface", None)
        if out_node and iface:
            for item in iface.items_tree:
                if getattr(item, "in_out", None) == "OUTPUT":
                    sock = next((s for s in out_node.inputs if s.name == item.name), None)
                    result[item.name] = eval_socket(sock)
        for s in self.outputs:
            result.setdefault(s.name, None)
        return result


def register():
    bpy.utils.register_class(FNGroupInstanceNode)


def unregister():
    bpy.utils.unregister_class(FNGroupInstanceNode)
