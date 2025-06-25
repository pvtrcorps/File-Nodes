
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
