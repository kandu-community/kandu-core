from rest_framework import permissions

from forms.utils import get_form_models

class IsOwnerOrStaff(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """

    def has_object_permission(self, request, view, obj):
    	if request.user.is_staff:
    		return True
    	else:
	        return obj.user == request.user

class HasPermission(permissions.BasePermission):
    def has_permission(self, request, view):
    	return view.model in [model for name, model in get_form_models(for_user=request.user)]

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)