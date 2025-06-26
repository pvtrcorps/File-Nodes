import bpy
from bpy.types import Node
from .base import FNBaseNode


class _DummyInputs:
    def __init__(self):
        self.values = {}

    def get_input_value(self, name):
        return self.values.get(name)


class FNGroupNode(Node, FNBaseNode):
    bl_idname = "FNGroupNode"
    bl_label = "File Node Group"

    node_tree: bpy.props.PointerProperty(
        type=bpy.types.NodeTree,
        poll=lambda self, nt: getattr(nt, "bl_idname", "") == "FileNodesTreeType",
    )

    def init(self, context):
        self._sync_sockets()

    def copy(self, node):
        self._sync_sockets()

    def update(self):
        self._sync_sockets()

    def _sync_sockets(self):
        while self.inputs:
            self.inputs.remove(self.inputs[-1])
        while self.outputs:
            self.outputs.remove(self.outputs[-1])
        tree = self.node_tree
        iface = getattr(tree, "interface", None)
        if not tree or not iface:
            return
        for item in getattr(iface, "items_tree", []):
            if getattr(item, "in_out", None) == 'INPUT':
                self.inputs.new(item.socket_type, item.name)
            elif getattr(item, "in_out", None) == 'OUTPUT':
                self.outputs.new(item.socket_type, item.name)

    def _evaluate_subtree(self, context):
        tree = self.node_tree
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
                    link = sock.links[0]
                    from_sock = link.from_socket
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

        output_nodes = [n for n in tree.nodes if getattr(n, "bl_idname", "") == "FNGroupOutputNode"]
        visited = set()

        def traverse(n):
            if n in visited:
                return
            visited.add(n)
            eval_node(n)
            for s in n.inputs:
                if s.is_linked and s.links:
                    for link in s.links:
                        traverse(link.from_node)

        for n in output_nodes:
            traverse(n)

        outputs = {}
        iface = getattr(tree, "interface", None)
        if iface:
            for item in getattr(iface, "items_tree", []):
                if getattr(item, "in_out", None) != 'OUTPUT':
                    continue
                for n in output_nodes:
                    sock = n.inputs.get(item.name)
                    if sock:
                        outputs[item.name] = eval_socket(sock)
                        break
        return outputs

    def process(self, context, inputs):
        tree = self.node_tree
        if not tree:
            return {s.name: None for s in self.outputs}
        ctx = getattr(tree, "fn_inputs", None)
        if ctx is None:
            ctx = _DummyInputs()
            tree.fn_inputs = ctx
        ctx.values = inputs.copy()
        result = self._evaluate_subtree(context)
        ctx.values = {}
        return result


def register():
    bpy.utils.register_class(FNGroupNode)


def unregister():
    bpy.utils.unregister_class(FNGroupNode)
