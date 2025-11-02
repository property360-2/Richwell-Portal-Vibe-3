"""Production settings for the Richwell Portal project."""
from .base import *  # noqa: F403,F401

DEBUG = False
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
