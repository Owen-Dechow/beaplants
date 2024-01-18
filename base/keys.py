import hashlib
from django.core.management.utils import get_random_secret_key
from django.utils import timezone


def get_hour_key(base_key):
    now = timezone.now()
    timed_key = f"{base_key}{now.year}{now.month}{now.day}{now.hour}"
    shaw = hashlib.sha512(timed_key.encode("utf-8")).hexdigest()
    return f"{shaw[0:4]}-{shaw[4:8]}-{shaw[8:12]}"


def create_secret_key(length):
    s = str(get_random_secret_key())[:length]
    return s
