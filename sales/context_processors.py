from .forms import TimezoneForm
from django.utils.timezone import now

def timezone_form(request):
    context = {}
    if request.user.is_authenticated:
        context["timezone_form"] = TimezoneForm(instance=request.user)
    # always add the current time
    context["now"] = now()
    return context
