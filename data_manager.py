import bpy
import uuid

class DataManager:
    """
    Manages the lifecycle of datablocks for the node tree evaluation.
    This system replaces the implicit CoW proxy system with an explicit,
    centralized manager.
    """
    def __init__(self):
        # Stores the actual datablock data, keyed by a unique ID.
        self._data_store = {}
        # Stores the reference count for each datablock ID.
        self._ref_counts = {}
        # A set to track which IDs correspond to copies created by the manager.
        self._owned_copies = set()
        print("DataManager: Initialized")

    def register_data(self, data, initial_refcount=1):
        """
        Registers a new datablock with the manager and returns its unique ID.
        'initial_refcount' specifies the initial number of consumers for this data.
        """
        # Check if this exact data object is already managed
        for existing_id, existing_data in self._data_store.items():
            if existing_data is data: # Use 'is' for identity check
                # If already managed, SET its refcount to the new initial_refcount
                # This handles cases where a datablock is modified in-place and then re-outputted.
                self._ref_counts[existing_id] = initial_refcount
                print(f"DataManager: Re-registered existing data {data} with ID {existing_id}. Set refcount to: {self._ref_counts[existing_id]}")
                return existing_id

        new_id = str(uuid.uuid4())
        self._data_store[new_id] = data
        self._ref_counts[new_id] = initial_refcount
        print(f"DataManager: Registered new data {data} with ID {new_id} (initial refcount: {initial_refcount})")
        return new_id

    def get_data(self, data_id):
        """Retrieves the datablock associated with a given ID."""
        data = self._data_store.get(data_id)
        print(f"DataManager: Retrieved data for ID {data_id}: {data}")
        return data

    def decrement_ref_count(self, data_id):
        """Decrements the reference count for a given data ID."""
        if data_id in self._ref_counts:
            self._ref_counts[data_id] -= 1
            print(f"DataManager: Decremented refcount for ID {data_id} to {self._ref_counts[data_id]}")
            if self._ref_counts[data_id] < 0:
                print(f"DataManager: WARNING: Refcount for ID {data_id} went negative!")

    def request_mutable_data(self, data_id):
        """
        Requests a mutable version of a datablock.
        If the data is shared (ref_count > 1), it creates a copy and returns
        a new ID for the copy. Otherwise, it returns the original ID.
        """
        if data_id not in self._ref_counts:
            print(f"DataManager: ID {data_id} not managed. Returning original.")
            return data_id # Not a managed datablock

        if self._ref_counts[data_id] > 1:
            # It's shared, so we need to copy it.
            original_data = self._data_store[data_id]
            print(f"DataManager: Requesting mutable copy for ID {data_id} (refcount: {self._ref_counts[data_id]}). Original data: {original_data}")
            
            # Attempt to copy the datablock
            try:
                new_data = original_data.copy()
                print(f"DataManager: Created copy: {new_data}")
            except AttributeError: # Not a Blender datablock, maybe a list or other type
                new_data = original_data
                print(f"DataManager: Data is not copyable, using original: {new_data}")
            
            # Register the new copy with an initial refcount of 1 (it's a new, unique instance)
            new_id = self.register_data(new_data, initial_refcount=1)
            
            # Mark it as a copy owned by the manager for later cleanup
            if hasattr(new_data, "as_pointer"):
                self._owned_copies.add(new_id)
                print(f"DataManager: Marked new ID {new_id} as owned copy.")

            # Decrement the ref count of the original data, as one consumer is now using the copy
            self.decrement_ref_count(data_id)
            
            return new_id
        
        # Not shared, safe to mutate directly.
        print(f"DataManager: ID {data_id} is unique (refcount: {self._ref_counts[data_id]}). Returning original ID.")
        return data_id

    def cleanup(self):
        """
        Removes all datablock copies created by the manager during evaluation.
        This is the explicit garbage collection step.
        """
        print("DataManager: Starting cleanup...")
        for data_id in list(self._owned_copies): # Iterate over a copy to allow modification
            data = self._data_store.get(data_id)
            
            # IMPORTANT: Do not remove if it's a scene with use_extra_user set
            if isinstance(data, bpy.types.Scene) and getattr(data, "use_extra_user", False):
                print(f"DataManager: Not cleaning up scene {data.name} with use_extra_user set.")
                continue

            if data and hasattr(data, "as_pointer") and data.users == 0:
                data_name = data.name # Store name before removal
                print(f"DataManager: Cleaning up data {data_name} with ID {data_id} (users: {data.users})")
                try:
                    # Check the correct bpy.data collection to remove from
                    if isinstance(data, bpy.types.Scene):
                        bpy.data.scenes.remove(data)
                    elif isinstance(data, bpy.types.Object):
                        bpy.data.objects.remove(data)
                    elif isinstance(data, bpy.types.Collection):
                        bpy.data.collections.remove(data)
                    elif isinstance(data, bpy.types.Material):
                        bpy.data.materials.remove(data)
                    elif isinstance(data, bpy.types.Mesh):
                        bpy.data.meshes.remove(data)
                    elif isinstance(data, bpy.types.Camera):
                        bpy.data.cameras.remove(data)
                    elif isinstance(data, bpy.types.Light):
                        bpy.data.lights.remove(data)
                    elif isinstance(data, bpy.types.World):
                        bpy.data.worlds.remove(data)
                    # Add other datablock types as needed
                    print(f"DataManager: Successfully removed {data_name}")
                except (ReferenceError, RuntimeError) as e:
                    print(f"DataManager: Error removing {data_name}: {e}")
                    pass
            else:
                print(f"DataManager: Not cleaning up data {data} with ID {data_id} (users: {getattr(data, 'users', 'N/A')})")

        self._data_store.clear()
        self._ref_counts.clear()
        self._owned_copies.clear()
        print("DataManager: Cleanup finished.")
