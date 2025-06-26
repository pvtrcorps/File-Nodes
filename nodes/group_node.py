import bpy
from bpy.types import NodeCustomGroup

from .group_input import FNGroupInputNode
from .group_output import FNGroupOutputNode
from ..tree import FileNodesTree


class FNGroupNode(NodeCustomGroup):
    bl_idname = "FNGroupNode"
    bl_label = "File Nodes Group"

    node_tree: bpy.props.PointerProperty(type=FileNodesTree)

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        if not self.node_tree:
            self.node_tree = bpy.data.node_groups.new("File Nodes Group", "FileNodesTreeType")
            self.node_tree.nodes.new("FNGroupInputNode")
            self.node_tree.nodes.new("FNGroupOutputNode")
        self._sync_sockets()

    def update(self):
        self._sync_sockets()

    def _sync_sockets(self):
        tree = self.node_tree
        iface = getattr(tree, "interface", None)
        if not tree or not iface:
            return
        ins = [i for i in iface.items_tree if getattr(i, "in_out", None) == 'INPUT']
        outs = [i for i in iface.items_tree if getattr(i, "in_out", None) == 'OUTPUT']
        in_names = [i.name for i in ins]
        out_names = [i.name for i in outs]
        for s in list(self.inputs):
            if s.name not in in_names:
                self.inputs.remove(s)
        for s in list(self.outputs):
            if s.name not in out_names:
                self.outputs.remove(s)
        for item in ins:
            sock = self.inputs.get(item.name)
            if sock is None:
                sock = self.inputs.new(item.socket_type, item.name)
            elif sock.bl_idname != item.socket_type:
                self.inputs.remove(sock)
                sock = self.inputs.new(item.socket_type, item.name)
            sock.name = item.name
        for item in outs:
            sock = self.outputs.get(item.name)
            if sock is None:
                sock = self.outputs.new(item.socket_type, item.name)
            elif sock.bl_idname != item.socket_type:
                self.outputs.remove(sock)
                sock = self.outputs.new(item.socket_type, item.name)
            sock.name = item.name

    def process(self, context, inputs):
        tree = self.node_tree
        if not tree:
            return {}
        iface = getattr(tree, "interface", None)
        ctx = getattr(tree, "fn_inputs", None)
        if iface and ctx:
            ctx.sync_inputs(tree)
            for item in iface.items_tree:
                if item.in_out == 'INPUT':
                    inp = ctx.inputs.get(item.name)
                    if inp:
                        prop = inp.prop_name()
                        if prop:
                            setattr(inp, prop, inputs.get(item.name))

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
            inputs_map = {s.name: eval_socket(s) for s in node.inputs}
            outputs_map = {}
            if hasattr(node, "process"):
                outputs_map = node.process(context, inputs_map) or {}
            for s in node.outputs:
                outputs_map.setdefault(s.name, None)
            resolved[node] = outputs_map
            return outputs_map

        visited = set()

        def traverse(node):
            if node in visited:
                return
            visited.add(node)
            eval_node(node)
            for sock in node.inputs:
                if sock.is_linked and sock.links:
                    for link in sock.links:
                        traverse(link.from_node)

        output_nodes = [n for n in tree.nodes if n.bl_idname == "FNGroupOutputNode"]
        for n in output_nodes:
            traverse(n)

        outputs = {}
        if iface and output_nodes:
            out_node = output_nodes[0]
            for item in iface.items_tree:
                if item.in_out == 'OUTPUT':
                    sock = out_node.inputs.get(item.name)
                    outputs[item.name] = eval_socket(sock) if sock else None
        return outputs


def register():
    bpy.utils.register_class(FNGroupNode)


def unregister():
    bpy.utils.unregister_class(FNGroupNode)
