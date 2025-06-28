"""Node that encapsulates a group of other nodes."""

import bpy
from bpy.types import NodeCustomGroup
from .base import FNBaseNode
from .. import operators
from ..common import LIST_TO_SINGLE


class FNGroupNode(NodeCustomGroup, FNBaseNode):
    """Execute an embedded node group and output its results."""
    bl_idname = "FNGroupNode"
    bl_label = "Group"
    bl_icon = 'NODETREE'

    @classmethod
    def poll(cls, ntree):
        return getattr(ntree, "bl_idname", None) == "FileNodesTreeType"

    def init(self, context):
        if not self.node_tree:
            self.node_tree = bpy.data.node_groups.new("Group", "FileNodesTreeType")
        self._sync_sockets()
        self._cached_tree = self.node_tree

    def copy(self, node):
        self._sync_sockets()
        self._cached_tree = self.node_tree

    def update(self):
        tree_changed = getattr(self, "_cached_tree", None) is not self.node_tree
        sockets_changed = self._sync_sockets()
        if tree_changed or sockets_changed:
            operators.auto_evaluate_if_enabled(context=bpy.context)
        self._cached_tree = self.node_tree

    def _sync_sockets(self):
        prev = [(s.name, s.bl_idname) for s in self.inputs] + [
            (s.name, s.bl_idname) for s in self.outputs
        ]

        tree = getattr(self, "node_tree", None)
        iface = getattr(tree, "interface", None)
        if not tree or not iface:
            while self.inputs:
                self.inputs.remove(self.inputs[-1])
            while self.outputs:
                self.outputs.remove(self.outputs[-1])
            changed = prev != []
            self._socket_hash = []
            return changed
        iface_inputs = [i for i in iface.items_tree if getattr(i, "in_out", None) == 'INPUT']
        iface_outputs = [i for i in iface.items_tree if getattr(i, "in_out", None) == 'OUTPUT']
        names_in = [i.name for i in iface_inputs]
        names_out = [i.name for i in iface_outputs]
        for sock in list(self.inputs):
            if sock.name not in names_in:
                self.inputs.remove(sock)
        for sock in list(self.outputs):
            if sock.name not in names_out:
                self.outputs.remove(sock)
        for item in iface_inputs:
            sock = self.inputs.get(item.name)
            if sock is None or sock.bl_idname != item.socket_type:
                if sock:
                    self.inputs.remove(sock)
                sock = self.inputs.new(item.socket_type, item.name)
            sock.name = item.name
        for item in iface_outputs:
            sock = self.outputs.get(item.name)
            if sock is None or sock.bl_idname != item.socket_type:
                if sock:
                    self.outputs.remove(sock)
                sock = self.outputs.new(item.socket_type, item.name)
            sock.name = item.name

        new = [(s.name, s.bl_idname) for s in self.inputs] + [
            (s.name, s.bl_idname) for s in self.outputs
        ]
        changed = prev != new
        self._socket_hash = new
        return changed

    def process(self, context, inputs):
        tree = self.node_tree
        if not tree:
            return {s.name: None for s in self.outputs}

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

        def eval_socket(sock):
            if not sock:
                return None
            if sock.is_linked and getattr(sock, "links", None):
                single = LIST_TO_SINGLE.get(sock.bl_idname)
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
            if getattr(node, "bl_idname", "") == "NodeGroupInput":
                node_outputs = {s.name: inputs.get(s.name) for s in node.outputs}
            else:
                node_inputs = {s.name: eval_socket(s) for s in node.inputs}
                node_outputs = {}
                if hasattr(node, "process"):
                    node_outputs = node.process(context, node_inputs) or {}
            for s in node.outputs:
                node_outputs.setdefault(s.name, None)
            resolved[node] = node_outputs
            return node_outputs

        out_node = None
        for n in getattr(tree, "nodes", []):
            if getattr(n, "bl_idname", "") in {"NodeGroupOutput", "FNGroupOutputNode"}:
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
    bpy.utils.register_class(FNGroupNode)

def unregister():
    bpy.utils.unregister_class(FNGroupNode)
