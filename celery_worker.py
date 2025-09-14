# celery_worker.py
from app.emails.tasks import c_app

if __name__ == "__main__":
    c_app.start()
