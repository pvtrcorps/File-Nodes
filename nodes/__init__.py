
import bpy, importlib
# Node modules used by the File Nodes addon. `input_nodes` now contains
# FNWorldInputNode for providing World datablocks.
from . import (
    read_blend, create_list, get_item_by_name, get_item_by_index,
    link_to_scene, link_to_collection, set_world, group_input, group_output,
    input_nodes, import_alembic, output_nodes,
    join_strings, split_string,
    set_render_engine, cycles_scene_props, eevee_scene_props,
    workbench_scene_props, output_props, scene_props, object_props,
    cycles_object_props, eevee_object_props, collection_props,
    world_props, camera_props, light_props, mesh_props, material_props,
    new_scene, new_object, new_collection, new_world, new_material,
    set_scene_name, set_collection_name, set_object_name,
    switch, index_switch
)

_modules = [
    read_blend, create_list, get_item_by_name, get_item_by_index,
    link_to_scene, link_to_collection, set_world, group_input, group_output,
    input_nodes, import_alembic, output_nodes,
    join_strings, split_string,
    set_render_engine, cycles_scene_props, eevee_scene_props,
    workbench_scene_props, output_props, scene_props, object_props,
    cycles_object_props, eevee_object_props, collection_props,
    world_props, camera_props, light_props, mesh_props, material_props,
    new_scene, new_object, new_collection, new_world, new_material,
    set_scene_name, set_collection_name, set_object_name,
    switch, index_switch
]

def register():
    for m in _modules:
        importlib.reload(m)
        if hasattr(m, 'register'):
            m.register()

def unregister():
    for m in reversed(_modules):
        if hasattr(m, 'unregister'):
            m.unregister()
