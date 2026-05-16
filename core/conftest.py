import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-only")
os.environ.setdefault("DEBUG", "True")
os.environ.setdefault("SITE_URL", "http://testserver")

import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def django_test_settings(settings):
    settings.ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True
