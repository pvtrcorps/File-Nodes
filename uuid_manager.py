import bpy
import uuid

# Custom property name to store the UUID
UUID_PROP_NAME = "_fn_uuid"

def get_uuid(datablock):
    """Returns the File Nodes UUID of a datablock, or None if it doesn't have one."""
    if datablock and hasattr(datablock, "get"):
        return datablock.get(UUID_PROP_NAME)
    return None

def get_or_create_uuid(datablock):
    """Returns the File Nodes UUID of a datablock. Creates one if it doesn't exist."""
    if not datablock or not hasattr(datablock, "get") or not hasattr(datablock, "__setitem__"):
        return None
    
    current_uuid = datablock.get(UUID_PROP_NAME)
    if current_uuid is None:
        new_uuid = str(uuid.uuid4())
        datablock[UUID_PROP_NAME] = new_uuid
        return new_uuid
    return current_uuid

def find_datablock_by_uuid(target_uuid, data_collection):
    """Searches a bpy.data collection for a datablock with the given UUID."""
    if not target_uuid or not data_collection:
        return None
    
    for db in data_collection:
        if get_uuid(db) == target_uuid:
            return db
    return None
