from .celery import app as celery_app

# Guarantees that @shared_task will use our app
__all__ = ("celery_app",)
