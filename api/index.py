"""Vercel entry point for the Django API."""

import os
import sys
from pathlib import Path
from urllib.parse import parse_qsl, urlencode

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "BE"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "helloHR.settings")

from django.core.wsgi import get_wsgi_application

django_app = get_wsgi_application()


def app(environ, start_response):
    """Restore Django's URL after Vercel routes the request to /api."""
    query = parse_qsl(environ.get("QUERY_STRING", ""), keep_blank_values=True)
    path = next((value for key, value in query if key == "__django_path"), None)
    if path is not None:
        environ["PATH_INFO"] = "/api/" + path
        environ["QUERY_STRING"] = urlencode(
            [(key, value) for key, value in query if key != "__django_path"]
        )
    return django_app(environ, start_response)
