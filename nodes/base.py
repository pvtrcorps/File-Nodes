"""Base mixins and helpers used by node implementations."""

import bpy


class FNCacheIDMixin:
    """Mixin to cache a created datablock ID based on a key."""

    _cached_key = None
    _cached_id = None

    def cache_get(self, key):
        if key == getattr(self, "_cached_key", None):
            return getattr(self, "_cached_id", None)
        return None

    def cache_store(self, key, data):
        self._cached_key = key
        self._cached_id = data

    def _invalidate_cache(self):
        self._cached_key = None
        self._cached_id = None

class FNBaseNode:
    '''Mixin to add a .process(context, inputs) stub'''
    bl_width_default = 160
    def process(self, context, inputs):
        return {}


class DynamicSocketMixin:
    """Mixin providing dynamic input socket management."""

    item_count: bpy.props.IntProperty(default=2)

    def update(self):
        self._ensure_virtual()

    def add_socket(self, idx):
        """Create a new input socket and return it. Subclasses must override."""
        raise NotImplementedError

    def socket_name(self, idx):
        """Return the display name for socket ``idx``."""
        raise NotImplementedError

    def insert_link(self, link):
        if self.inputs and link.to_socket == self.inputs[-1] and link.to_socket.bl_idname == 'NodeSocketVirtual':
            new_sock = self.add_socket(self.item_count + 1)
            self.inputs.move(self.inputs.find(new_sock.name), len(self.inputs) - 2)
            self.item_count += 1
            tree = self.id_data
            tree.links.new(link.from_socket, new_sock)
            if any(l is link for l in tree.links):
                tree.links.remove(link)
            self._ensure_virtual()
            return None
        return None

    def _ensure_virtual(self):
        real_inputs = [s for s in self.inputs if s.bl_idname != 'NodeSocketVirtual']
        while len(real_inputs) > 2 and not (real_inputs[-1].is_linked or getattr(real_inputs[-1], 'value', None)):
            self.inputs.remove(real_inputs[-1])
            real_inputs.pop()
            self.item_count -= 1

        if not self.inputs or self.inputs[-1].bl_idname != 'NodeSocketVirtual':
            self.inputs.new('NodeSocketVirtual', "")

        for idx, sock in enumerate(real_inputs, 1):
            sock.name = self.socket_name(idx)

        self.item_count = len(real_inputs)
