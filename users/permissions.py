from rest_framework.permissions import BasePermission

class RoleAllowed(BasePermission):
    allowed_roles = []

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not self.allowed_roles:
            return True
        return request.user.role in self.allowed_roles


def make_role_permission(*roles):
    class _P(RoleAllowed):
        allowed_roles = list(roles)
    return _P
