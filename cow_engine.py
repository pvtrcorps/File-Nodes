import bpy
from .common import LIST_TO_SINGLE
from .data_manager import DataManager

def _consumer_counts(tree):
    counts = {}
    # Iterate over all nodes and their output sockets
    for node in getattr(tree, "nodes", []):
        for sock in getattr(node, "outputs", []):
            # Use a stable key for the socket: (node_name, socket_name)
            socket_key = (node.name, sock.name)
            # For each output socket, count how many links originate from it
            if getattr(sock, "is_linked", False) and getattr(sock, "links", None):
                counts[socket_key] = len(sock.links)
            else:
                # If not linked, it still has one implicit consumer (the next node in the chain)
                # or zero if it's an unused output. For now, assume 1 if not explicitly linked.
                counts[socket_key] = 1 # Default to 1 if not linked, to ensure it's managed
    return counts


def evaluate_tree(tree, context, manager=None):
    if manager is None:
        manager = DataManager()
    resolved = {}
    evaluating = set()

    # Calculate consumer counts for all output sockets in the tree
    socket_consumer_counts = _consumer_counts(tree)

    output_types = {
        "FNOutputScenesNode",
        "FNRenderScenesNode",
        "NodeGroupOutput",
        "FNOutlinerNode",
    }

    def resolve_id(data_id):
        if isinstance(data_id, list):
            return [resolve_id(d) for d in data_id]
        return manager.get_data(data_id)

    def get_value_from_socket(sock):
        """Helper to get the raw value from a socket that is not linked."""
        if hasattr(sock, "value"):
            return sock.value
        return None

    def eval_socket(sock):
        print(f"eval_socket: Evaluating socket {sock.name} on node {sock.node.name}")
        if sock.is_linked and sock.links:
            single = LIST_TO_SINGLE.get(sock.bl_idname)
            
            if getattr(sock, "is_multi_input", False):
                # --- Multi-Input Socket ---
                values = []
                for link in sock.links:
                    from_sock = link.from_socket
                    print(f"eval_socket: Multi-input link from {from_sock.node.name}.{from_sock.name}")
                    outputs = eval_node(from_sock.node)
                    
                    # Get the data ID from the producing node's output
                    data_id = outputs.get(from_sock.name)
                    if data_id is None:
                        ident = getattr(from_sock, "identifier", from_sock.name)
                        data_id = outputs.get(ident)

                    if data_id is not None:
                        # Request a mutable version (CoW happens here)
                        mutable_id = manager.request_mutable_data(data_id)
                        # Only decrement if no copy was made (i.e., original ID was returned)
                        if mutable_id == data_id:
                            manager.decrement_ref_count(data_id)
                        values.append(mutable_id)
                
                # For multi-input, we return a list of IDs
                print(f"eval_socket: Multi-input returning IDs: {values}")
                return values
            else:
                # --- Single-Input Socket ---
                link = sock.links[0]
                from_sock = link.from_socket
                print(f"eval_socket: Single-input link from {from_sock.node.name}.{from_sock.name}")
                outputs = eval_node(from_sock.node)

                data_id = outputs.get(from_sock.name)
                if data_id is None:
                    ident = getattr(from_sock, "identifier", from_sock.name)
                    data_id = outputs.get(ident)

                if data_id is not None:
                    # Request a mutable version for the next node
                    if sock.is_mutable:
                        mutable_id = manager.request_mutable_data(data_id)
                        # Only decrement if the original data was not shared and no copy was made.
                        if mutable_id == data_id:
                            manager.decrement_ref_count(data_id)
                    else:
                        # For immutable sockets, we just pass the ID through without changing the ref count.
                        mutable_id = data_id
                    
                    # Handle list promotion (e.g., single item to list socket)
                    if single and from_sock.bl_idname == single:
                         print(f"eval_socket: Single-input returning list with ID: {[mutable_id]}")
                         return [mutable_id]
                    print(f"eval_socket: Single-input returning ID: {mutable_id}")
                    return mutable_id
                print("eval_socket: Single-input returning None")
                return None
        
        # --- Unlinked Socket ---
        # Get the default value and register it with the manager to get an ID
        val = get_value_from_socket(sock)
        if val is not None:
            # For unlinked sockets, assume a consumer count of 1
            data_id = manager.register_data(val, initial_refcount=1)
            print(f"eval_socket: Unlinked socket returning ID: {data_id} for value {val}")
            return data_id
        print("eval_socket: Unlinked socket returning None")
        return None

    def eval_node(node):
        print(f"eval_node: Evaluating node {node.name} ({node.bl_idname})")
        if node in resolved:
            print(f"eval_node: Node {node.name} already resolved. Returning {resolved[node]}")
            return resolved[node]
        if node in evaluating:
            # Circular dependency detected
            print(f"eval_node: Circular dependency detected for node {node.name}")
            return {s.name: None for s in node.outputs}

        evaluating.add(node)
        print(f"eval_node: Added {node.name} to evaluating set.")

        # Special handling for Group Inputs
        if getattr(node, "bl_idname", "") == "NodeGroupInput":
            print(f"eval_node: Processing NodeGroupInput {node.name}")
            outputs = {}
            ctx = getattr(node.id_data, "fn_inputs", None)
            for s in node.outputs:
                key = getattr(s, "identifier", s.name)
                val = ctx.get_input_value(s.name) if ctx else None
                # Register the input value to get an ID with its consumer count
                count = socket_consumer_counts.get((node.name, s.name), 1) # Use stable key
                data_id = manager.register_data(val, initial_refcount=count)
                outputs[key] = data_id
                if key != s.name:
                    outputs.setdefault(s.name, data_id)
            resolved[node] = outputs
            evaluating.discard(node)
            print(f"eval_node: NodeGroupInput {node.name} resolved. Returning {outputs}")
            return outputs

        # Special handling for NodeGroupOutput (the output node of a group)
        if getattr(node, "bl_idname", "") == "NodeGroupOutput":
            print(f"eval_node: Processing NodeGroupOutput {node.name}")
            outputs = {}
            for s in node.inputs: # Iterate over inputs of NodeGroupOutput
                key = getattr(s, "identifier", s.name)
                val_id = eval_socket(s) # Evaluate the socket connected to this input
                outputs[key] = val_id
                if key != s.name:
                    outputs.setdefault(s.name, val_id)
            resolved[node] = outputs
            evaluating.discard(node)
            print(f"eval_node: NodeGroupOutput {node.name} resolved. Returning {outputs}")
            return outputs

        raw_inputs = {s.name: eval_socket(s) for s in node.inputs}
        proc_inputs = {k: resolve_id(v) for k, v in raw_inputs.items()}
        print(f"eval_node: Inputs for {node.name} (Data): {proc_inputs}")
        
        # 3. Process the data
        outputs_data = {}
        if hasattr(node, "process"):
            print(f"eval_node: Calling process for {node.name}")
            outputs_data = node.process(context, proc_inputs, manager) or {}
            print(f"eval_node: Processed outputs for {node.name} (Data): {outputs_data}")

        # 4. Register the output data with the manager
        # This is the "wrapping" step
        wrapped_outputs = {}
        for s in node.outputs:
            key = getattr(s, "identifier", s.name)
            val = outputs_data.get(key)
            
            # Register the data and get a new ID
            count = socket_consumer_counts.get((node.name, s.name), 1) # Use stable key
            data_id = manager.register_data(val, initial_refcount=count)
            wrapped_outputs[key] = data_id
            
            # Also handle the 'name' key if identifier is different
            if key != s.name:
                wrapped_outputs.setdefault(s.name, data_id)
        resolved[node] = wrapped_outputs
        evaluating.discard(node)
        print(f"eval_node: Node {node.name} resolved. Returning IDs: {wrapped_outputs}")
        return wrapped_outputs

    # --- Main Evaluation Logic ---
    try:
        print("evaluate_tree: Starting main evaluation logic.")
        # Traverse the tree from output nodes
        visited = set()
        def traverse(node):
            if node in visited:
                return
            visited.add(node)
            print(f"traverse: Visiting node {node.name}")
            # Ensure dependencies are evaluated first
            for sock in node.inputs:
                if sock.is_linked and sock.links:
                    for link in sock.links:
                        traverse(link.from_node)
            eval_node(node)

        for node in tree.nodes:
            if node.bl_idname in output_types:
                print(f"evaluate_tree: Found output node {node.name}")
                traverse(node)

        # Handle final outputs for scenes to keep
        ctx = getattr(tree, "fn_inputs", None)
        if ctx:
            print("evaluate_tree: Processing fn_inputs context.")
            # ctx.scenes_to_keep is now a CollectionProperty, so we don't need to check for None
            for node in tree.nodes:
                if getattr(node, "bl_idname", "") == "NodeGroupOutput":
                    print(f"evaluate_tree: Processing NodeGroupOutput {node.name}")
                    for sock in getattr(node, "inputs", []):
                        stype = getattr(sock, "bl_idname", "")
                        if stype not in {"FNSocketScene", "FNSocketSceneList"}:
                            continue
                        
                        value_id = eval_socket(sock)
                        if value_id is None:
                            print(f"evaluate_tree: NodeGroupOutput socket {sock.name} has no value ID.")
                            continue

                        # Resolve the final data
                        value_data = manager.get_data(value_id)
                        print(f"evaluate_tree: NodeGroupOutput socket {sock.name} resolved to data: {value_data}")
                        
                        if stype in LIST_TO_SINGLE:
                            scenes = value_data or []
                        else:
                            scenes = [value_data] if value_data is not None else []
                        
                        for sc_data in scenes:
                            if sc_data:
                                # Add scene to the collection
                                new_ref = ctx.scenes_to_keep.add()
                                new_ref.scene = sc_data
                                print(f"evaluate_tree: Added scene {sc_data.name} to scenes_to_keep.")
    finally:
        # Crucial step: Clean up all the created copies
        
        manager.cleanup()