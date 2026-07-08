from rest_framework.throttling import ScopedRateThrottle

class APIKeyScopedRateThrottle(ScopedRateThrottle):
    """
    ScopedRateThrottle that keys the cache by:
      - X-API-Key header (if present),
      - otherwise authenticated user's id,
      - otherwise fallback to IP.
    This makes rate-limits per API key / user instead of per-IP.
    """
    def get_cache_key(self, request, view):
        api_key = request.headers.get("X-API-Key")
        if api_key:
            ident = api_key
        elif getattr(request, "user", None) and request.user.is_authenticated:
            ident = str(request.user.pk)
        else:
            ident = self.get_ident(request)

        return self.cache_format % {"scope": self.scope, "ident": ident}
