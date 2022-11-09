
# Create your views here.
import os
from django.template.response import TemplateResponse


def home(request):
    client_url = os.environ.get("CLIENT_URL", "")
    dashboard_url = os.environ.get("DASHBOARD_URL", "")
    return TemplateResponse(
        request,
        "home/home.html",
        {"client_url": client_url, "dashboard_url": dashboard_url},
    )



