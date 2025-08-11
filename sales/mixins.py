from django.core.exceptions import PermissionDenied

class AdOwnerRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        ad = self.get_object()
        if ad.user != request.user:
            raise PermissionDenied("You do not have permission to modify this ad.")
        return super().dispatch(request, *args, **kwargs)
