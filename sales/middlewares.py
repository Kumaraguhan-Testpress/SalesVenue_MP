from backports.zoneinfo import ZoneInfo
from django.utils import timezone

class BrowserTimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = request.COOKIES.get("timezone")
        if tzname:
            try:
                timezone.activate(ZoneInfo(tzname))
            except Exception:
                timezone.deactivate()
        else:
            timezone.deactivate()
        return self.get_response(request)
