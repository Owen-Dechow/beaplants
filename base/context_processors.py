from django.conf import settings

def site_style(request):
    return {"site_style": settings.WEBSITE_STYLE}
