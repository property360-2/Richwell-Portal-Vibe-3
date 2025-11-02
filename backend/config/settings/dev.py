"""Development settings for the Richwell Portal project."""
from .base import *  # noqa: F403,F401

DEBUG = True

if not ALLOWED_HOSTS:  # noqa: F405
    ALLOWED_HOSTS = ["*"]  # noqa: F405
