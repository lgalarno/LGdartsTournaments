from zoneinfo import ZoneInfo
from django.utils import timezone


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # make sure they are authenticated so we know we have their tz info.
        if request.user.is_authenticated:
            # we are getting the users timezone that in this case is stored in
            # a user's profile
            tz_str = request.user.time_zone
            timezone.activate(ZoneInfo(tz_str))
        # otherwise deactivate and the default time zone will be used anyway
        else:
            timezone.deactivate()

        response = self.get_response(request)
        return response
