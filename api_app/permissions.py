from rest_framework.permissions import BasePermission


class IsStaffOrIsSuperUser(BasePermission):
    message = "Only Admin or Superadmin users are allowed."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_staff or user.is_superuser)
        )


class IsSuperUser(BasePermission):
    message = "Only Superadmin users are allowed."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.is_superuser
        )