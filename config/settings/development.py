"""
Development settings — debug on, relaxed CORS, verbose errors.
"""

from .base import *  # noqa: F401, F403

DEBUG = True

# Allow all origins in dev (tighten this in production)
CORS_ALLOW_ALL_ORIGINS = True

# Show full error detail in API responses during development
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",  # interactive HTML renderer
]
