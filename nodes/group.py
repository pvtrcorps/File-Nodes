"""Node that encapsulates a group of other nodes."""

import bpy
from bpy.types import NodeCustomGroup
from .. import operators
from ..common import LIST_TO_SINGLE
from ..cow_engine import evaluate_tree as cow_evaluate_tree
from .base import FNBaseNode


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

    def process(self, context, inputs, manager):
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
                # Register the input value with the shared manager
                data_id = manager.register_data(val)
                setattr(inp, prop, manager.get_data(data_id)) # Set the actual data, not the ID

        # Evaluate the internal node tree using the shared manager
        cow_evaluate_tree(tree, context, manager)

        # Retrieve outputs from the internal NodeGroupOutput node
        out_node = None
        for n in getattr(tree, "nodes", []):
            if getattr(n, "bl_idname", "") == "NodeGroupOutput":
                out_node = n
                break
        
        result = {}
        if out_node:
            # The outputs of the internal NodeGroupOutput are already IDs
            # from the shared manager. We just need to map them to the group's outputs.
            for s in out_node.inputs: # NodeGroupOutput's inputs are the group's outputs
                key = getattr(s, "identifier", s.name)
                # The value is already an ID from the internal evaluation
                result[key] = manager.register_data(manager.get_data(s.value)) # Re-register to get a new ID for the group's output

        return result


def register():
    bpy.utils.register_class(FNGroupNode)

def unregister():
    bpy.utils.unregister_class(FNGroupNode)