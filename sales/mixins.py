from django.contrib.auth.mixins import UserPassesTestMixin

class AdOwnerRequiredMixin(UserPassesTestMixin):
    """Allow access only if the current user is the owner of the Ad."""

    def test_func(self):
        ad = self.get_object()
        return self.request.user == ad.user
