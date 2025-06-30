import bpy
from .common import LIST_TO_SINGLE

class DataProxy:
    """Wrapper for Blender datablocks implementing copy-on-write semantics."""
    def __init__(self, data, refcount=1):
        object.__setattr__(self, "_data", data)
        object.__setattr__(self, "refcount", refcount)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        object.__setattr__(self, "_data", value)

    @property
    def __class__(self):  # behave like underlying data for isinstance checks
        return self._data.__class__

    def __getattr__(self, name):
        return getattr(self._data, name)

    def __setattr__(self, name, value):
        if name in {"_data", "refcount"}:
            object.__setattr__(self, name, value)
        elif name == "data":
            object.__setattr__(self, "_data", value)
        else:
            ensure_mutable(self)
            setattr(self._data, name, value)

    def __bool__(self):
        return bool(self._data)

    def copy(self):
        """Duplicate the underlying datablock."""
        d = self._data
        try:
            return d.copy()
        except Exception:
            try:
                return type(d)(getattr(d, "name", ""))
            except Exception:
                return d

    def clone(self):
        """Return a new proxy with a duplicate of the data."""
        return DataProxy(self.copy(), refcount=self.refcount)


def ensure_mutable(proxy):
    """Ensure the proxy contains a unique copy before modification."""
    if isinstance(proxy, DataProxy) and proxy.refcount > 1:
        new_data = proxy.copy()
        proxy.refcount -= 1
        proxy.data = new_data
    if isinstance(proxy, DataProxy):
        return proxy.data
    return proxy


def _is_datablock(value):
    return hasattr(value, "as_pointer")


def _wrap(value, count):
    if isinstance(value, list):
        return [_wrap(v, count) for v in value]
    if _is_datablock(value):
        return DataProxy(value, refcount=count)
    return value


def _clone(value):
    if isinstance(value, list):
        return [_clone(v) for v in value]
    if isinstance(value, DataProxy):
        if value.refcount > 1:
            value.refcount -= 1
            return DataProxy(value.copy(), refcount=1)
        return value
    return value


def _unwrap(value):
    if isinstance(value, DataProxy):
        ensure_mutable(value)
        return value.data
    if isinstance(value, list):
        return [_unwrap(v) for v in value]
    return value


def _consumer_counts(tree):
    counts = {}
    links = getattr(tree, "links", None)
    if links:
        for link in links:
            out = link.from_socket
            counts[out] = counts.get(out, 0) + 1
    else:
        for node in getattr(tree, "nodes", []):
            for sock in getattr(node, "inputs", []):
                if getattr(sock, "is_linked", False) and getattr(sock, "links", None):
                    for link in sock.links:
                        out = link.from_socket
                        counts[out] = counts.get(out, 0) + 1
    return counts


def evaluate_tree(tree, context):
    counts = _consumer_counts(tree)
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
                    value = _clone(value)
                    if isinstance(value, DataProxy):
                        ensure_mutable(value)
                    if single and from_sock.bl_idname == single:
                        if value is not None:
                            values.append(value)
                    else:
                        values.append(value)
                return values
            else:
                link = sock.links[0]
                from_sock = link.from_socket
                outputs = eval_node(from_sock.node)
                value = outputs.get(from_sock.name)
                if value is None:
                    ident = getattr(from_sock, "identifier", from_sock.name)
                    value = outputs.get(ident)
                value = _clone(value)
                if isinstance(value, DataProxy):
                    ensure_mutable(value)
                if single and from_sock.bl_idname == single:
                    return [value] if value is not None else []
                return value
        if hasattr(sock, "value"):
            val = _clone(sock.value)
            if isinstance(val, DataProxy):
                ensure_mutable(val)
            return val
        return None

    def eval_node(node):
        if node in resolved:
            return resolved[node]
        if node in evaluating:
            return resolved.setdefault(node, {s.name: None for s in node.outputs})

        evaluating.add(node)

        if getattr(node, "bl_idname", "") == "NodeGroupInput":
            outputs = {}
            ctx = getattr(node.id_data, "fn_inputs", None)
            for s in node.outputs:
                key = getattr(s, "identifier", s.name)
                val = ctx.get_input_value(s.name) if ctx else None
                outputs[key] = val
                if key != s.name:
                    outputs.setdefault(s.name, val)
            resolved[node] = outputs
            evaluating.discard(node)
            return outputs

        raw_inputs = {s.name: eval_socket(s) for s in node.inputs}
        proc_inputs = {k: _unwrap(v) for k, v in raw_inputs.items()}
        outputs = {}
        if hasattr(node, "process"):
            outputs = node.process(context, proc_inputs) or {}
        wrapped = {}
        for s in node.outputs:
            key = getattr(s, "identifier", s.name)
            val = outputs.get(key)
            wrapped_val = _wrap(val, counts.get(s, 0))
            wrapped[key] = wrapped_val
            if key != s.name:
                wrapped.setdefault(s.name, wrapped_val)
        resolved[node] = wrapped
        evaluating.discard(node)
        return wrapped

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

    for node in tree.nodes:
        if node.bl_idname in output_types:
            traverse(node)

    ctx = getattr(tree, "fn_inputs", None)
    if ctx:
        if getattr(ctx, "scenes_to_keep", None) is None:
            ctx.scenes_to_keep = []
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
                        sc_data = _unwrap(sc)
                        if sc_data:
                            ctx.scenes_to_keep.append(sc_data)

